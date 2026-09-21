"""Build an isolated sandbox for refereeing one claim.

    python -m harness.make_refbox C0012 --out /tmp/refbox

The wired referee in `harness/referee.py` strips provenance from its *prompt*
-- MISSION sections 5, 7, 8 and 9 are withheld -- but it is handed `bash` and
`read_file` scoped to the project root, and `tools.PROTECTED` gates only
*writes*. So it can `cat islands/01-recurrence/HANDOFF.md` and read "the target
is achieved in this session", or `cat LEDGER/claims.jsonl` and see the claim's
own history and the explorer's confidence. The redaction is real in the prompt
and undone by one command.

This builds a directory containing exactly three things:

    REFEREE_PROMPT.md   the verbatim build_messages output for the claim
    solver / solver.exe the validated oracle, so counterexample hunting is real
    SOLVER.md           how to invoke it

and nothing else. A referee pointed at it cannot discover where the claim came
from, what anyone expects the answer to be, or how much budget is riding on it.
Used for the Opus pre-screens; see OPERATOR_NOTES.md.
"""
from __future__ import annotations

import argparse
import platform
import re
import shutil
import sys
from dataclasses import replace
from pathlib import Path

from .ledger import Ledger
from .referee import build_messages, refereeable

SOLVER_MD = """# The solver -- an independently validated oracle for f(q,r)

Use it to hunt counterexamples. It implements the recurrence in the submission
and nothing else.

    {exe} table  --rmax 24 --qmax 24     # grid, rows q=0.., cols r=0..
    {exe} row    --r 120 --qmax 400      # one column: `q  f(q,r)  f(q,r)-q`
    {exe} column --r 6541                # period / preperiod descriptor
    {exe} census --rmax 20000            # one descriptor line per r
    {exe}                                # full usage

In `table` output, line q (0-indexed) column r (0-indexed) is f(q,r); entries
with r > q are printed as f(q,q).

A `census` file ends with a `# complete rmax=... rows=...` trailer. A file
without it is truncated -- do not use it.

Precomputed censuses may be present as *.tsv; they save you recomputing.
"""


def build_solver(root: Path) -> Path:
    """Return a path to a solver binary, compiling one if needed."""
    from . import __name__ as _  # noqa: F401  (keep the package import explicit)
    sys.path.insert(0, str(root))
    from GROUND_TRUTH import chomp                      # type: ignore
    return chomp.build()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="harness.make_refbox")
    ap.add_argument("claim_id")
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", required=True,
                    help="directory to create (wiped if it exists)")
    ap.add_argument("--census", nargs="*", default=[],
                    help="optional precomputed census TSVs to copy in")
    ap.add_argument("--statement", default=None,
                    help="replace the claim statement with a provenance-free "
                         "restatement. The ledger statement is what reaches the "
                         "referee verbatim, and several of ours narrate project "
                         "history ('corrects C0009', 'the Phase 0 audit'), which "
                         "tells the referee what answer is wanted. Use this to "
                         "hand it the mathematics alone, and say in the verdict "
                         "record that you did.")
    a = ap.parse_args(argv)

    root = Path(a.root).resolve()
    out = Path(a.out).resolve()
    led = Ledger(root / "LEDGER")
    claim = led.resolved().get(a.claim_id)
    if claim is None:
        print(f"no such claim {a.claim_id}", file=sys.stderr)
        return 1
    ok, why = refereeable(root, claim)
    if not ok:
        print(f"{a.claim_id} is not refereeable: {why}", file=sys.stderr)
        return 1

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    if a.statement:
        claim = replace(claim, statement=a.statement)
    m = build_messages(root, claim, (root / why).read_text(), {})
    (out / "REFEREE_PROMPT.md").write_text(
        m[0]["content"] + "\n\n" + "=" * 70 + "\n\n" + m[1]["content"],
        encoding="utf-8")

    exe = build_solver(root)
    dest = out / exe.name
    shutil.copy2(exe, dest)
    invoke = f"./{exe.name}" if platform.system() != "Windows" else exe.name
    (out / "SOLVER.md").write_text(SOLVER_MD.format(exe=invoke), encoding="utf-8")

    for c in a.census:
        p = Path(c)
        if p.exists():
            shutil.copy2(p, out / p.name)

    # Paranoia check on the SUBMISSION only -- the referee's own system prompt
    # and MISSION section 6 legitimately mention islands and the ledger while
    # telling it what it will not be shown.
    body = m[1]["content"]
    body = body[body.index("## SUBMISSION"):] if "## SUBMISSION" in body else body
    low = body.lower()
    leaks = [probe for probe in
             ("handoff", "ledger", "island", "phase 0", "byrnes_audit",
              "seed_check", "session", "explorer", "budget", "conjecture n")
             if probe in low]
    leaks += [f"cross-reference {c}" for c in
              sorted(set(re.findall(r"C\d{4}", body))) if c != claim.id]
    print(f"refbox: {out}")
    for f in sorted(out.iterdir()):
        print(f"  {f.stat().st_size:>10,}  {f.name}")
    if leaks:
        print("\n!! PROVENANCE LEAK IN THE SUBMISSION:", leaks, file=sys.stderr)
        print("   The claim statement reaches the referee verbatim. Narrating\n"
              "   project history in it tells the referee what answer is wanted.\n"
              "   Re-run with --statement '<the mathematics alone>'.",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
