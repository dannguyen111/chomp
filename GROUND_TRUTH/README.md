# GROUND_TRUTH

The single source of truth for `f(q,r)` (MISSION.md section 2). **Read-only to
explorer sessions.** If you think it is wrong, file a `solver_bug` claim with a
reproducing input; do not patch it.

```
solver.cpp          the solver. streaming, interval-compressed, no O(r^2) table
chomp.py            thin Python wrapper; builds the binary on demand
seed_check.py       regenerates seed_check.md + seed_check.png from a census
seed_check.md       MISSION section 5 tested to r = 50000               <- read this
byrnes_audit.md     where Byrnes loses effectivity, with quotes         <- and this
tests/              25 checks against the literature; run_all.py drives them
tests/data/         vendored reference data + SOURCES.md (provenance)
data/               primary sources; gitignored, refetch with fetch_sources.py
fetch_sources.py    downloads the papers (not committed: the repo is public)
cache/              computed censuses (gitignored; census_50000.tsv = 436 s)
```

## Running it

```bash
python -m GROUND_TRUTH.tests.run_all --max-r 10000        # the full suite, ~55 s
python -m GROUND_TRUTH.tests.run_all --max-r 1000         # quick, ~10 s
python -m GROUND_TRUTH.seed_check                         # regenerate the write-up
python -m GROUND_TRUTH.tests.refresh                      # re-download references

GROUND_TRUTH/solver table  --rmax 24 --qmax 24            # the grid, f[q][r]
GROUND_TRUTH/solver row    --r 120 --qmax 400             # q, f(q,r), f(q,r)-q
GROUND_TRUTH/solver column --r 6541                       # period / preperiod
GROUND_TRUTH/solver census --rmax 50000 --out cache/c.tsv # one line per r
```

`--alpha A --margin M` set the horizon `qmax(r) = A*r + M` (default `1.8r+600`);
`--confirm C` sets how long periodicity must hold before a column is finalised
(default `max(C, r/4)` with `C = 300`). Horizons of `3r`, `4r` and `6r` produce
identical output, so the preperiods are not artefacts of the cutoff.

## How it avoids the O(r^2) table

Three facts, explained at the top of `solver.cpp`:

1. Every column settles by `q ~ 1.5r` — it either goes **stale** (constant
   `< q` forever; finitely many P-positions) or `f(q,r)-q` becomes exactly
   periodic. A settled column answers any later `q` in O(1) and needs no memory.
2. The mex at `(q,r)` needs only the current row, which is being computed left
   to right anyway, plus the column's value *set*, kept as a bitset. No cell is
   read twice, so the table never exists.
3. The values missing from a column's set below `q` are exactly the stale
   constants of the dead columns beneath it. Folding those into the same bitset
   makes it cover an unbroken prefix, so a monotone pointer skips the low range
   and the mex is found by scanning `cov|row` 64 candidates at a time.

`r = 50000` takes 436 s and about 200 MB, against ~1e13 cell visits and tens of
GB for the naive table.

## What it is validated against

25 tests, all passing, in three independent families.

- **The recurrence.** Brouwer's 325 published cells (`r <= q <= 24`), his r=120
  values, his `(r, start, period, pattern)` table, Nivasch's exhaustive period
  census to 10000 (both directions: nothing missing, nothing invented), and the
  trivial rows `r = 0,1,2,3,4,5` that were settled before computers.
- **The sequences.** OEIS A029899, A029900, A029901, A029902, A029903, A029904,
  A029905, A069001, term by term against their b-files, plus the complementarity
  of A029900 and A029901 (Sheiner 2026).
- **The game itself.** An independent brute-force game tree, built from the
  rules with no reference to the recurrence, agreeing with `f` on all 7770
  positions with `p <= 34`, reproducing A069001's Grundy values to `n = 40`, and
  confirming Grundy 0 iff P-position. This is the test that would catch a
  correct implementation of the *wrong object*.
