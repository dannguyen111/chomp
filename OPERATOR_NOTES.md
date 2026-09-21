# Operator notes

State of play for whoever is driving this, including a future session of me
with no memory of the last one. The *science* lives in `LEDGER/`,
`GROUND_TRUTH/` and the island `NOTES.md`; this file is the *operations* layer:
what has been run, what broke, what to run next, and the conventions that were
learned the expensive way.

Last updated: 2026-09-21, after session 2 and the Opus pre-screen.

---

## 1. Where things stand

**Budget: $2.72 of $30 spent. $27.28 left.** All of it on OpenRouter; the Opus
pre-screens were billed to the Claude plan instead.

| | |
|---|---|
| Repo | `github.com/dannguyen111/chomp`, public |
| Ledger | 26 lines, 21 active |
| Proven | **nothing** -- the referee gate has never run |
| Refereeable now | C0012, C0021 (both `lemma`, both with proof files) |
| Autopilot | **off** (`runs/AUTOPILOT` does not exist) |

Sessions run so far:

- **S20260920T2126** (island 01) -- 47 turns, $0.50, 93% cache. Produced C0012
  but logged **zero** claims; results were stranded in handoff prose and
  recovered by hand.
- **S20260921T0215** (island 02) -- 130 turns, $2.15, 97% cache. Logged
  C0014-C0020 correctly. Killed by the GitHub job timeout, not by its own
  limit; state survived only because `Commit state` has `if: always()`.

## 2. The next two things to run

### (a) The wired referee, on GitHub Actions -- never yet executed

Zero local load. This is the higher priority of the two, because it is the only
mechanism that can *kill* a bad claim, and it has never run.

```bash
gh workflow run referee --repo dannguyen111/chomp \
  -f claim_id=auto -f max_spend=1.00 -f max_claims=3
```

Expect ~$0.30/pass, two passes per claim, so ~$0.60-1.20 for C0012 and C0021.
Verdicts land in `LEDGER/referee/<id>.json` and are committed back.
`python -m harness.referee --list` is a free dry run showing what is eligible.

### (b) The Opus pre-screen, in a provenance-clean sandbox

Rebuild the sandbox first -- it is *not* in the repo and does not survive a
session:

```bash
python -m harness.make_refbox C0021 --out /tmp/refbox \
  --census GROUND_TRUTH/cache/census_20000.tsv \
  --statement "For every P-position (p,q,r) of 3-row Chomp with r >= 1, p - q <= 3r - 1; equivalently max over q >= r of (f(q,r) - q) is at most 3r - 1."
```

Then point two **fresh** agents at it (never a fork -- a fork inherits the
operator's context, which includes the expected answer). Give each the
directory and nothing else. Require both to agree; disagreement is a reject.

**Run these in the cloud if the local machine matters.** It is not the model
calls that load the CPU, it is the referees' own compute: pass A ran an
independent Python reimplementation of the recurrence, a 16M-cell sweep to
`q,r <= 4000`, columns to `r = 30000`, and a census to `r = 20000` -- 36 tool
calls over 35 minutes, with a second agent doing the same in parallel.
Either use remote agent isolation, or pass in the precomputed censuses below so
the sweeps are cheap.

## 3. Conventions learned the expensive way

**Claim statements reach the referee verbatim. Keep them provenance-free.**
Ours narrate project history -- "CORRECTION of C0009", "the Phase 0 audit set
this as island 01's opening target", "discharges (Z1) of byrnes_audit.md" --
which tells an adversarial reader exactly what answer is wanted, and cites
documents it cannot see. `make_refbox` now refuses to build a box whose
submission trips that check; use `--statement` to hand over the mathematics
alone, and record in the verdict that you restated it. Put the narrative in
`evidence`, which the referee never sees.

**Numerical agreement can confirm a true statement while the sentence around it
is false.** Two errors got through this way:

- the Lemma 5 coordinate (`n = p-q` instead of `p-r`) produced a *true but
  weaker* inequality, so every numerical check passed while the claim about
  what remained open was wrong -- and an entire island target was built on the
  artefact;
- `proofs/C0012.md` said all 402 tight cells lie on row `r=0`; the count was
  right, the attribution wasn't, and `(1,1)` had been printed in the operator's
  own verification output.

Check the sentence, not just the number.

**The caps are soft.** `over` is evaluated at the top of a turn, so a session
overshoots by up to `GRACE_TURNS` (10) turns while landing its results. Read
`--max-output-tokens` as a target, not a ceiling.

**In GitHub Actions, wall clock binds before dollars.** At the observed pace $5
is ~570 minutes and a hosted job is hard-killed at 360. Session cap 5.00,
`--max-minutes 300`, `timeout-minutes: 355`. Sessions land at $2-3.

## 4. Known defects, not yet fixed

**~~The wired referee can read its way around the redaction.~~ FIXED
2026-09-21.** `referee.py` now builds an isolated box with
`make_refbox.build_box()` and runs its tools against *that*, not the project
root, with `tools.dispatch(..., sandbox=True)`. The box holds the submission,
the solver and a usage note -- nothing else. `bash` runs with `shell=True`, so
root-scoping alone never constrained it (`cat ../../LEDGER/claims.jsonl` walked
straight out); sandbox mode additionally refuses any command reaching for a
parent directory, an absolute path or a home directory. Verdict records now
carry `sandboxed`, `submission_leaks` and `escape_attempts_blocked` -- a
referee that *tries* to escape is itself worth knowing about.

**C0013 is not refereeable and should not be sent.** It has no proof file, and
C0023 established that its displayed closed form is wrong -- the Zeilberger
state count omits the preperiod `a_0(r)`, so the true shape is a recursion.
Redo the derivation before refereeing it.

**The two failed pre-screen agents.** Referee pass B and the audit of the
computational claims (C0001/C0003/C0005) both died on a Claude plan spend
limit. The audit agent was asked to re-derive figures from a 50k-row census
(~7 min, ~0.5 GB) -- split it into one agent per claim and cap it at the r=10000
census next time.

## 5. What is durable and what is not

**In git, survives anything:** the ledger, both proof files, the referee verdict
records, `byrnes_audit.md` (with its ERRATA block), `seed_check.md`/`.png`,
island NOTES and HANDOFFs, all three workflows, the harness, `BUDGET.json`.

**On disk, gitignored, survives a reboot:** `.env` (the OpenRouter key) and
`GROUND_TRUTH/cache/` -- which now holds validated censuses at r = 3000, 10000,
15000 and 20000. Every census file ends in a `# complete rmax=... rows=...`
trailer; `chomp.census()` refuses one without it, because a truncated file used
to parse as a valid tiny census and silently poison everything downstream.

**Does not survive the session:** the refbox sandbox (rebuild with
`make_refbox`), the ability to resume a subagent, and the operator context --
which is what this file is for.
