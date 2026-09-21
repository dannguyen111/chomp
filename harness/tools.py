"""Tools available to the explorer.

bash alone would do, but heredoc escaping mangles LaTeX and long proofs badly
enough to waste real money, so write_file/read_file are separate.

Sandboxing here is a guardrail against an agent that wanders, not a security
boundary. If you care about the latter, run the whole session in a container
with no credentials mounted -- which you should, since GROUND_TRUTH is the
only thing standing between you and believing a false lemma.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

MAX_OUTPUT = 30_000  # chars; a runaway print loop must not eat the context

SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": (
                "Run a bash command in the project root. Use for compiling and "
                "running the solver, analysis scripts, and inspecting output. "
                "Long-running commands are fine up to the timeout."
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
_ESCAPE = re.compile(
    r"""(^|[\s'"=(])(\.\.[\\/]|[\\/](?![\\/])|~[\\/]|[A-Za-z]:[\\/])""")


def _escapes(command: str) -> str | None:
    m = _ESCAPE.search(command)
    return m.group(0).strip() if m else None


def dispatch(name: str, args: dict, root: Path, *, sandbox: bool = False) -> str:
    try:
        if name == "bash":
            if sandbox:
                bad = _escapes(args["command"])
                if bad:
                    return (f"REFUSED: {bad!r} reaches outside the working "
                            f"directory. Everything you need is in it; list it "
                            f"with `ls`. This refusal is recorded.")
            timeout = min(int(args.get("timeout", 600)), 3600)
            r = subprocess.run(
                args["command"],
                shell=True,
                cwd=root,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            out = r.stdout + (f"\n[stderr]\n{r.stderr}" if r.stderr else "")
            if r.returncode:
                out += f"\n[exit {r.returncode}]"
            return _clip(out) or "(no output)"

        if name == "write_file":
            p = _resolve(root, args["path"])
            if _protected(root, p):
                return f"REFUSED: {args['path']} is read-only (see MISSION.md s6)."
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(args["content"])
            return f"wrote {args['path']} ({len(args['content'])} chars)"

        if name == "read_file":
            p = _resolve(root, args["path"])
            if not p.exists():
                return f"no such file: {args['path']}"
            lines = p.read_text().splitlines()
            s, e = args.get("start"), args.get("end")
            if s or e:
                lines = lines[(s or 1) - 1 : e or len(lines)]
            return _clip("\n".join(lines)) or "(empty)"

        return f"unknown tool: {name}"

    except subprocess.TimeoutExpired:
        return "TIMEOUT. Re-run in the background writing to a file, then poll it."
    except Exception as e:  # never kill a paid session on a tool error
        return f"TOOL ERROR: {type(e).__name__}: {e}"
