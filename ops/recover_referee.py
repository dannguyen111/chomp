"""Bring a dead referee run's work back onto main.

While a referee job runs, referee.yml pushes a snapshot of BUDGET.json, LEDGER
and runs/referee to the side branch `referee-wip/run-<N>` every few minutes,
and deletes the branch once the job has committed to main normally. A branch
that is still there when the next job starts belongs to a run that died: the
`chomp` concurrency group means no other job is running.

Referee run 21 is the case this is for. It died two and a half hours into its
second claim, and everything it had learned went with the runner: the pass
verdicts, the transcript, and the record of what it had spent.

What is carried over, and how:

- LEDGER/claims.jsonl: lines main does not have are appended (the ledger is
  append-only, so this is the same union git's merge driver does).
- Verdict files under LEDGER/referee/ (final and invalid/): added if missing.
- LEDGER/referee/attempts.json: per-claim maximum.
- LEDGER/referee/progress/: a finished pass is reusable by the next run of
  the same submission. Taken unless main already has that run's verdict for
  the claim, or a progress file with at least as many passes.
- runs/referee/: transcripts and heartbeats, added if missing or longer.
- BUDGET.json / BUDGET.log.jsonl: spend entries main has not recorded are
  appended to the log and added to `spent`, so the cap still counts money the
  dead run spent.

Usage: python -m ops.recover_referee [--dry-run]
Prints what it recovered, and the branches it read, one per line, prefixed
with `branch:`, for the workflow to delete after it has pushed.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PREFIX = "referee-wip/"


def git(*args: str, check: bool = True) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True,
                       encoding="utf-8")
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def show(ref: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True,
                       text=True, encoding="utf-8")
    return r.stdout if r.returncode == 0 else None


def wip_refs() -> list[str]:
    git("fetch", "-q", "origin",
        f"+refs/heads/{PREFIX}*:refs/remotes/origin/{PREFIX}*", check=False)
    out = git("for-each-ref", "--format=%(refname:short)",
              f"refs/remotes/origin/{PREFIX}")
    return [l.strip() for l in out.splitlines() if l.strip()]


def finished_here(root: Path, claim: str, run: str) -> bool:
    """Did main already get this run's verdict on this claim?"""
    ref = root / "LEDGER" / "referee"
    for f in [ref / f"{claim}.json", *(ref / "invalid").glob(f"{claim}.*.json")]:
        try:
            if json.loads(f.read_text(encoding="utf-8")).get("run") == run:
                return True
        except (OSError, json.JSONDecodeError):
            continue
    return False


def recover(root: Path, ref: str, dry: bool) -> list[str]:
    done: list[str] = []
    run = ref.rsplit("/run-", 1)[-1]

    def write(rel: str, text: str) -> None:
        done.append(rel)
        if not dry:
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")

    files = git("ls-tree", "-r", "--name-only", ref, "--",
                "LEDGER/referee", "runs/referee").splitlines()

    # Ledger lines.
    theirs = show(ref, "LEDGER/claims.jsonl") or ""
    led = root / "LEDGER" / "claims.jsonl"
    ours = led.read_text(encoding="utf-8")
    have = set(ours.splitlines())
    new = [l for l in theirs.splitlines() if l.strip() and l not in have]
    if new:
        write("LEDGER/claims.jsonl",
              ours + ("" if ours.endswith("\n") or not ours else "\n")
              + "\n".join(new) + "\n")

    for rel in files:
        text = show(ref, rel)
        if text is None:
            continue
        name = rel.rsplit("/", 1)[-1]
        mine = root / rel
        if rel.startswith("runs/referee/"):
            if not mine.exists() or len(mine.read_text(encoding="utf-8")) < len(text):
                write(rel, text)
        elif rel.startswith("LEDGER/referee/progress/"):
            try:
                prog = json.loads(text)
            except json.JSONDecodeError:
                continue
            claim = prog.get("claim") or name[:-5]
            if (root / "LEDGER" / "referee" / f"{claim}.json").exists():
                continue
            if finished_here(root, claim, str(prog.get("run"))):
                continue
            if mine.exists():
                try:
                    cur = json.loads(mine.read_text(encoding="utf-8"))
                    if len(cur.get("verdicts", [])) >= len(prog.get("verdicts", [])):
                        continue
                except json.JSONDecodeError:
                    pass
            write(rel, text)
        elif name == "attempts.json":
            try:
                a = json.loads(text)
                b = json.loads(mine.read_text(encoding="utf-8")) if mine.exists() else {}
            except json.JSONDecodeError:
                continue
            merged = {k: max(a.get(k, 0), b.get(k, 0)) for k in {*a, *b}}
            if merged != b:
                write(rel, json.dumps(merged, indent=2, sort_keys=True) + "\n")
        elif name == "hold.json":
            continue                      # the operator's, never a run's
        elif rel.endswith(".json") and not mine.exists():
            write(rel, text)              # a verdict main never received

    # Spend. The per-call log is BUDGET.log.jsonl; a snapshot taken before
    # 2026-10-09 still carries it inline as BUDGET.json's `log`.
    theirs = show(ref, "BUDGET.json")
    if theirs:
        b_path = root / "BUDGET.json"
        l_path = root / "BUDGET.log.jsonl"
        mine_b = json.loads(b_path.read_text(encoding="utf-8"))
        their_b = json.loads(theirs)
        mine_log = mine_b.get("log", []) + _jsonl(
            l_path.read_text(encoding="utf-8") if l_path.exists() else "")
        their_log = their_b.get("log", []) + _jsonl(
            show(ref, "BUDGET.log.jsonl") or "")
        seen = {(e.get("t"), e.get("tag")) for e in mine_log}
        extra = sorted((e for e in their_log
                        if (e.get("t"), e.get("tag")) not in seen),
                       key=lambda e: e.get("t", 0))
        if extra:
            mine_b.pop("log", None)
            mine_b["spent"] = round(mine_b["spent"]
                                    + sum(e.get("cost", 0) for e in extra), 6)
            mine_b["calls"] = mine_b.get("calls", 0) + len(extra)
            print(f"  {ref}: {len(extra)} unrecorded calls, "
                  f"${sum(e.get('cost', 0) for e in extra):.4f}")
            done += ["BUDGET.json", "BUDGET.log.jsonl"]
            if not dry:
                old = [] if l_path.exists() else mine_log
                with l_path.open("a", encoding="utf-8") as f:
                    for e in old + extra:
                        f.write(json.dumps(e) + "\n")
                b_path.write_text(json.dumps(mine_b, indent=2), encoding="utf-8")
    return done


def _jsonl(text: str) -> list[dict]:
    out = []
    for line in text.splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="ops.recover_referee")
    ap.add_argument("--root", default=".")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    refs = wip_refs()
    if not refs:
        print("no dead referee runs to recover")
        return 0
    for ref in refs:
        got = recover(root, ref, a.dry_run)
        print(f"{ref}: recovered {len(got)} file(s)")
        for rel in got:
            print(f"  {rel}")
        print(f"branch: {ref.removeprefix('origin/')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
