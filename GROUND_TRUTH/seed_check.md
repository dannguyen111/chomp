# Seed check: is `N(r)/r -> sqrt(2)`?

Verdict up front: **the conjecture survives, and it is far too weak.** 
`N(r)` is not merely `sqrt(2) r + o(r)`; over every one of the **50000 rows with `1 <= r <= 50000`** the error is bounded:

```
    -3.1565  <=  N(r) - sqrt(2)*r  <=  5.6959        for all 1 <= r <= 50000
```

attained at r = 25550 and r = 26475.  Equivalently `N(r) - floor(sqrt(2) r)` takes only the values [-3, -2, -1, 0, 1, 2, 3, 4, 5, 6], and 98.4% of rows land in `{0,1,2,3}`.

So the project's target -- *any* explicit computable bound on `N(r)` -- is numerically supported at `N(r) <= sqrt(2) r + 6` and with enormous room to spare at `N(r) <= 2r`.  **Effectivity, not sharpness, is the whole difficulty.**


## 1. Method

`N(r)` is read off the solver's census: the least `q0` such that `f(q,r) - q` is exactly periodic for all `q >= q0`, computed online as `1 + max{q : d(q) != d(q+pi)}` for the minimal eventual period `pi`.

Census file: `GROUND_TRUTH/cache/census_50000.tsv` (r <= 50000).  The solver is validated by `GROUND_TRUTH/tests/` against Brouwer's 325-cell table, eight OEIS sequences, the r=120 anomaly and Nivasch's full period census; every one of the nine `(r, start)` pairs in MISSION.md section 5 is reproduced exactly.


**Horizon robustness.** Each column is finalised at `q = 1.8r + 600` once periodicity has held for `max(300, r/4)` steps.  Re-running with horizons of `3r`, `4r` and `6r` and confirmation windows up to 2000 changes **no** `N(r)`, period or pattern (0 differences for r <= 6000 at 6r, and for r <= 20000 at 3r).  The preperiods are not horizon artefacts.


## 2. The ratio distribution

| r-band | rows | mean N/r | sd N/r | mean N-sqrt2 r | min | max |
|---|---:|---:|---:|---:|---:|---:|
| 1-99 | 99 | 1.466367 | 0.186878 | +0.946 | -0.912 | +3.603 |
| 100-399 | 300 | 1.419132 | 0.005370 | +1.067 | -0.975 | +4.356 |
| 400-999 | 600 | 1.415908 | 0.001633 | +1.099 | -1.710 | +4.702 |
| 1000-2999 | 2000 | 1.414799 | 0.000607 | +1.056 | -1.060 | +5.300 |
| 3000-9999 | 7000 | 1.414405 | 0.000193 | +1.120 | -0.984 | +5.406 |
| 10000-24999 | 15000 | 1.414279 | 0.000066 | +1.069 | -1.435 | +5.647 |
| 25000-49999 | 25000 | 1.414244 | 0.000029 | +1.087 | -3.157 | +5.696 |

The mean tracks `sqrt(2) = 1.414214` and the spread falls like `1/r`: the sd drops ~6450x from the 1-99 band to the 25000-49999 band while `r` grows ~743x -- exactly the signature of a bounded numerator, not of `o(r)` drift.


## 3. Does it tighten? Yes, and the sup saturates

| r <= | sup abs(N - sqrt2 r) |
|---:|---:|
| 10 | 2.3431 |
| 100 | 3.6030 |
| 1000 | 4.7023 |
| 5000 | 5.3004 |
| 10000 | 5.4061 |
| 20000 | 5.6467 |
| 30000 | 5.6959 |
| 40000 | 5.6959 |
| 50000 | 5.6959 |

The supremum stops moving well before the end of the range.  If `N(r) - sqrt(2) r` were unbounded -- even logarithmically -- this column would keep climbing; it does not.


## 4. Does it differ by period class? Barely, and not in the mean

| class | rows | mean N/r | sd N/r | min N-sqrt2 r | max N-sqrt2 r |
|---|---:|---:|---:|---:|---:|
| stale | 29289 | 1.414594 | 0.010838 | -0.124 | +3.497 |
| p1 | 19787 | 1.414251 | 0.003913 | -3.157 | +5.696 |
| p2 | 675 | 1.414213 | 0.000169 | -1.640 | +4.440 |
| p3 | 29 | 1.414260 | 0.000146 | -0.554 | +4.418 |
| p4 | 212 | 1.414346 | 0.000590 | -1.435 | +4.686 |
| p6 | 1 | 1.414281 | 0.000000 | +0.739 | +0.739 |
| p8 | 3 | 1.414175 | 0.000024 | -1.249 | -0.387 |
| p9 | 4 | 1.414194 | 0.000036 | -0.410 | +0.669 |

The nine published points in MISSION.md are all period >= 2 rows, of which there are 924 below r = 50000.  **The `sqrt(2)` law is not a property of that class** -- it holds just as tightly for the period-1 rows and for the `stale` rows (those with only finitely many P-positions), which together are 98.2% of all rows.  Conditioning on the period was an artefact of which rows happen to be interesting enough to publish.


## 5. Rows that break it: none, and here is why

| | r | class | period | N(r) | N - sqrt2 r |
|---|---:|---|---:|---:|---:|
| min | 25550 | p1 | 1 | 36130 | -3.1565 |
| min | 31235 | p1 | 1 | 44170 | -2.9606 |
| min | 458 | p1 | 1 | 646 | -1.7098 |
| max | 44560 | p1 | 1 | 63023 | +5.6437 |
| max | 19457 | p1 | 1 | 27522 | +5.6467 |
| max | 26475 | p1 | 1 | 37447 | +5.6959 |

### Where the `sqrt(2)` actually comes from

The rows split into two complementary families whose densities are the Friedman-Landsberg reciprocals:

```
  stale rows (A029902):  29289 / 50000  =  0.585780   vs  1/a = 0.585786,  a = 1 + sqrt(2)/2
  live  rows          :  20711 / 50000  =  0.414220   vs  1/b = 0.414214,  b = 1 + sqrt(2)
```

For a **stale** row the connection is exact rather than statistical. The census confirms `N(r) = dconst + 1` for all 29289 stale rows, and `(r, dconst)` is precisely the pair `(A029902(n), A029901(n))`.  Since `b = sqrt(2) a` **exactly**,

```
  N(r) - sqrt(2) r  =  A029901(n) + 1 - sqrt(2) A029902(n)
                    =  1 + eps1(n) - sqrt(2) eps2(n)
```

where `eps1, eps2` are the deviations of those two sequences from their lines.  Brouwer reports (for n below 130000) `eps1 in [-1.506, 1.493]` and `eps2 in [-1.853, 0.940]`, which predicts `N - sqrt(2) r in [-1.835, 5.114]`; observed over the stale rows here: `[-0.124, 3.497]`.  Consistent, and tighter.


**This is the payload for the islands.** For the ~59% of rows that are stale, Conjecture N is not an independent conjecture at all: it is *equivalent* to an explicit strip bound for A029901 and A029902 about their Friedman-Landsberg lines. An effective Byrnes bound on those rows needs exactly one thing -- a computable constant `K` with `|A029902(n) - a n| <= K` -- and nothing about periodicity. The live rows obey the same law with the roles of `a` and `b` swapped (`r ~ b n`, `N ~ sqrt(2) b n = (2+sqrt(2)) n`), but there the analogous strip bound is *not* in the literature; A029903/A029904/A029905 carry no published error term.


## 6. Period spectrum (new data beyond the published census)

| period | rows (r <= 50000) | rows (r <= 10000, Nivasch) |
|---:|---:|---:|
| 1 | 19787 | 3938 |
| 2 | 675 | 141 |
| 3 | 29 | 7 |
| 4 | 212 | 54 |
| 6 | 1 | 0 |
| 8 | 3 | 0 |
| 9 | 4 | 2 |

Periods outside Nivasch's published set `{2,3,4,9}` first occur above r = 10000: `r=11036` (period 6), `r=18718` (period 8), `r=28109` (period 8), `r=46110` (period 8).  These are not in the literature.


## 7. Verdict

**Conjecture N is alive and understated.** It should be replaced in the ledger by the stronger and more useful form:

> `N(r) = sqrt(2) r + O(1)`, with `|N(r) - sqrt(2) r| < 5.70` verified for all `1 <= r <= 50000`.


Two warnings against over-reading it:

1. This is numerics, not proof.  MISSION.md section 7: numerical agreement is evidence, never proof.  The bound is logged as `type: observation`, `status: evidence`.
2. The `sqrt(2)` is *downstream* of the Friedman-Landsberg constants `a = 1 + sqrt(2)/2` and `b = 1 + sqrt(2)`, which are themselves derived from unproven scaling assumptions.  Proving `N(r) = sqrt(2) r + O(1)` by way of those constants would be proving the harder thing first.  A crude effective bound such as `N(r) <= 100 r`, proved directly from the mex structure, is worth more to this project than a sharp one that assumes the renormalisation picture.

