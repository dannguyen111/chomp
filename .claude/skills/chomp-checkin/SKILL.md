---
name: chomp-checkin
description: Catch up on the unattended chomp loop since the last check-in -- diff local vs origin, a Haiku digest of what the crons and operator changed, verified red flags, and a ranked list of actions for Opus with model and effort for each. Use when Dan says "check in", "what happened", "catch me up", or at the start of any session on this repo.
---

# Chomp check-in

The loop commits to `origin/main` unattended, so a local checkout is stale
within a day. This skill turns "what happened since I last looked" into one
cheap pass: shell for facts, Haiku for reading, the main model only for judging.

| step | who | effort |
|---|---|---|
| 0-1 facts | shell | -- |
| 2 digest | `Explore` agent, `model: haiku` | high |
| 3 verify, 4 report | main session (Opus) | medium |
| acting on the report | see the table you produce in step 4 | |

## 0. Where was the last check-in?

```bash
LAST=$(cat .git/chomp-last-checkin 2>/dev/null || git rev-parse HEAD)
```

`.git/chomp-last-checkin` is local and untracked; step 5 writes it.

## 1. Facts, from the shell only

```bash
git fetch -q --prune origin
git log --oneline --format='%h %ad %s' --date=short $LAST..origin/main
git diff --stat $LAST..origin/main -- . ':!BUDGET.log.jsonl' ':!runs/**/*.jsonl'
git branch -r | grep -v 'origin/main$'          # stray branches, incl. referee-wip/*
python ops/digest.py --since "$(git log -1 --format=%cI $LAST)"
```

If `git log` is empty: print the digest, say "nothing new since <sha>", stop.
If the digest says `Autopilot: OFF` or shows no commits, lead with that -- the
loop has stopped and nothing else matters.

## 2. Digest -- delegate to Haiku

Spawn **one** `Agent(subagent_type: "Explore", model: "haiku", effort: "high")`.
Give it `$LAST`, `origin/main`'s sha, and the `--stat` list from step 1, and
this brief:

> Read-only: no pull, checkout, commit, or edits; scratch files only in the
> scratchpad. Read the diff with `git diff $LAST..origin/main -- <path>` one
> path at a time. Never open `BUDGET.log.jsonl` or `runs/**/*.jsonl` whole --
> grep them for a specific claim id or for `REFUSED`. Read only section 0 and
> the newest dated section of OPERATOR_NOTES.md. Return at most ~900 words in
> six sections: (1) timeline, one line per commit; (2) ledger/science -- status
> changes per claim id (last entry per id in LEDGER/claims.jsonl wins), referee
> verdicts, restatements, proof-file changes in substance; (3) harness/workflow
> code changes and why; (4) budget -- spent/cap before and after, and per-tag or
> per-model spend from new BUDGET.log.jsonl lines; (5) what the notes now say
> and what they fail to mention; (6) red flags, each with file:line and marked
> CONFIRMED (seen directly) or SUSPECTED. Specifically check: any claim newly
> `proven` -- is novelty checked, are its cited lemmas in `depends_on`, and
> did its transcript's searches actually run or come back REFUSED?

## 3. Verify before repeating

Haiku is wrong sometimes and the referee fabricates. For the top 2-3
CONFIRMED flags, run **one** targeted command each (a `git show`, a `grep` of a
transcript, a `python -c` on a ledger line). Report only what survives; mark
the rest as Haiku's, unverified.

## 4. Report to Dan

1. One-paragraph summary: what ran, what changed status, spend and runway.
2. Red flags (verified first).
3. Stale notes: OPERATOR_NOTES §0's "Last updated" vs the newest dated
   section; any budget projection the digest contradicts.
4. **Actions for Opus, ranked**: action | why | model | effort | est. cost.
   Defaults:
   - proof, novelty, or referee-verdict reasoning: Opus high or xhigh
   - harness and workflow fixes: Opus medium
   - notes, docs, renames, mechanical edits: Sonnet medium
   - reading logs or transcripts: Haiku only

## 5. Record the check-in

Only if the working tree is clean:

```bash
git pull --ff-only && git rev-parse HEAD > .git/chomp-last-checkin
```

If the tree is dirty, say so and skip the pull; don't write the marker.

## Guardrails (from OPERATOR_NOTES §0, learned the expensive way)

- Never hand-edit `LEDGER/claims.jsonl`; use `harness/ledger.py`. Append-only,
  last entry per id wins.
- Never run `test_harness.py` in the real tree: copy it to the scratchpad,
  `git init && git add -A` there (the tests call `git ls-files`), blank
  `LEDGER/claims.jsonl`, and reset `BUDGET.json` + `BUDGET.log.jsonl`.
- `proven` means the proof survived the gate, not that it is new. Check
  `novelty_checked` and the literature (#G07, Sheiner) yourself.
- A referee's `novelty.searched` list is unverified: the sandbox refuses
  network, so check the transcript for `REFUSED` before believing it.
- Cloud routines can't `gh workflow run` (GraphQL 403); dispatch locally.
- Manual `workflow_dispatch` uses the $5.00 / $1.00 default caps and ignores
  `runs/AUTOPILOT` -- always pass `max_spend` and `max_claims` explicitly.
- Off switch: delete `runs/AUTOPILOT` and push.
