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
from .ledger import Ledger
from .orclient import (
    EXPLORER_MODEL,
    Budget,
    BudgetExhausted,
    OpenRouter,
)

HANDOFF_NUDGE = (
    "\n\n[HARNESS] You are at {pct:.0f}% of this session's budget; the binding "
    "limit is {which}. Stop exploring now and land your results in this order:\n"
    "  1. Append EVERY claim to LEDGER/claims.jsonl via harness.ledger. A claim "
    "that exists only in your handoff does not exist: the next session reads the "
    "ledger, and your handoff will be overwritten.\n"
    "  2. Record failed ideas in LEDGER/dead_ends.md, with the reason.\n"
    "  3. Update islands/{island}/NOTES.md.\n"
    "  4. Write islands/{island}/HANDOFF.md in the mandated format.\n"
    "Do not begin new work."
)

LEDGER_NUDGE = (
    "\n\n[HARNESS] You have appended {n} claims to the ledger this session and "
    "the session is ending. If you established anything at all, including a "
    "negative result, append it NOW with harness.ledger before writing the "
    "handoff. Prose in HANDOFF.md is not a ledger entry and does not survive."
)

FINAL_NUDGE = (
    "\n\n[HARNESS] Budget exhausted. Write islands/{island}/HANDOFF.md right "
    "now, this turn, using write_file. Nothing else."
)

STATUS = (
    "\n\n[HARNESS] budget: tokens {out:,}/{maxout:,} ({pout:.0f}%) | spend "
    "${spend:.2f}/${maxspend:.2f} ({pspend:.0f}%) | time {mins:.0f}/{maxmins} min "
    "({pmins:.0f}%) | claims logged this session: {n}"
)

# Turns allowed after a limit is breached, to land results and write the
# handoff. Session 2 ran 25 minutes past its own max-minutes and was killed by
# the GitHub job timeout instead: the loop only exited on a turn with no tool
# calls, and the model kept calling tools through every FINAL_NUDGE. This is the
# hard stop that was missing.
GRACE_TURNS = 10


def _ledger_ids(root: Path) -> set[str]:
    """Claim ids currently on disk. Used to tell the explorer, every turn, how
    many claims it has actually landed -- prose in a handoff is not a claim."""
    try:
        return {c.id for c in Ledger(root / "LEDGER").raw()}
    except Exception:                                   # noqa: BLE001
        return set()


def run(
    root: Path,
    island: str,
    *,
    max_output_tokens: int = 1_430_000,
    max_minutes: int = 300,
    session_spend_cap: float = 5.00,
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
    claims_at_start = _ledger_ids(root)

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
    over_since: int | None = None
    which = "none"

    def write_summary() -> dict:
        """Rewritten after every turn, so a session killed by the platform
        still leaves a summary. Session 2 was cancelled mid-loop and left only
        a transcript, because this used to run once after the loop."""
        s = {
            "session": session_id,
            "island": island,
            "turns": turn,
            "output_tokens": out_tokens,
            "minutes": round((time.time() - started) / 60, 1),
            "cost": round(budget.spent - start_spend, 4),
            "total_spent": round(budget.spent, 4),
            "remaining": round(budget.remaining, 4),
            "handoff_written": (root / "islands" / island / "HANDOFF.md").exists(),
            "claims_appended": sorted(_ledger_ids(root) - claims_at_start),
            "stopped_on": which,
            "complete": False,
        }
        (run_dir / "summary.json").write_text(json.dumps(s, indent=2))
        return s

    while True:
        turn += 1
        elapsed_min = (time.time() - started) / 60
        session_spend = budget.spent - start_spend
        # Pace against whichever limit is closest, not output tokens alone. A
        # session bounded by wall clock or spend otherwise gets no warning at
        # all and simply stops -- which is how session 1 ended with its results
        # stranded in handoff prose instead of in the ledger.
        fracs = {
            "output tokens": out_tokens / max_output_tokens,
            "wall clock": elapsed_min / max_minutes,
            "spend": session_spend / session_spend_cap,
        }
        which = max(fracs, key=fracs.get)
        pct = 100 * fracs[which]
        over = pct >= 100
        n_claims = len(_ledger_ids(root) - claims_at_start)

        if over and over_since is None:
            over_since = turn
        # Hard stop. Nudging is a request; this is the enforcement. Without it a
        # model that keeps calling tools never reaches the `not reply.tool_calls`
        # exit below, and the run dies on the platform timeout instead.
        if over_since is not None and turn - over_since >= GRACE_TURNS:
            log({"event": "grace_exhausted", "turn": turn, "limit": which,
                 "grace_turns": GRACE_TURNS})
            print(f"[session] {GRACE_TURNS} turns past the {which} limit; "
                  f"stopping.")
            break

        if over and nudged:
            messages.append({"role": "user",
                             "content": FINAL_NUDGE.format(island=island)})
        elif (over or pct >= 85) and not nudged:
            messages.append({"role": "user", "content": HANDOFF_NUDGE.format(
                pct=pct, which=which, island=island)})
            if n_claims == 0:
                messages.append({"role": "user",
                                 "content": LEDGER_NUDGE.format(n=n_claims)})
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

        # Live budget readout. Appended at the END of the conversation, so the
        # cached prefix is untouched. Session 1 had no idea which limit it was
        # against and guessed wrong, so it truncated its own write-up.
        messages.append({"role": "user", "content": STATUS.format(
            out=out_tokens, maxout=max_output_tokens, pout=100 * fracs["output tokens"],
            spend=session_spend, maxspend=session_spend_cap,
            pspend=100 * fracs["spend"], mins=elapsed_min, maxmins=max_minutes,
            pmins=100 * fracs["wall clock"], n=n_claims)})
        write_summary()

    summary = write_summary()
    summary["complete"] = True
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    log({"event": "end", **summary})

    print("\n" + json.dumps(summary, indent=2))
    if not summary["handoff_written"]:
        print("\n!! NO HANDOFF WRITTEN -- read the transcript before spending more.")
    if not summary["claims_appended"]:
        print("\n!! NO CLAIMS APPENDED -- a session that logged nothing to the "
              "ledger left nothing behind. Read the handoff and the transcript "
              "before spending more.")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--island", default="01-recurrence", choices=list(prompt.ISLANDS))
    ap.add_argument("--max-output-tokens", type=int, default=1_430_000)
    ap.add_argument("--max-minutes", type=int, default=300)
    ap.add_argument("--session-cap", type=float, default=5.00)
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
