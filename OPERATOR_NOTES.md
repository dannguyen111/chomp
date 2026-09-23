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

## 3a. The first referee run, and what it cost

Run 35654519435 (2026-09-21) produced no verdicts and **marked both claims
`refuted`**. Neither referee ever argued against the mathematics; all four
passes were starved by the sandbox and never emitted JSON, and referee.py
mapped an unparseable reply to `reject`, which `refuted` follows from. The
claims have been restored to `open` and the verdict files quarantined under
`LEDGER/referee/invalid/`.

Two bugs, both mine, both now fixed:

1. **A harness failure was treated as a mathematical judgement.** `_parse`
   returning None became `disposition: reject`. It now becomes `inconclusive`,
   which can never combine into a reject, never changes claim status, and is
   written to `referee/invalid/` so the claim stays refereeable. *No code path
   may turn "the referee did not finish" into "the claim is false."*
2. **The escape screen refused any `/` preceded by whitespace** -- which is
   every Python division, so every analysis script the referee wrote was
   rejected. It burned its turns on refusals. The screen now matches paths, not
   punctuation, and is tested against the fifteen commands the failed run
   actually issued.

What the run did prove: the referees **tried to escape**, ten times on one
claim and six on the other, including `ls -la / && find / -maxdepth 3 -iname
'*chomp*'` -- an explicit hunt for the project directory. Sandboxing was not
paranoia.

Network is now blocked in the sandbox too. The referee prompt asks for a
novelty check, but this repo is public and named for the problem, so a search
for the claim can land on the project itself and hand over every piece of
provenance the box removes. **Novelty is the operator's job**, not the
referee's; treat the `novelty` field of any verdict as unfilled.

Containment is a guardrail, not a boundary: `bash` runs with `shell=True`, and
a determined agent can still enumerate directories. The real fix is running the
job in a container. Until then, read `escape_attempts_blocked` in every verdict.

## 3b. Referee runs 3 and 4: the gate works, the bookkeeping did not

**Run 3** got a pass through for the first time: `t=0.3` returned `accept`,
high confidence, no gaps, after reimplementing the recurrence independently to
`q,r <= 1500`, sweeping the full table to 400, and checking every live row of
the r<=50000 census. `t=0.8` ran out of turns -- being *asked* for a verdict was
not enough, it made another tool call on its last turn. Tools are now withdrawn
on the forced turn, so a reply can only be the verdict.

**Run 4** got both passes through, and **both found the proof correct**:
`t=0.3` "The stated claim is proved correctly... the deficiency is not a gap in
the proof"; `t=0.8` "No gap found". The run nonetheless marked C0012
**refuted**, because the old rule was "disagreement falls to the weaker
verdict" and `accept` != `accept_with_gaps`. A disagreement about whether to
flag a scope caveat became a refutation.

Reverted, and the algebra rewritten: **only an agreed `accept` promotes and only
an agreed `reject` refutes.** Everything else -- a caveat mismatch, a genuine
accept/reject split, any unfinished pass -- leaves the claim exactly as it was.
A split is an open question, not a refutation. There is a regression test over
all nine disposition pairs; every historical failure of this gate now resolves
to "leave it alone".

`novelty_checked` is also no longer set on the strength of "the referee did not
say it was known". The sandbox blocks search, so the referee cannot check
novelty; the flag is only set when a pass actually reports `novel`.

**Standing lesson.** Three of this gate's four failures were the same mistake in
different clothes: treating "the gate did not reach a confident yes" as "the
claim is false". If you touch this code, the invariant is that *only an agreed,
finished, explicit reject may ever mark a claim refuted.*

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

## 2026-09-23: the literature base was missing its most important paper

C0012 was proved, refereed twice, promoted to `proven`, and is **prior art**.
It is stated verbatim in section 8.1 of

  Brouwer, Horvath, Molnar-Saska, Szabo, "On Three-Rowed Chomp",
  INTEGERS 5 (2005) #G07,  https://math.colgate.edu/~integers/fg7/fg7.pdf

one line after the recurrence: *"We see that 1 <= f(q,r) <= q+r+1."*

That paper is where the recurrence in MISSION section 2 comes from, and it was
never in `GROUND_TRUTH/fetch_sources.py`. The project vendored Byrnes,
Zeilberger, Hegarty-Larsson and Brouwer's *webpage*; the webpage does not
state the bound. Nobody read the source paper. Now added to the source list.

**Nothing found a false statement here.** The solver was right, the proof was
right, four adversarial passes were right. Every check the project runs was a
check for *correctness*, and the claim was correct. It was novelty that failed,
and `novelty_checked` sat at `false` on a claim already marked `proven` --
the gate does not look at that field, and neither did I until now.

### The other two overlaps, now resolved

Checked the same day, and the earlier wording here overstated the risk.

- **section 8.4 / 8.6** give the strips empirically, with the constants:
  `alpha = 1 + 1/sqrt(2)` and `beta = 1 + sqrt(2)`, and the bands
  `alpha n - 1.242 < d_n < alpha n + 2.141`, `beta n - 1.506 < q_n < beta n + 1.493`,
  `alpha n - 1.853 < r_n < alpha n + 0.780`. **C0011 already cites and reproduces
  these**, so it was never a novelty failure. Its content is SATURATION (the sup
  stops rising) and the extension to `r = 50000`, neither of which is in #G07.
  Both stand.
  *Attribution:* `alpha` and `beta` are in #G07 (2005), two years before
  Friedman-Landsberg (2007). "The Friedman-Landsberg strips" credits the wrong
  paper for the constants; F-L give the renormalisation derivation of them.
- **section 8.7** heuristics and **8.4/8.6** strips are all about `d_n`, `q_n`,
  `r_n`. **None is `N(r)`, the preperiod**, which #G07 does not treat. So C0003
  is new as a statement -- but it is one more instance of a pattern #G07 already
  documents for three sibling sequences, with a constant in the same family
  (`sqrt(2) = beta - 1`), and should be presented that way.
- **section 8.8** proves `q_n <= 3n - 1` by a counting argument of the same
  flavour as C0012's.

C0003 and C0011 are now `novelty_checked: true`. Twelve `evidence` claims remain
unchecked.

### Standing rule

**Re-check every `novelty_checked: false` claim against #G07 before presenting
any of it as a contribution.** There are 14 such claims, all `evidence`. Read
fg7.pdf first -- it is six pages.

A claim being `proven` says the proof survived the gate. It says nothing
whatsoever about whether the result is new.
