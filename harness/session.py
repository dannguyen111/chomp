"""Explorer session runner.

A session is the unit of work: one long conversation with live state, not a
stateless tick. It ends when the token budget, wall clock or spend cap says so
-- and it always ends by writing a handoff, because an unfinished session that
left no notes is money burned twice.
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from . import prompt, tools
from .orclient import (
    EXPLORER_MODEL,
    Budget,
    BudgetExhausted,
    OpenRouter,
)

HANDOFF_NUDGE = (
    "\n\n[HARNESS] You are at {pct:.0f}% of this session's token budget. Stop "
    "exploring now. Append any claims to LEDGER/claims.jsonl, record failures in "
    "LEDGER/dead_ends.md, update your island NOTES.md, and write HANDOFF.md in "
    "the mandated format. Do not begin new work."
)

FINAL_NUDGE = (
    "\n\n[HARNESS] Budget exhausted. Write HANDOFF.md right now, this turn, "
    "using write_file. Nothing else."
)


def run(
    root: Path,
    island: str,
    *,
    max_output_tokens: int = 220_000,
    max_minutes: int = 240,
    session_spend_cap: float = 3.00,
    temperature: float = 0.7,
) -> dict:
    session_id = datetime.now(timezone.utc).strftime("S%Y%m%dT%H%M")
    run_dir = root / "runs" / session_id
    run_dir.mkdir(parents=True, exist_ok=True)

    prompt.assert_stable_prefix(root, island)

    budget = Budget(root / "BUDGET.json")
    client = OpenRouter(budget)
    start_spend = budget.spent
    started = time.time()

    messages = prompt.build(root, island, session_id)
    transcript = run_dir / "transcript.jsonl"

    def log(obj: dict) -> None:
        with transcript.open("a") as f:
            f.write(json.dumps(obj, default=str) + "\n")

    log({"event": "start", "island": island, "session": session_id,
         "prefix": prompt.prefix_fingerprint(root, island)})

    out_tokens = 0
    nudged = False
    turn = 0

    while True:
        turn += 1
        elapsed_min = (time.time() - started) / 60
        session_spend = budget.spent - start_spend
        pct = 100 * out_tokens / max_output_tokens

        over = (
            out_tokens >= max_output_tokens
            or elapsed_min >= max_minutes
            or session_spend >= session_spend_cap
        )

        if over and nudged:
            messages.append({"role": "user", "content": FINAL_NUDGE})
        elif (over or pct >= 85) and not nudged:
            messages.append({"role": "user", "content": HANDOFF_NUDGE.format(pct=pct)})
            nudged = True

        try:
            reply = client.chat(
                messages,
                model=EXPLORER_MODEL,
                tools=tools.SCHEMA,
                temperature=temperature,
                reasoning_effort="xhigh",
                tag=f"explorer/{island}/{session_id}",
            )
        except BudgetExhausted as e:
            log({"event": "budget_exhausted", "detail": str(e)})
            print(f"[session] {e}")
            break

        out_tokens += reply.completion_tokens
        log({
            "event": "assistant", "turn": turn, "text": reply.text,
            "tool_calls": reply.tool_calls, "cost": reply.cost,
            "in": reply.prompt_tokens, "cached": reply.cached_tokens,
            "out": reply.completion_tokens,
        })
        cache_pct = (
            100 * reply.cached_tokens / reply.prompt_tokens
            if reply.prompt_tokens else 0
        )
        print(
            f"[t{turn:03d}] ${reply.cost:.4f}  out={reply.completion_tokens:>6}  "
            f"cache={cache_pct:>3.0f}%  spent=${budget.spent:.2f}"
        )

        messages.append({
            "role": "assistant",
            "content": reply.text,
            **({"tool_calls": reply.tool_calls} if reply.tool_calls else {}),
        })

        if not reply.tool_calls:
            # No tools requested. If we already forced the handoff, we're done.
            if over:
                break
            messages.append({
                "role": "user",
                "content": "[HARNESS] Continue. Test the next concrete thing.",
            })
            continue

        for call in reply.tool_calls:
            fn = call["function"]
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except json.JSONDecodeError as e:
                result = f"TOOL ERROR: unparseable arguments: {e}"
            else:
                result = tools.dispatch(fn["name"], args, root)
            log({"event": "tool", "name": fn["name"], "args": fn.get("arguments"),
                 "result": result[:4000]})
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": result,
            })

    summary = {
        "session": session_id,
        "island": island,
        "turns": turn,
        "output_tokens": out_tokens,
        "minutes": round((time.time() - started) / 60, 1),
        "cost": round(budget.spent - start_spend, 4),
        "total_spent": round(budget.spent, 4),
        "remaining": round(budget.remaining, 4),
        "handoff_written": (root / "islands" / island / "HANDOFF.md").exists(),
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    log({"event": "end", **summary})

    print("\n" + json.dumps(summary, indent=2))
    if not summary["handoff_written"]:
        print("\n!! NO HANDOFF WRITTEN -- read the transcript before spending more.")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--island", default="01-recurrence", choices=list(prompt.ISLANDS))
    ap.add_argument("--max-output-tokens", type=int, default=220_000)
    ap.add_argument("--max-minutes", type=int, default=240)
    ap.add_argument("--session-cap", type=float, default=3.00)
    ap.add_argument("--temperature", type=float, default=0.7)
    a = ap.parse_args()
    run(
        Path(a.root).resolve(),
        a.island,
        max_output_tokens=a.max_output_tokens,
        max_minutes=a.max_minutes,
        session_spend_cap=a.session_cap,
        temperature=a.temperature,
    )


if __name__ == "__main__":
    main()
