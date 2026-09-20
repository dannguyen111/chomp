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


def referee(root: Path, claim_id: str, session: str = "referee") -> dict:
    led = Ledger(root / "LEDGER")
    resolved = led.resolved()
    claim = resolved.get(claim_id)
    if claim is None:
        raise SystemExit(f"no such claim {claim_id}")
    if not claim.proof_ref:
        raise SystemExit(f"{claim_id} has no proof_ref; nothing to referee")

    proof_path = root / claim.proof_ref
    if not proof_path.exists():
        raise SystemExit(f"proof file missing: {claim.proof_ref}")
    proof = proof_path.read_text()
    deps = {d: resolved[d] for d in claim.depends_on if d in resolved}

    client = OpenRouter(Budget(root / "BUDGET.json"))
    verdicts = []

    for temp in (0.3, 0.8):
        messages = build_messages(root, claim, proof, deps)
        # The referee gets tools so it can actually hunt counterexamples.
        for _ in range(40):
            reply = client.chat(
                messages,
                model=REFEREE_MODEL,
                tools=tools.SCHEMA,
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
                messages.append({
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": tools.dispatch(fn["name"], args, root),
                })

        v = _parse(reply.text)
        if v is None:
            v = {"disposition": "reject", "gap_description":
                 "referee emitted no parseable verdict", "confidence": "low"}
        v["_temperature"] = temp
        verdicts.append(v)
        print(f"[referee t={temp}] {v.get('disposition')} — "
              f"{(v.get('gap_description') or '')[:110]}")

    d0, d1 = (v.get("disposition") for v in verdicts)
    agreed = d0 == d1
    # Disagreement is never an accept. Split decisions fall to the weaker verdict.
    final = d0 if agreed else "reject"

    out_dir = root / "LEDGER" / "referee"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "claim": claim_id, "agreed": agreed, "final": final, "verdicts": verdicts,
    }
    (out_dir / f"{claim_id}.json").write_text(json.dumps(report, indent=2))

    novel = all(
        (v.get("novelty") or {}).get("result") != "already known" for v in verdicts
    )
    if final == "accept" and agreed and novel:
        led.set_status(claim_id, "proven", session, novelty_checked=True)
        print(f"\n{claim_id} PROMOTED to proven.")
    elif final == "reject":
        led.set_status(
            claim_id, "refuted", session,
            evidence=verdicts[0].get("gap_description", "")[:400],
        )
        print(f"\n{claim_id} REFUTED. Record the lesson in dead_ends.md.")
    else:
        print(f"\n{claim_id} left at '{claim.status}' "
              f"(disposition={final}, agreed={agreed}, novel={novel}).")

    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("claim_id")
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    referee(Path(a.root).resolve(), a.claim_id)


if __name__ == "__main__":
    main()
