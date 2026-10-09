# Operator notes

State of play for whoever is driving this, including a future session of me
with no memory of the last one. The *science* lives in `LEDGER/`,
`GROUND_TRUTH/` and the island `NOTES.md`; this file is the *operations* layer:
what has been run, what broke, what to run next, and the conventions that were
learned the expensive way.

Last updated: **2026-10-09**. Sections 0 and the dated sections at the end are
current. Sections 1-5 and the logs before 2026-10-04 are in `OPERATOR_NOTES_ARCHIVE.md`;
the rules they established are condensed under *Standing rules* below.

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

In Claude Code, `/chomp-checkin` (`.claude/skills/chomp-checkin/`) does this and
more: fetch, digest, a Haiku read of the diff, verified red flags, and ranked
next actions. `.claude/CODEBASE_MAP.md` maps the code.

### State at 2026-10-09

- **Proven since 10-05:** C0028 (run 19, recovered from the log) and C0060 (run
  23). C0060 is the mex rule at the diagonal cell, counted out. It is not stated
  in Sheiner or #G07, but it is derivative of them (operator check, ledger
  2026-10-09). Run 23 had overwritten that check with `novelty_checked=False`;
  restored, and `referee.py` no longer clears an operator's flag.
- **C0032 / C0033:** the text rewritten on 10-07 had never been refereed (the
  `unresolved.2` verdicts quote the old text). Run 24 (scheduled, 10-09) is on
  C0032 and a manual run is queued for C0033. Both dropped C0001 from
  `depends_on` on 10-07. Correctly: C0001 is computational evidence, and no
  step of the proof uses it.
- **C0029** is fine at r=1. The proof handles it explicitly (`f(1,1)=3`,
  `f(q,1)=2`, so `N(1)=3`); solver confirms.
- **Budget split 10-09:** `BUDGET.json` is `{cap, spent, calls}` only; per-call
  lines (now with `model`) go to `BUDGET.log.jsonl` (merge=union). `Budget()`
  migrates an inline `log` on first open. BUDGET.json was briefly restored to
  its old shape so run 24, which checked out the old tree, could rebase; the
  next run on new code migrates it once.
- **Referee hardening 10-09:** `novelty.searched` is moved to `_claimed_not_run`
  (the sandbox has no network, and run 23 listed REFUSED queries as searched);
  pass reuse is fingerprinted on solver/tools/model too; a failed final push
  now fails the job and keeps `referee-wip/run-N`. `tests.yml` runs the suite
  on Linux on every code push.

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
- Budget was **$19.39 of $30** at 2026-10-09 ($10.61 left). With explorer
  sessions paused since 10-04, only the referee spends: $0.08-$0.45 a day,
  so weeks of runway, not the 10-11 exhaustion predicted on 09-27. Each
  workflow refuses to start below its own cap, so the loop stops cleanly
  rather than dying mid-proof.

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
  with a blanked ledger and budget, and `git init && git add -A` in the copy
  (the tests call `git ls-files`). `tests.yml` does exactly this on push.
  Individual pure tests can be imported and called.
- A workflow run uses the tree it checked out. A format change pushed while a
  run is in flight (as with the budget split on 10-09) conflicts at its
  rebase. Check `gh run list` before pushing a change to `BUDGET*` or `LEDGER/`.
- **Never hand-edit `LEDGER/claims.jsonl`.** Use `harness/ledger.py`. It is
  append-only and last-entry-per-id wins.
- A `proven` status says the proof survived the gate. It says **nothing** about
  whether the result is new.
- Bash heredocs in this environment **mangle backslashes** (`\\b` arrives as
  `\x08`). For any edit containing regex escapes, use the Edit tool.
- `RemoteTrigger` needs a structured `body` object, not a JSON string.

---

## Standing rules (condensed from the archive)

Each of these cost real money once. Full context in `OPERATOR_NOTES_ARCHIVE.md`.

- **Only an agreed, finished, explicit `reject` may mark a claim `refuted`.** A
  split, a caveat mismatch or an unfinished pass leaves the claim untouched
  (archive s3a, s3b). No code path may turn "the referee did not finish" into
  "the claim is false".
- **Claim statements reach the referee verbatim; keep them provenance-free.**
  Narrative goes in `evidence`. `make_refbox` refuses a leaky submission; use
  `--statement` and record the restatement (s3).
- **Check the sentence, not just the number.** Two errors passed every numeric
  check while the prose around them was false (s3).
- **Novelty is the operator's job.** The sandbox has no network; a verdict's
  `novelty` field is unfilled, and `searched` is cleared by the harness. Read
  #G07 and Sheiner before claiming anything (s3a, 2026-09-23, 2026-09-26).
- **Containment is a guardrail, not a boundary.** Read
  `escape_attempts_blocked` in every verdict (s3a).
- **Caps are soft and wall clock binds first in Actions:** sessions overshoot by
  up to `GRACE_TURNS`; a hosted job dies at 360 min (s3).
- **Durable vs not:** git holds the ledger, proofs, verdicts, workflows,
  harness and budget. `.env` and `GROUND_TRUTH/cache/` (censuses with a
  `# complete` trailer) are gitignored. The refbox and operator context do not
  survive a session (s5).
- Opus pre-screen recipe (`make_refbox --out ... --census ... --statement`,
  two fresh agents, never a fork): archive s2(b).


## 2026-10-04: exploring paused, budget moved to the referee

### Why

Referee runs 13-15 (all MiMo) all went to C0024 and none produced a verdict.
The auto queue took the lowest id first, and inconclusive runs go to
`invalid/` on purpose, so C0024 held the front of the line while seventeen
other refereeable claims waited. The referee has judged two claims ever.

### What changed

- **`session.yml` is disabled** (`gh workflow disable session`). `runs/AUTOPILOT`
  is untouched because it gates both workflows; the referee cron still runs.
  Re-enable with `gh workflow enable session`.
- **Referee harness** (`dcc0354` and the commit after it):
  - `_parse` takes the last JSON object with a `disposition`. The old greedy
    regex broke on any `{...}` set written before the verdict.
  - A pass that ends on an unparseable reply is asked once more, with the
    tools withdrawn. A verdict that still fails records `_finish_reason` and
    `_raw_tail`.
  - `LEDGER/referee/attempts.json` counts runs without a verdict, and the queue
    is ordered by fewest attempts first.
  - An observation whose proof file is a lemma's proof is refereed once, as
    that lemma. 18 eligible claims became 9 proofs.
  - `LEDGER/referee/hold.json` takes a claim out of the queue, with a reason.
- **`referee.yml`** commits and pushes after each claim, and its timeout is now
  350 minutes. (It does not fit six claims: see 2026-10-05.)
- **Referee model stays MiMo**, at Dan's direction.

### Literature review of the 9 proofs

The ledger evidence has the full note for each, under session
`operator-novelty-check`. Sources checked: #G07, Sheiner v2, Zeilberger, Byrnes,
Padhi arXiv:2608.11290v2 section 4 (new, Aug 2026), and the Nowakowski GONC6
unsolved-problems list.

| claim | verdict | queue |
|---|---|---|
| C0024, C0028 | clear: no source gives an effective bound. This is the effective form of Zeilberger's pigeonhole | refereed |
| C0033 | clear | refereed |
| C0032 | reformulation of Zeilberger's Fundamental Recurrence, attributed | refereed |
| C0029 | derivative of #G07 section 8.8, attributed | refereed |
| C0060 | identity clear. **Premise (P) is #G07 section 8.3 = Sheiner Lemma 4.1, so the lemma is unconditional** | refereed |
| C0045 | known: Sheiner recurrence (1) at q=r=n | held |
| C0080 | known: Sheiner Lemma 2.3(a)-(b), #G07 section 8.3 | held |
| C0041 | weaker than C0080, so weaker than prior art | held |

Two side findings:

- **Sheiner Lemma 2.3(b) has NO typo** (corrected 2026-10-04). The PDF prints
  `f(t2,s) ≠ p`, and his Lean has `≠` too. The earlier "printed with `=`"
  note came from a text extraction that drops the slash of `≠`, along with
  `≤`, `∈` and `∪`. Check symbols against the rendered page, never against
  extracted text. The C0080 novelty note in `LEDGER/claims.jsonl` still
  carries the false "a typo" parenthetical. The verdict (KNOWN) stands.
- **Padhi Conjecture 4.6** (bounded-discrepancy quasi-periodicity of the
  diagonal families, rotation numbers in Q(sqrt 2)) is island 02's target,
  stated independently on 247 cells. Our census is far larger, so C0011's
  saturation is evidence for it.

Separately, session 30 rewrote C0003 with `novelty_checked: false`, which
dropped the operator's flag. The note is still in its evidence.

## 2026-10-05: referee runs 16-17, six attempts and no verdict

### What happened

- **Run 16** (manual, 6 claims) finished C0029, C0032, C0033, C0060, all
  `unresolved`, and was cancelled at the 350-minute timeout in the middle of
  C0028. C0024 never ran. Claims take **65-85 minutes**, not 30-50.
- **Run 17** (cron) had a C0028 pass end `inconclusive`, then **failed** in the
  summary step: `KeyError: 'claim'` from reading `attempts.json`. The verdict
  had already been pushed.
- $2.60 spent. The digest said `NEEDS YOU: nothing`.
- The cron started at 18:30Z, not 09:17Z. The three runs before it also started
  5-9 hours late. That is GitHub's scheduler; nothing in the repo causes it.

### Fixed

- `_parse` lost a complete verdict. Run 17's t=0.3 pass wrote valid
  reasoning, but the JSON had unescaped quotes inside a string. The parser now
  retries with stray quotes escaped and marks the verdict `_repaired: true`.
  **Read a repaired verdict before trusting it.**
- `invalid/<id>.<final>.<n>.json`, one file per attempt. Run 17 had overwritten
  run 16's C0028 record. Older files keep their unnumbered names.
- `referee.yml`: the summary step skips `attempts.json` and `hold.json`. The
  loop starts no claim after 260 minutes. Scheduled commits are titled with the
  real target, not `()`.
- `ops/digest.py`: NEEDS YOU now flags failed or cancelled runs (needs `gh`),
  attempts without a verdict, agreed `accept_with_gaps`, and stale holds.

### The proofs

- **C0029, new proof, new bound `N(r) <= 2r+2`.** The old chain also needed
  "A029902 is increasing", i.e. constant-row values increase with the row.
  Neither referee pass caught that it is **unproved**. #G07 s8.11 leaves a
  related question open. The new proof: the freeze value equals the freeze
  point (Sheiner Lemma 2.1), then Sheiner Lemma 4.2 at `q = r+1` plus #G07 s8.1
  gives `c_r <= 2r+1`. It no longer uses s8.8. Still derivative. There is a
  provenance-free restatement in `restatements.json`, and the leak scan of the
  submission is empty.
- **C0028**: Addendum 3 gives the base case: row 0 is `f(q,0) = q+1`, so
  `u_0 = 0` and `u_1 <= 12`. Addendum 2 is rewritten: `a1 >= u_r` follows from
  the minimality of `N(r)`, the suffix keeps least period `p_r`, and the
  well-ordering step is written out.
- **C0032/C0033**: the scope is now `r >= 1`. The machine and (FR) fail only at
  `(0,0)`, and row 0 is explicit. The invariant `H_a ⊆ [0,m_r-1]` is proved, and
  the stale-row `N(c)` convention is stated. C0033 says it claims no bound.
- **C0060**: unconditional. (P) is Sheiner L4.1 + L2.3(a). The mex branch at
  `(n,n)` holds because `d_{n-1} > n-1`, and the `d_a` are distinct by the mex.
  Restated as an identity with no bound, which answers the reject's
  effectivity objection.
- All four got provenance-free restatements and are back in the queue.
- **Effectivity objections to structural lemmas.** The referee prompt applies
  the effectivity trap to every claim. C0033 and C0060 each drew "no computable
  bound", though neither claims one. If that keeps producing rejects, scope the
  rule in `prompts/referee.md` to claims that assert a bound. That is a change
  to the gate, so Dan decides.
- Dispatched 2026-10-06 ~01:49Z: `claim_id=C0029`, then `claim_id=C0028`.
  **Do not queue a third run while one is pending**: a concurrency group keeps
  one pending run, and a new one cancels it.
- The C0080 ledger note no longer calls Sheiner 2.3(b) a typo.


## 2026-10-07: run 21 died mid-claim; referee work is now saved as it goes

### What happened

- **Run 21** (manual, `auto`, 4 claims) refereed C0032 and committed the result
  at 00:27Z. It then worked on its second claim until 02:56Z and died with the
  Referee step still running. The job used about 230 of its 350 minutes, so
  this was not the timeout. GitHub has no log for it (the log API returns 404),
  which is what a lost runner looks like. The likeliest cause is memory: the
  referee's shell commands had no memory cap, and a timed-out command killed
  only its shell, so anything it had started kept running. Claims 2-4 were
  lost, and so was the spend after 00:27, which never reached `BUDGET.json`.
- **Run 22** (scheduled) refereed C0033.
- **C0032 and C0033: second split each**, one accept and one
  accept_with_gaps. The gaps were: (FR) was used without being derived from
  section 2, which also leaves the mex over positives vs. non-negatives
  unexplained; "empty trail at a = 0" was false under the infinite-trail
  definition; `#G07 s8.1` was cited without being a declared dependency; the
  invariant was stated one step past termination; and the `r = 1` convention
  was missing.

### Fixed

- **Proof** (`C0032_machine.md`). (FR) is now derived from section 2 in four
  steps. The only outside input is the stale-row lemma `f(q0,r) = q0`, which
  is the declared dependency C0029. The trail is finite, so `T_0 = ∅` and
  `H_0 = V'(0)` honestly, and the infinite-trail reading is a remark.
  `f(q,c) <= q+c+1` is proved inline (the mex set has at most `q+c` elements),
  so `#G07` is no longer cited. The invariant stops at termination, `r = 1` is
  spelled out, and the claim ids are gone from the headings. Re-checked on an
  independent table built from section 2: 20469 steps, rows 1-132, 0 failures,
  with `{1..q-1} ⊆ S` at every step.
- **Ledger.** C0024 is dropped from C0032's `depends_on`. It was unused and is
  still open, yet the referee was shown it as "already established". The
  C0032 and C0033 restatements get the defined-values and `r = 1` wording.
- **Dependencies are shown restated.** `build_messages` now uses a
  dependency's restatement when one exists. C0029's ledger text, which names
  byrnes_audit.md, was going to the referee verbatim. The leak scan now covers
  the dependency text and no longer flags ids the claim declares. Both claims
  scan clean.
- **Progress is saved as it goes.**
  - `harness/referee.py` writes `LEDGER/referee/progress/<id>.json` after every
    pass, and one transcript line per message to
    `runs/referee/run-<N>/<id>.t<temp>.jsonl`.
  - The workflow pushes these, `BUDGET.json` and a heartbeat (`free -m`, top
    processes) to the side branch `referee-wip/run-<N>` every 5 minutes. The
    snapshot never touches main or the working tree, so it cannot conflict
    with anything.
  - A clean finish deletes the branch.
  - If the job dies, the next job's "Recover dead runs" step
    (`ops/recover_referee.py`) brings back the progress, transcripts, missing
    ledger lines and verdicts, and the unrecorded spend.
  - A rerun of the identical submission (same fingerprint) reuses a finished
    pass. A changed proof starts from scratch.
  - Worst case, a dead runner now loses 5 minutes of work.
- **Sandbox.**
  - Each referee command is capped at 8 GB of address space
    (`CHOMP_SANDBOX_MEM_GB`). The model sees a MemoryError instead of the
    runner dying.
  - A timeout now kills the command's whole process group.
  - Background jobs are reaped at the end of each pass.
- **Digest** flags unfinished progress files and leftover `referee-wip/*`
  branches.

### Still yours

- **Novelty** for C0032 and C0033 cannot be checked from the sandbox. Your
  2026-10-04 review rated C0033 clear and C0032 an attributed derivative.
- Run 21's spend on its second claim is unrecoverable: it ran before
  snapshots existed. `BUDGET.json` undercounts by whatever that was, at most
  the $1.00 per-claim cap. OpenRouter's dashboard has the real figure.
- The claims run 21 never finished are still in the queue.
