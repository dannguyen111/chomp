"""Facts for the daily digest. Read-only; prints a plain-text report.

The scheduled cloud agent runs this and emails the output. Everything here is
computed from the repository, so the agent does not have to infer anything --
which matters, because the one thing this project has repeatedly caught its own
models doing is asserting things they did not check.

    python3 ops/digest.py [--since '25 hours ago']
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone


def sh(*args: str) -> str:
    try:
        return subprocess.run(args, capture_output=True, text=True,
                              encoding="utf-8", errors="replace",
                              check=False).stdout.strip()
    except OSError as e:
        return f"(failed: {e})"


def resolve(blob: str) -> dict[str, dict]:
    """Last entry per id wins. Unparseable lines are skipped, as in ledger.py."""
    out: dict[str, dict] = {}
    for line in blob.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            c = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(c, dict) and "id" in c:
            out[c["id"]] = c
    return out


def money(x: float) -> str:
    return f"${x:,.4f}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="25 hours ago")
    a = ap.parse_args(argv)

    old = sh("git", "rev-list", "-1", f"--before={a.since}", "HEAD")
    L: list[str] = []
    add = L.append

    add(f"CHOMP DAILY  {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC")
    add("=" * 60)

    # --- autopilot -------------------------------------------------------
    import os
    on = os.path.exists("runs/AUTOPILOT")
    add(f"Autopilot:  {'ON' if on else 'OFF -- the loop is stopped'}")

    # --- budget ----------------------------------------------------------
    try:
        cur = json.load(open("BUDGET.json", encoding="utf-8"))
        spent, cap = float(cur["spent"]), float(cur["cap"])
        line = f"Budget:     {money(spent)} of {money(cap)}"
        if old:
            try:
                prev = json.loads(sh("git", "show", f"{old}:BUDGET.json"))
                d = spent - float(prev["spent"])
                line += f"   (+{money(d)} since {a.since})"
                if d > 0:
                    line += (f"\n            {(cap - spent) / d:.1f} windows left "
                             f"at that rate -- one window, so treat it as a "
                             f"rough signal, not a forecast")
                else:
                    line += "\n            nothing spent -- did the crons run?"
            except (json.JSONDecodeError, KeyError, ValueError, ZeroDivisionError):
                pass
        add(line)
    except (OSError, json.JSONDecodeError, KeyError) as e:
        add(f"Budget:     UNREADABLE ({e})")

    # --- commits ---------------------------------------------------------
    add("")
    if not old:
        add("Commits:    (no commit older than the window; repo may be new)")
        log = sh("git", "log", "--oneline", "-10")
    else:
        log = sh("git", "log", "--oneline", f"{old}..HEAD")
        add(f"Commits since {old[:8]}:")
    add("  " + ("\n  ".join(log.splitlines()) if log else "(none -- nothing ran)"))

    # --- claims ----------------------------------------------------------
    add("")
    try:
        now = resolve(open("LEDGER/claims.jsonl", encoding="utf-8").read())
        was = resolve(sh("git", "show", f"{old}:LEDGER/claims.jsonl")) if old else {}
        new = [k for k in now if k not in was]
        moved = [(k, was[k].get("status"), now[k].get("status"))
                 for k in now if k in was
                 and was[k].get("status") != now[k].get("status")]
        add(f"Ledger:     {len(now)} claims"
            f"  ({sum(1 for c in now.values() if c.get('status') == 'proven')} proven,"
            f" {sum(1 for c in now.values() if c.get('status') == 'open')} open)")
        if new:
            add("  NEW:")
            for k in sorted(new):
                add(f"    {k}  [{now[k].get('status')}] "
                    f"{str(now[k].get('statement'))[:90]}")
        if moved:
            add("  STATUS CHANGED:")
            for k, b, c in sorted(moved):
                add(f"    {k}  {b} -> {c}")
        if not new and not moved:
            add("  no new claims, no status changes")
        unchecked = [k for k, c in now.items()
                     if not c.get("novelty_checked")
                     and c.get("status") not in ("superseded",)]
        add(f"  novelty unchecked: {len(unchecked)}")
    except (OSError, json.JSONDecodeError) as e:
        add(f"Ledger:     UNREADABLE ({e})")

    # --- referee ---------------------------------------------------------
    add("")
    if old:
        ch = sh("git", "diff", "--name-only", old, "HEAD", "--", "LEDGER/referee")
        add("Referee files changed:")
        add("  " + ("\n  ".join(ch.splitlines()) if ch else "(none)"))
    for p, label in (("LEDGER/referee", "verdicts"),):
        try:
            import glob
            for f in sorted(glob.glob(p + "/*.json")):
                d = json.load(open(f, encoding="utf-8"))
                add(f"  {f.replace(chr(92), '/')}: final={d.get('final')} "
                    f"agreed={d.get('agreed')} spend={d.get('spend')}")
        except (OSError, json.JSONDecodeError):
            pass

    # --- what needs a human ----------------------------------------------
    add("")
    add("NEEDS YOU")
    flags: list[str] = []
    if not on:
        flags.append("autopilot is OFF -- nothing will run until runs/AUTOPILOT returns")
    try:
        if spent >= cap - 2.0:
            flags.append(f"budget nearly gone ({money(cap - spent)} left)")
    except NameError:
        pass
    try:
        for k, b, c in moved:
            if c == "proven":
                flags.append(f"{k} was PROMOTED to proven -- check the verdict")
            if c == "refuted":
                flags.append(f"{k} was REFUTED -- check it was a real rejection")
    except NameError:
        pass
    if not log:
        flags.append("no commits in 24h -- the crons may be failing; check Actions")
    add("  " + ("\n  ".join(flags) if flags else "nothing"))

    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
