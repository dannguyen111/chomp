"""Referee gate.

Two rules carry all the weight:

1. Provenance is stripped. The referee sees the claim and the proof and nothing
   about where they came from -- not the island, not the session log, not the
   seed conjecture in MISSION.md s5, not the explorer's stated confidence. A
   referee who knows the expected answer will find reasons to accept it.

2. It runs twice, at different temperatures, and both must agree. One
   sycophantic pass is the single most likely way a false lemma gets promoted
   to `proven`, and at roughly $0.30 a run the second opinion is cheap.
"""
from __future__ import annotations

import argparse
import json
import re
import tempfile
from dataclasses import replace
from pathlib import Path

from . import tools
from .ledger import Ledger
from .orclient import REFEREE_MODEL, Budget, OpenRouter

# Mission sections the referee may see. Section 5 (the sqrt(2) seed conjecture),
# 7, 8 and 9 are withheld: they telegraph the expected answer and the budget.
ALLOWED_SECTIONS = ("## 1.", "## 2.", "## 3.", "## 4.", "## 6.")


def redacted_mission(root: Path) -> str:
    text = (root / "MISSION.md").read_text()
    blocks = re.split(r"\n(?=## \d+\.)", text)
    keep = [b for b in blocks if b.lstrip().startswith(ALLOWED_SECTIONS)]
    return "\n\n".join(keep)


def build_messages(root: Path, claim, proof: str, deps: dict) -> list[dict]:
    dep_text = (
        "\n".join(f"- [{d.id}] {d.statement}" for d in deps.values())
        or "(none cited)"
    )
    return [
        {"role": "system", "content": (root / "prompts" / "referee.md").read_text()},
        {
            "role": "user",
            "content": (
                f"{redacted_mission(root)}\n\n{'=' * 70}\n\n"
                f"## SUBMISSION\n\n**Claim.** {claim.statement}\n\n"
                f"**Results cited as already established:**\n{dep_text}\n\n"
                f"**Proof.**\n\n{proof}\n\n{'=' * 70}\n\n"
                "Referee this submission. Run all three passes. Emit only the JSON."
            ),
        },
    ]


def _parse(text: str) -> dict | None:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def _restatement(root: Path, claim_id: str) -> str | None:
    """A provenance-free restatement of the claim, if one is on file.

    See LEDGER/restatements.json. The substitution is recorded in the verdict
    so it can be audited against the ledger statement afterwards.
    """
    p = root / "LEDGER" / "restatements.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text()).get(claim_id)
    except json.JSONDecodeError:
        print(f"[referee] restatements.json is not valid JSON; ignoring it")
        return None


class NotRefereeable(Exception):
    """The claim cannot be judged yet. Not an error -- a skip."""


def refereeable(root: Path, claim) -> tuple[bool, str]:
    """Can this claim be put in front of the referee right now?

    A claim is judged on a PROOF. Several claims carry a `proof_ref` that points
    at supporting evidence instead -- a census write-up, a literature audit, the
    test runner. Handing those to the referee would ask it whether a document
    that never claimed to be a proof is a valid proof; it would say no, and the
    claim would be marked `refuted` and hidden from every future explorer. So
    the bar is: a `lemma`, or a file written deliberately as a proof (under a
    `proofs/` directory). Observations are validated by the solver and their
    `verified_range`, not by an adversarial reader.
    """
    if not claim.proof_ref:
        return False, "no proof_ref"
    ref = claim.proof_ref.split(" (")[0].strip()      # tolerate "path (NOTE)"
    if claim.type != "lemma" and "/proofs/" not in ref.replace("\\", "/"):
        return False, f"{claim.type} backed by evidence, not a proof: {ref}"
    if not (root / ref).exists():
        return False, f"proof file missing: {ref}"
    if claim.status in ("proven", "refuted", "superseded"):
        return False, f"already {claim.status}"
    if (root / "LEDGER" / "referee" / f"{claim.id}.json").exists():
        return False, "already refereed"
    return True, ref


def referee(root: Path, claim_id: str, session: str = "referee",
            max_spend: float = 1.00) -> dict:
    led = Ledger(root / "LEDGER")
    resolved = led.resolved()
    claim = resolved.get(claim_id)
    if claim is None:
        raise SystemExit(f"no such claim {claim_id}")
    ok, why = refereeable(root, claim)
    if not ok:
        raise NotRefereeable(f"{claim_id}: {why}")

    proof = (root / why).read_text()
    deps = {d: resolved[d] for d in claim.depends_on if d in resolved}

    budget = Budget(root / "BUDGET.json")
    start_spend = budget.spent
    client = OpenRouter(budget)
    verdicts = []

    # The referee works inside an isolated box, NOT the project root. Its tools
    # used to be scoped to the repo, and `bash` runs with shell=True, so one
    # `cat islands/<id>/HANDOFF.md` handed it the expected answer and the
    # explorer's confidence -- which is exactly what this gate is supposed not
    # to know. See harness/make_refbox.py.
    from . import make_refbox
    restated = _restatement(root, claim_id)
    box = Path(tempfile.mkdtemp(prefix=f"refbox-{claim_id}-"))
    # Hand over the precomputed censuses. Run 2 spent most of its 40 turns
    # recomputing a 50000-row census the repo already had, and never reached a
    # verdict. The referee should spend its turns on the proof, not on the
    # solver.
    cached = sorted((root / "GROUND_TRUTH" / "cache").glob("census_*.tsv"))
    box, leaks = make_refbox.build_box(root, claim, box, census=cached,
                                       statement=restated)
    if restated:
        print(f"[referee] using the provenance-free restatement of {claim_id} "
              f"from LEDGER/restatements.json")
    if leaks:
        print(f"[referee] WARNING: the submission for {claim_id} names "
              f"{leaks}. The claim statement reaches the referee verbatim, so "
              f"this tells it what answer is wanted. Recorded in the verdict; "
              f"use `make_refbox --statement` for a clean run.")
    refusals = 0
    # What the model is actually shown. build_box() applies the restatement to
    # its own copy for the box file; the wired path builds its own messages, so
    # it has to be applied here too or only the box would be clean.
    submitted = replace(claim, statement=restated) if restated else claim

    TURNS = 40
    for temp in (0.3, 0.8):
        messages = build_messages(root, submitted, proof, deps)
        # The referee gets tools so it can actually hunt counterexamples.
        for turn in range(TURNS):
            left = TURNS - turn
            # Both passes of the first two runs simply ran out of turns -- the
            # spend cap never bit (they used $0.16 of $0.60) and nothing told
            # them the end was coming, so the loop exited on a tool call and
            # there was no verdict to parse. Warn, then force.
            forcing = budget.spent - start_spend >= max_spend or left <= 2
            if forcing:
                print(f"[referee] forcing a verdict "
                      f"({'spend cap' if left > 2 else 'out of turns'}).")
                messages.append({"role": "user", "content":
                                 "[HARNESS] Stop. Emit your JSON verdict now, "
                                 "this turn, and nothing else. If you did not "
                                 "finish, say so in gap_description and set "
                                 "confidence low -- do not reject a claim you "
                                 "did not manage to check."})
            elif left <= 6:
                messages.append({"role": "user", "content":
                                 f"[HARNESS] {left} turns left. Stop starting "
                                 f"new computations and converge on a verdict."})
            reply = client.chat(
                messages,
                model=REFEREE_MODEL,
                # On the forced turn the tools are withdrawn. Asking for a
                # verdict is not enough: run 3's t=0.8 pass was asked, made a
                # tool call anyway, and the loop ended with no text to parse.
                # With no tools offered, a reply can only be the verdict.
                tools=None if forcing else tools.SCHEMA,
                temperature=temp,
                reasoning_effort="xhigh",
                tag=f"referee/{claim_id}/t{temp}",
            )
            messages.append({
                "role": "assistant",
                "content": reply.text,
                **({"tool_calls": reply.tool_calls} if reply.tool_calls else {}),
            })
            if not reply.tool_calls:
                break
            for call in reply.tool_calls:
                fn = call["function"]
                args = json.loads(fn.get("arguments") or "{}")
                result = tools.dispatch(fn["name"], args, box, sandbox=True)
                if result.startswith("REFUSED:") and "outside" in result:
                    refusals += 1
                    print(f"[referee t={temp}] blocked an escape: "
                          f"{str(args.get('command'))[:90]}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": result,
                })

        v = _parse(reply.text)
        if v is None:
            # NOT a reject. A referee that never produced a verdict has said
            # nothing about the mathematics, and mapping that to `reject` --
            # which `refuted` follows from -- silently destroys correct claims.
            # The first run of this gate did exactly that to both claims it saw.
            v = {"disposition": "inconclusive", "gap_description":
                 "no parseable verdict: the referee did not finish. This is a "
                 "harness failure and says nothing about the claim.",
                 "confidence": "none"}
        v["_temperature"] = temp
        verdicts.append(v)
        print(f"[referee t={temp}] {v.get('disposition')} -- "
              f"{(v.get('gap_description') or '')[:110]}")

    d0, d1 = (v.get("disposition") for v in verdicts)
    agreed = d0 == d1
    # Only two outcomes may move a claim: both passes accepting promotes it,
    # both passes rejecting refutes it. Everything else means the gate did not
    # resolve, and the claim is left exactly as it was.
    #
    # The earlier rule -- "disagreement falls to the weaker verdict", i.e. to
    # reject -- refuted C0012 on a run where NEITHER pass rejected it: one said
    # `accept`, the other `accept_with_gaps`, both at high confidence and both
    # explicitly finding the proof correct. A disagreement about whether to
    # flag a caveat is not evidence of falsity, and neither is a genuine
    # accept/reject split: that is an unresolved question, not a refutation.
    if agreed and d0 in ("accept", "reject"):
        final = d0
    elif "inconclusive" in (d0, d1):
        final = "inconclusive"
    else:
        final = "unresolved"

    out_dir = root / "LEDGER" / "referee"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "claim": claim_id, "agreed": agreed, "final": final,
        "sandboxed": True,
        "restated": restated,          # null = judged on the ledger statement
        "ledger_statement": claim.statement if restated else None,
        "submission_leaks": leaks,
        "escape_attempts_blocked": refusals,
        "spend": round(budget.spent - start_spend, 4),
        "verdicts": verdicts,
    }
    # An inconclusive run is a harness bug report, not a verdict. Keep it out of
    # the verdict directory, or `refereeable()` will treat the claim as judged
    # and never look at it again.
    name = (f"{claim_id}.json" if final in ("accept", "reject")
            else f"invalid/{claim_id}.{final}.json")
    (out_dir / name).parent.mkdir(parents=True, exist_ok=True)
    (out_dir / name).write_text(json.dumps(report, indent=2))

    results = [(v.get("novelty") or {}).get("result") for v in verdicts]
    known = any(r == "already known" for r in results)
    # Network is blocked in the sandbox, so the referee cannot actually search.
    # Recording novelty_checked=True on the strength of "it did not say the
    # result was known" would be a lie in the ledger; novelty is the operator's
    # job (OPERATOR_NOTES.md).
    novelty_checked = all(r == "novel" for r in results)

    if final == "accept" and not known:
        led.set_status(claim_id, "proven", session,
                       novelty_checked=novelty_checked)
        print(f"\n{claim_id} PROMOTED to proven"
              + ("." if novelty_checked
                 else " (novelty NOT checked -- the sandbox blocks search)."))
    elif final == "reject":
        led.set_status(
            claim_id, "refuted", session,
            evidence=verdicts[0].get("gap_description", "")[:400],
        )
        print(f"\n{claim_id} REFUTED by both passes. Record the lesson in "
              f"dead_ends.md.")
    elif final == "inconclusive":
        print(f"\n{claim_id} INCONCLUSIVE -- a pass did not finish. The claim "
              f"is untouched and remains refereeable. A harness problem to "
              f"fix, not a result.")
    else:
        print(f"\n{claim_id} UNRESOLVED -- the passes disagreed ({d0} vs {d1}). "
              f"Not promoted, and NOT refuted: a split is an open question, not "
              f"a refutation. The claim is untouched and remains refereeable; "
              f"read both verdicts in "
              f"LEDGER/referee/invalid/{claim_id}.unresolved.json.")

    return report


def main() -> None:
    ap = argparse.ArgumentParser(prog="harness.referee")
    ap.add_argument("claim_id", nargs="?", default="auto",
                    help="a claim id, or 'auto' for every refereeable claim")
    ap.add_argument("--root", default=".")
    ap.add_argument("--max-spend", type=float, default=1.00,
                    help="USD cap per claim (default 1.00)")
    ap.add_argument("--max-claims", type=int, default=3,
                    help="in auto mode, referee at most this many (default 3)")
    ap.add_argument("--list", action="store_true",
                    help="show what is refereeable and exit; spends nothing")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    led = Ledger(root / "LEDGER")

    if a.list or a.claim_id == "auto":
        ready, skipped = [], []
        for c in sorted(led.resolved().values(), key=lambda c: c.id):
            ok, why = refereeable(root, c)
            (ready if ok else skipped).append((c.id, c.status, c.type, why))
        print(f"refereeable now ({len(ready)}):")
        for cid, st, ty, ref in ready:
            print(f"  {cid}  {st}/{ty}  {ref}")
        if a.list:
            print(f"\nnot yet ({len(skipped)}):")
            for cid, st, ty, why in skipped:
                print(f"  {cid}  {st}/{ty}  -- {why}")
            return
        if not ready:
            print("nothing to referee.")
            return
        for cid, *_ in ready[:a.max_claims]:
            print(f"\n=== refereeing {cid} ===")
            try:
                referee(root, cid, max_spend=a.max_spend)
            except NotRefereeable as e:
                print(f"skipped: {e}")
        return

    try:
        referee(root, a.claim_id, max_spend=a.max_spend)
    except NotRefereeable as e:
        print(f"skipped: {e}")


if __name__ == "__main__":
    main()
