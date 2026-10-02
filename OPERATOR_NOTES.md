# Operator notes

State of play for whoever is driving this, including a future session of me
with no memory of the last one. The *science* lives in `LEDGER/`,
`GROUND_TRUTH/` and the island `NOTES.md`; this file is the *operations* layer:
what has been run, what broke, what to run next, and the conventions that were
learned the expensive way.

Last updated: **2026-10-01**. Sections 0 and the dated sections at the end are
current. **Sections 1 and 2 are stale** -- see the note on them.

---

## 0. READ THIS FIRST

### Before anything else: this file is behind the repo

Everything below was verified locally on **2026-09-27**. Autopilot went on that
day, so by the time you read this the crons have been running unattended and
**the remote has commits this file knows nothing about.** First two commands:

```
git pull
python3 ops/digest.py --since '10 days ago'
```

Do not report any status from this file as current without doing that. The
whole recurring failure of this project has been asserting things that were not
checked; do not let the handoff be the next instance.

### The loop is autonomous as of 2026-09-27

| when (UTC) | what | cap | where |
|---|---|---|---|
| 03:17 | `session.yml` -- one explorer session, islands alternate | $1.50 | Actions |
| 09:17 | `referee.yml` -- auto mode, 1 claim | $0.75 | Actions |
| 13:00 | daily digest emailed to sidan.nguyen@gmail.com | free | Claude routine |

- **Off switch:** delete `runs/AUTOPILOT` and push. One file, both workflows,
  effective next cron. Manual `workflow_dispatch` ignores it.
- `:17` not `:00` deliberately -- GitHub's scheduler queues hardest on the hour.
- Both workflows share the `chomp` concurrency group, so a long session queues
  the referee instead of racing it on the ledger.
- Scheduled runs pin their own caps; **manual dispatch uses the old $5.00/$1.00
  defaults.** The gate branches on `github.event_name == 'schedule'`. If you ever
  drive these from an external cron (cron-job.org etc.) you will silently get the
  manual caps and bypass `runs/AUTOPILOT` -- pass `inputs` explicitly.
- Digest routine: `trig_01P8MeN3FDkBPRfW1xcHq6Wk`. It runs `ops/digest.py` and
  follows `ops/DIGEST_PROMPT.md`; both are in the repo so they can be fixed
  without touching the routine.
- Budget was **$5.2492 of $30** at 2026-09-27T21:14Z, burning ~$1.72/day, so it
  should exhaust around **2026-10-11**. Each workflow refuses to start below its
  own cap, so the loop stops cleanly rather than dying mid-proof.

### The single most important fact

**C0012 is `proven` AND it is prior art.** `f(q,r) <= q+r+1` is stated verbatim
in Brouwer-Horvath-Molnar-Saska-Szabo, *On Three-Rowed Chomp*, INTEGERS 5 (2005)
**#G07 section 8.1**, one line after the recurrence it introduces. Therefore
**(Z1) was discharged in 2005** and the project's first proven claim is a
restatement.

Root cause: #G07 was never in `fetch_sources.py`. The project vendored Byrnes,
Zeilberger, Hegarty-Larsson and Brouwer's *webpage* -- which does not state the
bound -- but not the paper the recurrence comes from. Both #G07 and Sheiner are
in the source list now. **Read them before claiming anything about `f(q,r)`.**

Nothing found a false statement here: the solver, the proof and all four
adversarial passes were right. *Novelty* failed, and `novelty_checked` sat at
`false` on a claim already marked `proven`. The gate never looks at that field.

### Novelty status

Checked: **C0003, C0006, C0011, C0012, C0017**. Roughly **16 unchecked**, all
`evidence`. C0013, C0022 still need Sheiner read against them.

- **C0011 is the best candidate contribution.** #G07 section 8.12 says proving
  `d_n, r_n ~ alpha n` and `q_n ~ beta n` suffices for opening-move uniqueness.
  Sheiner (2026) proved uniqueness by a *different* route and explicitly does
  not establish those asymptotics, so **they are still open**, and C0011's
  saturation is strictly stronger than them. Proving it closes 8.12's second
  half.
- **#G07 section 8.2 is WRONG.** It claims period 25 at r=782 and period 720 at
  r=7751. Both are below r=10000 where Nivasch's census (which Brouwer endorses
  on his own page) finds only periods 2,3,4,9 and lists neither row. Our solver:
  r=782 is live with period 1, r=7751 is stale. Pinned by
  `test_nivasch.py::test_fg7_period_claim_is_wrong`. **26 tests pass.**
- Attribution: `alpha = 1 + 1/sqrt(2)` and `beta = 1 + sqrt(2)` are in #G07
  (2005), two years before Friedman-Landsberg. "The Friedman-Landsberg strips"
  credits the wrong paper for the constants.

### The referee gate: fixed, but not trustworthy

Runs 6 and 7 **could not reach a verdict at all.** The sandbox refused the
referee permission to write a verification script, so it argued from unchecked
premises and rejected C0021 twice at *high* confidence on two different wrong
objections (run 6: claimed `(3r-1)+m+n != p+q+r-1`, which are identically equal;
run 7: claimed the bound holds only when `q=r`, refuted by (5,3,2)).

`harness/tools.py` now allows scratch writes under `/tmp` -- network and
filesystem-sweep blocks untouched. Pinned by
`test_sandbox_allows_scratch_but_not_escape`.

**Run 8, after the fix:** both passes returned a verdict for the first time in
three attempts, at half the cost ($0.27). t=0.3 **accepted at high confidence
with the correct argument**. t=0.8 rejected at *medium* confidence on **scope** --
the claim bounds values, not the preperiod -- which is a real distinction and not
a defect in C0021.

**But its `first_gap_line` is a fabricated quotation.** It cited a sentence that
is verbatim from C0009 (superseded) and appears **nowhere in the 13,217-character
prompt** -- verified by rebuilding the box and searching six fragments of it.
The referee rejected on evidence it was never given. Mechanism unknown; do not
guess at one.

Consequence: a fabricated objection can only *block* a claim, never promote a
false one, because promotion needs an agreed accept. `final=unresolved` left
C0021 `open`, correctly. **Read the digest when anything reaches `proven`.**

### Sheiner 2026, and the Lean question

**Erez Sheiner, "Unique Winning Opening Move in Three-Row Chomp", arXiv:2605.23837**
(v2 2026-06-09). Read in full; nothing of ours is subsumed. Three things of his
to use: Lemma 2.3(a) (for fixed `q`, `f(q,0..q)` are distinct), Lemma 4.1
(`f(q,q)` is the column max, hence `> q`), and confirmation his `B(q,r)`
decomposition matches our recurrence including closed forms and tight cells.
His Lemma 4.1 pairs with #G07 8.1 to sandwich `q+1 <= f(q,q) <= 2q+1`, both ends
attained for `q <= 400`.

His acknowledgements say the proof was **"fully formalized and machine-verified
in the Lean 4 proof assistant, using only its standard library."** That is the
exact base layer -- well-definedness of `f`, the two-branch recurrence, `mex`,
well-foundedness -- that makes formalizing anything else here cheap, and it is
**not linked in the paper**.

**An email asking for it was sent to erez@math.biu.ac.il on 2026-09-27** (by the
operator, from sidan.nguyen@gmail.com). It also offered the #G07 8.2 erratum and
the independent check of his two lemmas. **If a reply has arrived, that changes
the Lean plan -- check before rebuilding the base layer.**

Standing view on Lean: worth it, but **not for C0012** (prior art, so it buys
rigor on a known result). It is for the base layer plus whatever the real
theorem turns out to be. The target `N(r)` bound is far too big to formalize on
this budget.

### Open work, in priority order

1. **Write THE THEOREM.** The result is scattered across 23 ledger entries and
   two proof files; nobody can read it. One island-01 session chaining the
   recurrence -> C0012 -> C0021 -> the corrected state count into one statement
   with one proof file. Build it on C0011/C0013, not on C0012.
2. **C0013's closed form is wrong.** Per C0023(c) the Zeilberger state count
   omits the preperiod `a_0(r)`, so the correct form is
   `N(r) + period(r) <= a_0(r) + p_r (M_r+1)^(M_r)` -- a **recursion over r**,
   not the displayed closed form. It must be restated and unrolled before
   `2^(2^r poly(r))` means anything.
3. **Novelty-check the remaining ~16**, #G07 and Sheiner in hand.
4. **The 5-item referee eval**, if the gate misbehaves again. Build it from this
   project's own real errors: C0012 and C0021 as-is must be accepted; C0009's
   `n = p-q` slip, C0012's old "all 402 tight cells on row r=0" line, and
   C0013's missing `a_0(r)` must be rejected. ~$2 per model. Three of those
   errors actually fooled someone.
5. C0021 needs no further referee runs -- it is redundant to #G07's published
   `q+r+1`, which is sharper than its `3r-1`.

### Gotchas that cost real time

- `test_harness.py` **pollutes the ledger and charges the budget** -- it appends
  claims, writes a corrupt line and a fake handoff. Run it in a throwaway copy
  with a blanked ledger. Individual pure tests can be imported and called.
- **Never hand-edit `LEDGER/claims.jsonl`.** Use `harness/ledger.py`. It is
  append-only and last-entry-per-id wins.
- A `proven` status says the proof survived the gate. It says **nothing** about
  whether the result is new.
- Bash heredocs in this environment **mangle backslashes** (`\\b` arrives as
  `\x08`). For any edit containing regex escapes, use the Edit tool.
- `RemoteTrigger` needs a structured `body` object, not a JSON string.

---

## 1. Where things stand

> **STALE -- 2026-09-21. Kept for the record; see section 0 for current state.**
> The status table below has since been corrected in place, but the surrounding
> prose predates referee runs 3-8, the novelty audit, and autopilot.

**Budget: $2.72 of $30 spent. $27.28 left.** All of it on OpenRouter; the Opus
pre-screens were billed to the Claude plan instead.

| | |
|---|---|
| Repo | `github.com/dannguyen111/chomp`, public |
| Ledger | 26 lines, 21 active |
| Proven | **C0012** -- and it is prior art (#G07 section 8.1). See the novelty note. |
| Refereeable now | C0021 only (`lemma` + proof file); it has survived 3 runs unresolved |
| Autopilot | **ON** since 2026-09-27 -- see `runs/AUTOPILOT`, which is the off switch |
| Cron | session 03:17 UTC daily (cap $1.50); referee 09:17 UTC daily (cap $0.75, 1 claim) |

Sessions run so far:

- **S20260920T2126** (island 01) -- 47 turns, $0.50, 93% cache. Produced C0012
  but logged **zero** claims; results were stranded in handoff prose and
  recovered by hand.
- **S20260921T0215** (island 02) -- 130 turns, $2.15, 97% cache. Logged
  C0014-C0020 correctly. Killed by the GitHub job timeout, not by its own
  limit; state survived only because `Commit state` has `if: always()`.

## 2. The next two things to run

> **OBSOLETE -- 2026-09-21. Both have happened.** The referee has run eight
> times, not zero; the Opus pre-screen ran and found a real error (the 402
> tight-cell attribution). This section's title is actively wrong and it is kept
> only because the reasoning in it explains why the gate was designed the way it
> was. For what to run next, see section 0.

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

## 2026-09-23 (later): two more things the source list was missing

### A 2026 paper works in our exact recurrence

Erez Sheiner, "Unique Winning Opening Move in Three-Row Chomp",
arXiv:2605.23837, v1 2026-05-22, v2 2026-06-09. Now in `fetch_sources.py`.

It proves every 3xn Chomp rectangle has exactly one winning opening move,
settling the three-row case of Gale's 52-year-old question -- which is
**#G07 section 8.12's "most interesting" open problem** -- working directly in
Brouwer's `f(q,r)`. Its tool is a *rightmost-hole principle* on the sets
`C(q,r)`, and it yields a partition of the positive integers by A029900 /
A029901.

**Nobody on this project has read it.** It is the most recent work on the exact
object we are studying and it is four months old. Two specific exposures:

- its A029900 / A029901 partition is adjacent to **C0017** (the claimed bridge
  `A029902(n) = f(n,n)`);
- its rightmost-hole principle is a structural fact about `C(q,r)`, which is
  the same set C0012's counting argument bounds.

### C0011 is better than we thought

#G07 8.12 says proving `d_n, r_n ~ alpha n` and `q_n ~ beta n` suffices for
uniqueness. Sheiner got uniqueness *without* those asymptotics and does not
establish them, so **the asymptotics are still open**. C0011's saturation is
strictly stronger than them. It is not a reproduction of Brouwer's table; it is
empirical evidence on a published open problem, and proving it would close the
second half of 8.12.

### Revised standing rule

Read #G07 **and** arXiv:2605.23837 before claiming anything. The lesson of
C0012 was not "check novelty at the end" -- it was that the project spent two
days building on a recurrence whose source paper it had never opened.

## 2026-09-26: Sheiner arXiv:2605.23837, read in full

Ten pages. What it does, and what it means for us.

### What it proves

Theorem 1.1: every `[n,n,n]` has exactly one winning opening move. The route is
Prop 4.4 -- the positive integers partition into `D = {f(a,a)}` and
`S = {p : f(p,r)=p for some r<p}`, i.e. **A029900 and A029901 are
complementary**. That is precisely the conjecture #G07 section 8.6 states and
leaves open. So Sheiner closed it.

### Nothing of ours is subsumed

- **C0012** (`f(q,r) <= q+r+1`) is NOT in Sheiner. Its prior art remains #G07
  section 8.1 alone.
- **C0017** is clear. Sheiner partitions A029900 / A029901 as SETS; C0017 is a
  quantitative `O(1)` relation between A029902(n) and `f(n,n)`, different
  sequences and a different kind of statement. He gives no asymptotics or O(1)
  relations anywhere.
- **C0011** is untouched, as already recorded: he gets uniqueness without the
  alpha/beta asymptotics, so #G07 8.12's second half stays open.

### What he has that we should use

- **Lemma 2.3(a): for fixed `q`, the values `f(q,0),...,f(q,q)` are distinct.**
  A clean structural fact we never stated.
- **Lemma 4.1: `f(q,q) = max_r f(q,r)`, and `f(q,q) > q`.** This is Brouwer's
  section 8.3 made rigorous, and the `> q` comes from distinctness: `q+1`
  distinct positive integers force a maximum of at least `q+1`. It is a LOWER
  bound on the diagonal, exactly complementary to C0012's upper bound. Our
  proof file for C0012 should cite it as the matching side.
- His `B(q,r) = R(q,r) u C(q,r)` agrees with our recurrence: his
  `f(a,min(a,r))` for `a < r` is our branch (A). His closed forms
  `f(q,0)=q+1`, `f(1,1)=3`, `f(q,1)=2 (q>=2)`, `f(q,2)=q+2 (q>=2)` match the
  solver, including the `(1,1)` tight cell C0012 documents.

### The line that matters most for us

> "As an independent check, the proof has been fully formalized and
> machine-verified in the Lean 4 proof assistant, using only its standard
> library."

Someone has already formalized this recurrence in Lean 4 with mathlib alone:
well-definedness of `f` (his Lemma 2.1), the two-branch recurrence, the mex,
distinctness, diagonal maximality. That is the exact base layer we costed at
roughly a day, and it is the part that makes C0012 and C0021 cheap once it
exists.

**The development is not linked in the paper** -- the only URLs are Brouwer's
page and the two OEIS entries. So it is either unpublished, an ancillary file,
or available on request. Worth asking the author before rebuilding it.
