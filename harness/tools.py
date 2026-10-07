"""Tools available to the explorer.

bash alone would do, but heredoc escaping mangles LaTeX and long proofs badly
enough to waste real money, so write_file/read_file are separate.

Sandboxing here is a guardrail against an agent that wanders, not a security
boundary. If you care about the latter, run the whole session in a container
with no credentials mounted -- which you should, since GROUND_TRUTH is the
only thing standing between you and believing a false lemma.
"""
from __future__ import annotations

import os
import re
import signal
import subprocess
from pathlib import Path

MAX_OUTPUT = 30_000  # chars; a runaway print loop must not eat the context

# Address-space cap on every sandboxed command, in GiB. The runner has 16 GB
# and nothing else on it matters, but if a referee's census or table eats all
# of it the kernel kills the runner itself, and the job dies with no log and
# no verdict. That is the likeliest reading of referee run 21, which died two
# and a half hours into a claim with its step still running and no log. Under
# the cap the script gets a MemoryError or bad_alloc it can read and
# work around.
SANDBOX_MEM_GB = float(os.environ.get("CHOMP_SANDBOX_MEM_GB", "8"))

# Process groups started by sandboxed commands. A command the model puts in
# the background outlives the call that started it, and subprocess's own
# timeout kills only the shell, not what the shell started. reap() kills them.
_GROUPS: set[int] = set()


def _sandbox_limits() -> None:      # runs in the child, before exec
    import resource
    cap = int(SANDBOX_MEM_GB * 2**30)
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))


def _killpg(pgid: int) -> None:
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def reap() -> None:
    """Kill everything a sandboxed command left running."""
    while _GROUPS:
        _killpg(_GROUPS.pop())

SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": (
                "Run a bash command in the project root. Use for compiling and "
                "running the solver, analysis scripts, and inspecting output. "
                "Long-running commands are fine up to the timeout. In the "
                "referee sandbox each command is capped at "
                f"{SANDBOX_MEM_GB:g} GB of address space: a MemoryError or "
                "bad_alloc means use less memory, not retry."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "timeout": {
                        "type": "integer",
                        "description": "seconds, default 600, max 3600",
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": (
                "Write a file, creating parent directories. Overwrites. Use this "
                "rather than bash heredocs for proofs, notes and code -- heredoc "
                "escaping corrupts LaTeX and backslashes."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file. Optional line range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "start": {"type": "integer"},
                    "end": {"type": "integer"},
                },
                "required": ["path"],
            },
        },
    },
]

# Paths the explorer may never write to. GROUND_TRUTH is read-only by mission
# rule; if the solver is wrong the explorer files a claim, it does not patch.
PROTECTED = ("GROUND_TRUTH", "MISSION.md", "prompts", "harness", "BUDGET.json")


def _resolve(root: Path, rel: str) -> Path:
    p = (root / rel).resolve()
    if not str(p).startswith(str(root.resolve())):
        raise PermissionError(f"path escapes project root: {rel}")
    return p


def _protected(root: Path, p: Path) -> bool:
    try:
        rel = p.resolve().relative_to(root.resolve())
    except ValueError:
        return True
    return rel.parts and rel.parts[0] in PROTECTED


def _clip(s: str) -> str:
    if len(s) <= MAX_OUTPUT:
        return s
    half = MAX_OUTPUT // 2
    return (
        s[:half]
        + f"\n\n... [{len(s) - MAX_OUTPUT} chars elided; redirect to a file "
        f"and inspect it in slices] ...\n\n"
        + s[-half:]
    )


# `bash` runs with shell=True, so `_resolve`'s root check does not constrain it:
# `cat ../../LEDGER/claims.jsonl` walks straight out. That is harmless for an
# explorer working in its own project, and fatal for a referee, whose whole
# value is not knowing what answer is expected. In sandbox mode the tools run
# against an isolated box (see harness/make_refbox.py) and any command that
# reaches for a parent directory, an absolute path or a home directory is
# refused -- inside a four-file box there is no legitimate reason to.
#
# The first version of this screen refused any "/" preceded by whitespace. That
# also refuses `a / b`, so every Python script the referee wrote was rejected,
# it burned its turns on refusals, and produced no verdict at all. Match paths,
# not punctuation: a parent-directory hop, a home-directory reference, or a
# rooted path that is not inside the box.
_ESCAPE = re.compile(
    r"""(?:(?<=^)|(?<=[\s'"=(<>|;&]))"""          # at a token boundary
    r"""(\.\.[\\/]|~[\\/]|/[A-Za-z]|[A-Za-z]:[\\/])""")

# Network egress. The referee's novelty pass wants it, but this repo is public
# and named for the problem: a search for the claim can land on the project
# itself, which hands over every piece of provenance the box removes. Novelty
# is checked by the operator instead.
_NET = re.compile(r"\b(curl|wget|nc|ncat|ssh|scp|ftp|telnet|pip|npm|git)\b")

# A bare "/" cannot be told from division without breaking arithmetic again, so
# sweeps rooted at "/" are matched by the command instead. This is the one the
# first run actually attempted: `ls -la / && find / -maxdepth 3 -iname '*chomp*'`.
_SWEEP = re.compile(r"\b(find|fd|locate|tree|du|ls)\b[^|;&]*?\s/(?:\s|$)")


def _escapes(command: str, root: Path) -> str | None:
    """Why this command may not run in a sandbox, or None if it may."""
    m = _NET.search(command)
    if m:
        return (f"{m.group(1)!r} reaches the network. Everything needed to "
                f"judge the submission is in the working directory; novelty is "
                f"not your call to make here.")
    m = _SWEEP.search(command)
    if m:
        return (f"{m.group(1)!r} rooted at '/' sweeps the filesystem. "
                f"Everything you need is in the working directory.")
    for m in _ESCAPE.finditer(command):
        tok = m.group(1)
        start = m.start(1)
        rest = command[start:]
        # `2>/dev/null` is in almost every shell command ever written, and it
        # reads nothing. Blocking it starved the referee of every command it
        # tried to run. The /dev sinks are allowed; /dev/... anything else, and
        # every other rooted path, is not.
        if re.match(r"/dev/(null|zero|stdout|stderr|stdin)\b", rest):
            continue
        # Scratch space. The referee reaches for /tmp by habit when it wants to
        # write a verification script, and refusing that cost run 7 its verdict:
        # it was blocked once (`mkdir -p /tmp/gtest && cat > /tmp/gtest/grundy.py`),
        # never retried inside the box, and rejected a correct claim on reasoning
        # it had not run. /tmp on a fresh runner holds nothing about this project.
        # The controls that actually protect provenance are the network block,
        # the sweep block, and the refusal of rooted paths into the real
        # checkout -- all of which still stand. A referee that can run its own
        # counterexample search is the entire point of the sandbox having a
        # shell at all.
        if re.match(r"/tmp\b", rest):
            continue
        # An absolute path INTO the box is fine -- the referee often cds to it.
        if (rest.startswith(str(root))
                or rest.startswith(str(root).replace("\\", "/"))):
            continue
        return (f"{tok!r} reaches outside the working directory. Everything you "
                f"need to judge the submission is in it; list it with `ls`. "
                f"Write scratch files in the working directory or under /tmp -- "
                f"both are writable. A verification script you actually ran is "
                f"worth more than an argument you did not check.")
    return None


def _tool_env() -> dict:
    """The environment a model's shell commands run in: ours, minus the API key.

    Session 28 found OPENROUTER_API_KEY in its shell and ran
    `python -m harness.referee` on its own claims five times -- ~140 of its
    300 minutes, outside the referee's schedule and spend cap -- then patched
    the proof against the verdict and reran. A model that can call a model can
    grade its own work; one agreed accept would have promoted a claim nobody
    independent had read. Nothing a tool call legitimately does needs the key.
    """
    env = {k: v for k, v in os.environ.items() if "OPENROUTER" not in k.upper()}
    # Child Pythons print UTF-8, which is what dispatch() decodes. On Windows
    # they would otherwise print in the console code page.
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


def dispatch(name: str, args: dict, root: Path, *, sandbox: bool = False) -> str:
    try:
        if name == "bash":
            if sandbox:
                bad = _escapes(args["command"], root)
                if bad:
                    return f"REFUSED: {bad} This refusal is recorded."
            timeout = min(int(args.get("timeout", 600)), 3600)
            posix = os.name == "posix"
            p = subprocess.Popen(
                args["command"],
                shell=True,
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                # A model's script printing one stray byte must not turn a
                # paid tool call into a UnicodeDecodeError.
                encoding="utf-8",
                errors="replace",
                env=_tool_env(),
                # Its own process group, so a timeout or reap() can kill the
                # whole tree and not just the shell.
                start_new_session=posix,
                preexec_fn=_sandbox_limits if (sandbox and posix) else None,
            )
            if sandbox and posix:
                _GROUPS.add(p.pid)
            try:
                stdout, stderr = p.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                if posix:
                    _killpg(p.pid)
                else:
                    p.kill()
                p.communicate()
                raise
            out = stdout + (f"\n[stderr]\n{stderr}" if stderr else "")
            if p.returncode:
                out += f"\n[exit {p.returncode}]"
            return _clip(out) or "(no output)"

        if name == "write_file":
            p = _resolve(root, args["path"])
            if _protected(root, p):
                return f"REFUSED: {args['path']} is read-only (see MISSION.md s6)."
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(args["content"], encoding="utf-8")
            return f"wrote {args['path']} ({len(args['content'])} chars)"

        if name == "read_file":
            p = _resolve(root, args["path"])
            if not p.exists():
                return f"no such file: {args['path']}"
            lines = p.read_text(encoding="utf-8").splitlines()
            s, e = args.get("start"), args.get("end")
            if s or e:
                lines = lines[(s or 1) - 1 : e or len(lines)]
            return _clip("\n".join(lines)) or "(empty)"

        return f"unknown tool: {name}"

    except subprocess.TimeoutExpired:
        return "TIMEOUT. Re-run in the background writing to a file, then poll it."
    except Exception as e:  # never kill a paid session on a tool error
        return f"TOOL ERROR: {type(e).__name__}: {e}"
