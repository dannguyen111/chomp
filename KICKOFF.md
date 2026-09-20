# KICKOFF — paste this into Claude Code

Run Claude Code in the directory containing `chomp-harness.zip`, then paste
everything below the line. This is Phase 0. It costs nothing but subscription
tokens — no OpenRouter calls happen here, and you should not create an API key
until Phase 0 reports back.

---

You are setting up a research harness. Work autonomously through the whole
checklist and only stop at the two STOP points. Do not ask me to confirm
intermediate steps.

**Do not call any external paid API. Do not create or use an OPENROUTER_API_KEY.
This entire task is local computation.**

## Step 1 — Unpack and verify

Unzip `chomp-harness.zip`, `cd chomp`, `pip install requests`, then run
`python test_harness.py`. All eight tests must pass. If any fail, fix the
harness before continuing. Read `MISSION.md` in full — it is the spec for
everything below.

## Step 2 — Build the solver

Create `GROUND_TRUTH/`. Implement the Brouwer recurrence from MISSION.md §2 for
3-row Chomp:

```
f(q,r) = f(q,q)                                        if r > q
f(q,r) = f(q-1,r)                                      if f(q-1,r) < q
f(q,r) = mex{ f(a,r) : a<q } ∪ { f(q,b) : b<r }        otherwise
```

The naive table is O(n²) cells, which is hopeless at the ranges that matter.
Rows become eventually constant or eventually linear, so store **intervals, not
cells**. Target: `r ≤ 50,000` in a few GB. C++ with a thin Python wrapper.
Expose a CLI that can dump a row, dump the period/preperiod for a row, and run
a census over a range of r.

## Step 3 — Validate (non-negotiable)

The solver is the only thing preventing the agents from believing false lemmas.
Write `GROUND_TRUTH/tests/` checking all of:

- Brouwer's small table of `f(q,r)` for `q,r ≤ 24` (fetch from
  https://aeb.win.tue.nl/games/chomp.html)
- OEIS A029899, A029900, A029901, A029902, A029903, A029904, A029905, A069001
  (fetch the b-files)
- The r=120 anomaly: for large q, `f(q,120) = q + const + (−1)^q`, first
  deviating from linear at q=170
- Nivasch's period census to r=10,000: the published period-2, period-3,
  period-4 lists, and period 9 occurring exactly at r=6541 and r=8767
- Trivial cases: 2×n P-positions are exactly (a+1,a); r=2 P-positions have p−q=2

Every one must pass. A solver that disagrees with the literature anywhere is a
solver that will silently poison the whole project.

## Step 4 — Test the seed conjecture

MISSION.md §5 conjectures that `N(r)/r → √2`, where `N(r)` is the preperiod. I
derived this from nine published data points. **Verify or kill it.**

Compute `N(r)` for every r with a non-trivial period in Nivasch's census
(~200 values, r ≤ 10,000), then extend as far as your machine allows. Report:
the ratio distribution, whether it tightens with r, whether it differs by period
class, and any r that breaks it. Write this to `GROUND_TRUTH/seed_check.md` with
a plot.

If the conjecture fails, say so plainly and do not soften it. A dead seed
conjecture found for free in Phase 0 is a good outcome; discovering it after
spending $12 of explorer sessions is not.

## Step 5 — Literature audit

Read Byrnes' poset game periodicity proof and Zeilberger's exposition of it
(`https://sites.math.rutgers.edu/~zeilberg/mamarim/mamarimPDF/byrnes.pdf`).
Identify **the specific step where effectivity is lost** — the pigeonhole,
compactness or minimal-criminal argument that yields existence without a
computable bound. Write `GROUND_TRUTH/byrnes_audit.md` naming that step,
quoting it, and stating precisely what would have to be made quantitative.

This is the single most valuable artifact in Phase 0. If you find it, it saves
an entire explorer session, and both islands start from a sharp question instead
of a vague one.

## Step 6 — Seed the ledger

Append the Phase 0 findings to `LEDGER/claims.jsonl` using `harness/ledger.py`
(do not hand-edit the file). Everything from Step 4 is `type: observation`,
`status: evidence`, with an honest `verified_range`. Nothing from Phase 0 is
`proven` — only the referee promotes. Update `islands/01-recurrence/NOTES.md`
and `islands/02-renorm/NOTES.md` with what each island should know at start.

## STOP 1 — report to me

Post a summary: test results, max r reached and runtime, the √2 verdict, the
Byrnes gap you found, and what you seeded into the ledger. **Wait for my go.**

## Step 7 — after I say go

I will create an OpenRouter key and export it. Then run exactly one session:

```
SESSION_CAP=3.00 ./run.sh 01-recurrence
```

Watch the `cache=` column. If it is not above 80% by turn three, kill the run —
something is churning the cached prefix and every turn is costing full price.

## STOP 2 — transcript autopsy

When the session ends, read `runs/<id>/transcript.jsonl` end to end and tell me:
what the explorer wasted tokens on, whether it stayed on its island thesis,
whether the handoff is specific enough to start from, and what you would change
in `prompts/explorer.md`. Propose the diff. **Do not spend more budget until I
approve it.**

## Step 8 — prepare the repo for the cloud

Read `CLOUD.md`. Run `git init`, add a `.gitignore` for `__pycache__/` and
`GROUND_TRUTH/solver` (the binary is cached by Actions, not committed), and make
the initial commit. Then verify that `.github/workflows/*.yml` reference only
paths that now exist: the solver source at `GROUND_TRUTH/solver.cpp` and the
test runner invoked as `python -m GROUND_TRUTH.tests.run_all --max-r N`. If your
Phase 0 layout differs, fix the workflow to match rather than renaming your code.

Finally, print the exact commands I need to create the remote, push, and add the
`OPENROUTER_API_KEY` secret. Do not create the remote or push yourself.
