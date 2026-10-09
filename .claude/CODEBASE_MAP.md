---
sha: 0eee105f8a31d120a31f1b54c0b9f73940b3ad1e
branch: main
timestamp: 2026-10-09T16:36:58Z
---
# CODEBASE MAP: chomp-harness (Effective Byrnes for 3-Row Chomp)


## Project Summary
Autonomous math-research harness that attacks one open problem: a computable bound on the preperiod in Byrnes' eventual-periodicity theorem for 3-row Chomp. LLM "explorer" sessions (OpenRouter, MiMo-V2.6-Pro) run on GitHub Actions crons, append claims to an append-only ledger, and an adversarial "referee" gate is the only path to `proven`. Operator is Dan Nguyen; the repo is public, with the Lean archive kept private (see Conventions).

## Commands
Run from repo root. No pyproject, requirements.txt, lint, or formatter is configured. Deps are `requests` (CI adds `matplotlib` for phase0).
- Install: `pip install requests` (plus `matplotlib` for seed_check). CI uses Python 3.12. Local `__pycache__` is cpython-311.
- Offline tests (spend nothing, no network): `python test_harness.py`. Copies tracked files to a temp dir for session/ledger tests.
- Build solver (Linux/CI): `g++ -O3 -march=x86-64-v3 -flto -o GROUND_TRUTH/solver GROUND_TRUTH/solver.cpp`. On Windows/any: `python -c "from GROUND_TRUTH import chomp; chomp.build()"` (MSVC env on nt).
- Validate vs literature: `python -m GROUND_TRUTH.tests.run_all --max-r 1000` (~10 s) or `--max-r 10000` (~55 s).
- Session (one explorer run): `./run.sh 01-recurrence` (needs OPENROUTER_API_KEY in env or `.env`) or `python -m harness.session --root . --island 01-recurrence --session-cap 1.50`.
- Referee: `python -m harness.referee --list` (free). `python -m harness.referee C0032 --root . --max-spend 1.00`. `python -m harness.referee auto --max-claims 1`.
- Referee sandbox for hand inspection: `python -m harness.make_refbox C0012 --out <dir>` (`--statement` for a clean restatement).
- Recover a dead referee job: `python -m ops.recover_referee --dry-run`.
- Daily digest (read-only): `python3 ops/digest.py --since '25 hours ago'`.
- Workflows (manual): `gh workflow run phase0 | session | referee` (Actions cron is gated by `runs/AUTOPILOT`).
- Operator steps: see `OPERATOR_NOTES.md` §0 (pull, then run digest first). Not duplicated here.

## Technologies
- Python 3.x (stdlib + `requests`); `from __future__ import annotations`, dataclasses, walrus.
- C++ solver `GROUND_TRUTH/solver.cpp` (streaming, interval-compressed, no O(r^2) table). Subcommands `table`, `row`, `column`.
- OpenRouter chat-completions API, tool calling. Model `xiaomi/mimo-v2.6-pro` (explorer and referee; LIBRARIAN_MODEL unused). `reasoning: {effort: xhigh}`, `usage.include` for real cost.
- GitHub Actions (ubuntu-latest): `session.yml`, `referee.yml`, `phase0.yml`; `actions/cache` for solver binary.
- Bash (`run.sh`), Git (`merge=union` ledger, `text=auto eol=lf`).
- Claude Code project settings: `.claude/settings.json` denies Read of `BUDGET.log.jsonl`, `runs/**/*.jsonl`, `GROUND_TRUTH/**/*.tsv`. Skill: `.claude/skills/chomp-checkin/SKILL.md`.

## Directory Structure
```
chomp/
  README.md, KICKOFF.md, MISSION.md   setup runbook; immutable problem statement (prefixed to every explorer session)
  OPERATOR_NOTES.md                  ops handoff, 736 lines; §0 authoritative (linked, not copied)
  CLOUD.md                           GitHub Actions deploy notes
  run.sh                             local watchdog: flock or mkdir lock, then harness.session
  BUDGET.json                        {cap 30.0, spent, calls}; hard cap; read by workflow gates
  BUDGET.log.jsonl                   one line per paid call (DO NOT read whole; union-merged)
  test_harness.py                    offline tests (17 test_* funcs), real state untouched
  harness/                           the engine (Python package)
    session.py                       explorer loop: budget pacing, nudges, transcript, summary
    referee.py                       referee gate: queue, two passes, verdict, ledger promotion
    orclient.py                      OpenRouter client + persistent Budget (cap check, charge)
    ledger.py                        Claim model + append-only ledger, last-write-wins
    prompt.py                        prompt assembly with byte-stable prefix + fingerprint guard
    tools.py                         explorer/referee tools: bash, read_file, write_file (+ sandbox)
    make_refbox.py                   isolated referee box (prompt + solver + census), leak scan
  prompts/                           explorer.md, referee.md (system prompts; stable prefix / referee system)
  ops/                               digest.py (read-only facts), recover_referee.py, DIGEST_PROMPT.md (for cloud digest agent)
  .github/workflows/                 session.yml (cron 03:17 UTC), referee.yml (cron 09:17 UTC), phase0.yml (manual)
  LEDGER/                            shared research state (see Architecture)
    claims.jsonl                     append-only claims (DO NOT read beyond first few lines)
    dead_ends.md                     failed ideas with reasons; shown to every explorer
    mission_disputes.md, restatements.json (provenance-free claim wording for referee)
    referee/                         verdicts C####.json, invalid/, attempts.json, hold.json, progress/ (transient)
  islands/<id>/                      NOTES.md (cumulative), HANDOFF.md (overwritten each session), proofs/, scratch/ (gitignored)
    01-recurrence/                   Brouwer recurrence attack (proofs/ has C0012, C0021, C0024, C0027, C0028, C0032_machine, C0041, C0080)
    02-renorm/                       Friedman-Landsberg renormalization picture (no proofs/ yet)
  GROUND_TRUTH/                      read-only oracle + literature (explorer may not write here)
    solver.cpp, chomp.py             oracle source; chomp.build() compiles on demand (binary gitignored)
    seed_check.py / .md / .png       MISSION §5 sqrt(2) seed test write-up
    byrnes_audit.md                  where Byrnes loses effectivity
    tests/                           run_all.py drives 25 literature checks; tests/data/SOURCES.md
    cache/                           censuses census_{3000,10000,15000,20000}.tsv, census_50000.log (gitignored)
    data/                            third-party papers, gitignored (fetch_sources.py)
    lean/                            README only committed; chomp-lean/ is a PRIVATE repo clone (gitignored)
  runs/                              per-session output: S<YYYYMMDDTHHMM>/{summary.json,transcript.jsonl}
    referee/run-<N>/                 per-claim transcripts + heartbeat.txt
    AUTOPILOT                        empty file; its presence enables the crons
    .prefix-<island>                 prompt fingerprint (gitignored; local only)
```

## Key Entry Points
- `harness/session.py:258` `main()`, `:72` `run()`: one explorer session. CLI: `--root --island --session-cap --max-output-tokens --max-minutes --temperature`.
- `harness/referee.py:579` `main()`, `:297` `referee()`: one claim, two passes (temps 0.3 and 0.8). Modes: `<id>`, `auto`, `--list`.
- `harness/make_refbox.py:125` `main()`, `:64` `build_box()`: build a sandboxed referee directory.
- `harness/orclient.py:124` `OpenRouter.chat()`: only path that spends money. `:46` `Budget`.
- `harness/tools.py:241` `dispatch()`: tool router. `:54` `SCHEMA` (bash, write_file, read_file).
- `ops/digest.py:92` `main()`; `ops/recover_referee.py:185` `main()`.
- `GROUND_TRUTH/chomp.py` `build()`, `census()`, `table()`, `row()`: Python face of the solver.
- Workflows: `.github/workflows/session.yml` (gate, island pick, commit `runs BUDGET LEDGER islands`), `referee.yml` (recover, per-claim loop, 5-min snapshots), `phase0.yml` (self-test in /tmp copy, build, validate, cache, commit).

## Architecture Notes
Data flow (unattended loop):
1. cron `session.yml` 03:17 UTC. Gate: `runs/AUTOPILOT` exists, `remaining >= cap` (cron cap $1.50). Restores solver cache (`fail-on-cache-miss`). Island = run_number parity (01 or 02).
2. `session.run()` builds messages via `prompt.build()`: system = `explorer.md` + `MISSION.md` (stable, fingerprinted); user = volatile suffix (LEDGER render, dead_ends, island NOTES, HANDOFF) + "begin" line. Volatile content must stay at the END.
3. Loop: `OpenRouter.chat()` (budget.check, then POST, then `budget.charge(usage.cost)`), then `tools.dispatch()` per tool call, with the result fed back. Every turn writes `summary.json`. Explorer claims are written with `Ledger.add/append` (via bash `python -c` or `write_file`).
4. Pacing: `max(output tokens, wall clock, spend)` fraction. At >=85% a HANDOFF nudge; at 100% a FINAL nudge; after `GRACE_TURNS=10` hard stop. A no-tool-call reply ends the loop only when over budget.
5. Commit step (`session.yml`) pushes BUDGET, BUDGET.log, LEDGER, islands, runs to `main`, with 3 rebase-retries.
6. cron `referee.yml` 09:17 UTC (cron cap $0.75, 1 claim). Recovers dead runs from `referee-wip/run-N` branches (`ops/recover_referee.py`). Then, per claim: `referee.referee()` refereeable queue, box via `make_refbox`, passes at t=0.3 and t=0.8 (TURNS=40, forced verdict when spend>=cap or 2 turns left), verdict files, then `set_status`. A background loop pushes a snapshot to `referee-wip/run-N` every 5 min. Each claim is committed under `flock` (`/tmp/chomp-git.lock`).
7. Promotion rule (`referee.py:501-506`): `accept` on both passes -> `proven` (unless any novelty result is "already known"). `reject` on both -> `refuted`. Everything else (split, accept_with_gaps, inconclusive) leaves the claim untouched.
8. Daily digest: an external scheduled cloud agent runs `ops/digest.py` read-only and reports (see `ops/DIGEST_PROMPT.md`).
9. `phase0.yml` (manual, once): self-test in /tmp copy (`test_harness.py`, blanks LEDGER first), build solver, validate `run_all`, `actions/cache/save` keyed `solver-<hash of solver.cpp>`, commit GROUND_TRUTH/LEDGER/islands.

State and config locations:
- Budget: `BUDGET.json` (totals). `Budget.check(headroom=0.25)` before each call (orclient.py:91). Per-call log: `BUDGET.log.jsonl`. Cost is OpenRouter's `usage.cost` only, never a hardcoded price.
- Secret: `OPENROUTER_API_KEY` from `.env` (local, gitignored) or GitHub secret. Stripped from the explorer's and referee's shell env (`tools._tool_env`, tools.py:224).
- Claims: `LEDGER/claims.jsonl`. `Claim` fields: id `C####`, statement, type (lemma|conjecture|observation|solver_bug), status (open|evidence|proven|refuted|superseded), proof_ref, depends_on, verified_range, novelty_checked, session. Last line per id wins (`Ledger.resolved`, ledger.py:68). Explorer sees open/evidence/proven only (`active`, ledger.py:75).
- Referee output: `LEDGER/referee/<C>.json` (accept/reject only). Anything else goes to `LEDGER/referee/invalid/<C>.<final>.<n>.json` and increments `attempts.json`. `hold.json` takes claims out of the queue with a reason. `progress/<C>.json` is transient, saved at pass boundaries and deleted at end. `LEDGER/restatements.json` holds provenance-free statements used for the referee.
- Island state: `islands/<id>/NOTES.md`, `HANDOFF.md`. `prompt.ISLANDS` (prompt.py:19) defines the thesis; CLI `--island` choices come from it.
- Sandbox policy: `tools.PROTECTED` (tools.py:119) = GROUND_TRUTH, MISSION.md, prompts, harness, BUDGET.json, BUDGET.log.jsonl. `_escapes()` (tools.py:179) applies only when `sandbox=True` (referee): blocks network tools, `/` sweeps, and absolute paths outside the box (`/tmp` and `/dev/*` allowed).
- Concurrency: all three workflows share concurrency group `chomp` (`cancel-in-progress: false`). `run.sh` uses flock or mkdir lock locally.

## Conventions & Gotchas
- Provenance is the referee's whole point. `redacted_mission()` (referee.py:35) keeps only MISSION §§1-4 and 6 (`ALLOWED_SECTIONS`). The referee box (make_refbox) contains only REFEREE_PROMPT.md, the solver, SOLVER.md, and censuses. Its leak scan (make_refbox.py `build_box`) flags words like "handoff", "ledger", "island", "referee", "prescreen". Use `--statement` to restate.
- Only `lemma`-type claims, or those whose `proof_ref` is under `/proofs/`, go to the referee (`refereeable`, referee.py:193). Observations are validated by the solver instead. A proof file shared with a lemma is refereed once, as the lemma's.
- Both passes use the SAME model, differing only in temperature (0.3, 0.8). The schedule's `REFEREE_MODEL` is in the fingerprint, so a model change invalidates saved passes.
- Verdict parsing: `_parse` returns the LAST JSON object with a `disposition` key. It falls back to a quote-repair pass (`_escape_stray_quotes`, marks `_repaired`). A missing verdict becomes `inconclusive`, never `reject`. This is deliberate (see the comment at referee.py:465).
- Referee forced turn: tools are withdrawn (`tools=None`) so the reply must be the verdict. A verdict is retried once if unparseable.
- Saved passes resume (`_progress_path`, `_fingerprint`, referee.py:266-280). Reuse requires the same messages, model, and ENVIRONMENT files (solver.cpp, chomp.py, tools.py, make_refbox.py). `referee.py` itself is deliberately excluded.
- `referee()` does NOT catch `BudgetExhausted` (only `main()` catches `NotRefereeable`). A mid-pass budget stop crashes the claim with no verdict. Completed passes survive in progress/ and are reused on rerun.
- "Already refereed" means `LEDGER/referee/<C>.json` exists. Unresolved claims stay eligible, and the auto queue orders by attempts (fewest first).
- Explorer `bash` is NOT sandboxed (`session.py` calls `dispatch` without `sandbox=True`). Its `bash` has network and git access and is not confined to the root (`cd` escapes it). `write_file` is confined to the project root (`_resolve`) and only refuses PROTECTED paths, so `write_file` can overwrite `LEDGER/claims.jsonl`. "Append-only" is convention, not enforced. `LEDGER/` is not in PROTECTED.
- Prompt cache discipline: `assert_stable_prefix` (prompt.py:91) raises SystemExit when the fingerprint of explorer.md + MISSION.md changes. Its state file `runs/.prefix-<island>` is gitignored and never committed, so the guard only works locally. In CI it cannot trip. The `prompt.py` docstring still says "DeepSeek caches"; the model is now MiMo.
- `session.run` defaults (`max_output_tokens=1_430_000`, `max_minutes=300`, `session_spend_cap=5.00`) are overridden by the cron (cap 1.50). The job timeout is 355 min. `referee.yml` stops starting claims after 260 min.
- `runs/AUTOPILOT` gates the crons only. `workflow_dispatch` ignores it.
- `ops/DIGEST_PROMPT.md` lists the referee cron at 09:00; `referee.yml` says 09:17.
- `.gitattributes` forces LF. `run.sh` breaks on CRLF on Linux runners. Keep `LEDGER/claims.jsonl` as `merge=union`, and never rewrite it.
- `GROUND_TRUTH/solver*`, `GROUND_TRUTH/cache/`, `GROUND_TRUTH/data/`, `islands/*/scratch/`, `runs/.prefix-*`, `.env`, and `GROUND_TRUTH/lean/*` (except README) are gitignored. A stale local binary is a known way to pass a false lemma. Rebuild after editing solver.cpp.
- `test_harness.py` must never write the real tree. Tests copy tracked files to a temp dir. Its ledger tests use an empty ledger, and phase0 blanks `LEDGER/claims.jsonl` before running it.
- Lean/Sheiner material is private. The repo clone `GROUND_TRUTH/lean/chomp-lean` is a separate private repo (dannguyen111/chomp-lean), gitignored. Never commit, paste, or publish any of it. Do not read it into public artifacts.
- Local-only quirks: `run.sh` needs bash (Git Bash on Windows works; flock absent, so the mkdir lock is used). The `/tmp/chomp-git.lock` and `/tmp/recover.txt` paths are Linux-runner only.
- Known-taken literature: a claim may be held in `LEDGER/referee/hold.json` (prior art). Check `dead_ends.md` and `hold.json` before refereeing something new.
