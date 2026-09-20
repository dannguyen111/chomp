# Provenance of the vendored reference data

Everything in this directory was downloaded on **2026-09-20** and is committed
so the test suite runs offline, in CI, and byte-identically a year from now.
`python -m GROUND_TRUTH.tests.refresh` re-downloads and rewrites it; if that
produces a diff, something upstream changed and the diff is the news.

| file | source | contents |
|---|---|---|
| `brouwer_table_24.txt` | `https://aeb.win.tue.nl/games/chomp.html`, section "A small table" | 325 cells of `f(q,r)`, `r <= q <= 24`, one line per `r` |
| `r120_pvalues.txt` | same page, section "3-by-n Chomp" | `f(q,120)` for `q = 120..255`, the 136 values Brouwer prints |
| `nivasch_periods.json` | same page, Gabriel Nivasch's quoted census | every `r <= 10000` of period 2 (141), 3 (7), 4 (54), 9 (2) |
| `brouwer_patterns.json` | same page, "Patterns in 3-by-n Chomp" | 19 rows of `(r, start, period, pattern)` |
| `oeis/A0299xx.txt`, `oeis/A069001.txt` | `https://oeis.org/<id>/b<nnn>.txt` | OEIS b-files |

Raw copies of the fetched HTML and PDFs live in `GROUND_TRUTH/data/` and are not
used by the tests.

## Caveats found while fetching

- **The b-files for A029900 through A029905 are synthesised**, not authored:
  their header says "b-file synthesized from sequence entry", so they contain
  only the ~20-65 terms shown in the OEIS entry. A029899 (401 terms) and
  A069001 (2522 terms) are real b-files.
- **A029901's stated offset is 1 but its synthesised b-file is 0-indexed.**
  `common.oeis()` reads the file, so the tests index it from 0. A029902 through
  A029905 and A029899 are 0-indexed too; A069001 is 1-indexed.
- Brouwer's `(r, start, period, pattern)` table gives the pattern as a deviation
  from the mean, so `test_brouwer_pattern_table` compares normalised patterns
  (each minus its own minimum) rather than raw `d` values. The `start` column is
  compared exactly and is not normalised.
- Brouwer's error-term strips for A029901/A029902 are indexed from `n = 1`.
  Reproducing them requires the same convention.

## Identifications used by the tests

Each is verified term by term in `test_oeis.py`, not assumed:

```
  A029899(n) = #{P-positions (p,q,r) with p <= n}
  A029900(q) = f(q,q)
  A029901    = sorted { p : (p,p,r) is a P-position }  = the stale constants
  A029902    = sorted { r : (p,p,r) is a P-position }  = the r whose rows die
  A029903    = c, A029904 = q0, A029905 = r, over those r with
               f(q,r) = q + c for all q >= q0  (live rows of period 1;
               r = 120 is deliberately absent, its row has period 2)
  A069001(n) = Grundy value of the 3 x n rectangle
```
