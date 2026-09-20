# Effective Byrnes for 3-Row Chomp

An agent harness attacking one open problem: put a computable bound on the
preperiod in Byrnes' eventual-periodicity theorem for 3-row Chomp.

**Start here: `KICKOFF.md`.** Open Claude Code in this directory and paste:

    Read KICKOFF.md and execute it autonomously from Step 1. Stop only at the
    two STOP points it defines. Do not create or use an OPENROUTER_API_KEY.

Everything else in this file is reference.

## Reading order
| File | What it is |
|---|---|
| `KICKOFF.md` | The setup runbook. Phase 0 through cloud deploy. |
| `MISSION.md` | The problem, what is proven, the target. Immutable. |
| `CLOUD.md` | GitHub Actions deploy. Free, no machine left open. |
| `prompts/` | Explorer and referee system prompts. |

## Running locally
    export OPENROUTER_API_KEY=sk-or-...
    pip install requests
    python test_harness.py          # offline, spends nothing
    ./run.sh 01-recurrence          # ~$3, one session

`flock` in `run.sh` means a cron trigger starts a session only when none is
alive. In the cloud the Actions concurrency group does the same job.

## Budget
$30 total, about 8 to 12 sessions. `BUDGET.json` is the hard cap and survives
crashes. Cost comes from OpenRouter's own accounting, never from hardcoded
prices. Phase 0 spends nothing and should be done on a Claude subscription.

## Three checkpoints
1. **After Phase 0.** Is the solver validated, does the sqrt(2) seed hold?
2. **After session 1.** Read the transcript before automating anything. In the
   cloud this is enforced: scheduled runs exit unless `runs/AUTOPILOT` exists.
3. **Around session 5.** Concentrate the rest on whichever island is producing.

## Layout
    MISSION.md              immutable; prefixed to every session
    prompts/                explorer + referee system prompts
    GROUND_TRUTH/           solver + fixtures; read-only to agents
    LEDGER/claims.jsonl     append-only, last-write-wins
    LEDGER/dead_ends.md     the most cost-effective file here
    islands/<id>/           NOTES.md, HANDOFF.md, scratch/
    runs/<session>/         transcript + summary
    BUDGET.json             hard cap, survives crashes
    .github/workflows/      phase0 (manual) + session (cron, gated)
