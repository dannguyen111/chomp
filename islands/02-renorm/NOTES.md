# Island 02 -- renormalization attack

Phase 0 findings you should not re-derive. Backed by
`GROUND_TRUTH/seed_check.md` and `GROUND_TRUTH/byrnes_audit.md`.

## Your target is sharper than "explain sqrt(2)"

The seed conjecture (MISSION section 5) survived and came back much stronger:

```
    -3.1565  <=  N(r) - sqrt(2) r  <=  5.6959      for every 1 <= r <= 50000
```

`N(r) - floor(sqrt(2) r)` takes only ten values, `-3..6`; 99.4% of rows land in
`{0,1,2,3}`; the supremum of `|N(r) - sqrt(2) r|` stops increasing after
`r = 26475` and is unchanged from 30000 to 50000. So `N(r) = sqrt(2) r + O(1)`,
not `+ o(r)`.

**And the `sqrt(2)` is not a fact about the interesting rows.** It holds just as
tightly on the period-1 rows and on the stale rows, which together are 98.2% of
all rows. The nine points tabulated in MISSION section 5 are all period `>= 2`
only because those are the rows worth publishing.

## Where the sqrt(2) actually comes from -- this is your lever

Rows split into two complementary families with the Friedman-Landsberg
reciprocal densities:

```
   stale rows (A029902):  29289/50000 = 0.585780   vs  1/a = 0.5857864,  a = 1 + sqrt(2)/2
   live  rows          :  20711/50000 = 0.414220   vs  1/b = 0.4142136,  b = 1 + sqrt(2)
```

For a **stale** row the link is an exact identity, not a statistical one. The
census confirms `N(r) = dconst + 1` for all 29289 stale rows, and `(r, dconst)`
is precisely `(A029902(n), A029901(n))`. Since `b = sqrt(2) a` **exactly**,

```
   N(r) - sqrt(2) r  =  A029901(n) + 1 - sqrt(2) A029902(n)
                     =  1 + eps1(n) - sqrt(2) eps2(n)
```

where `eps1`, `eps2` are the deviations of those two sequences from their lines.
Brouwer reports (below `n = 130000`) `eps1 in [-1.506, 1.493]` and
`eps2 in [-1.853, 0.940]`, predicting `N - sqrt(2) r in [-1.835, 5.114]`;
observed on the stale rows here: `[-0.124, 3.497]`. Consistent and tighter.

**So on the majority of rows, Conjecture N is not an independent conjecture. It
is equivalent to an explicit strip bound.** The target is therefore:

> Prove `|A029902(n) - a n| <= K` for an explicit computable `K`, with
> `a = 1 + sqrt(2)/2`. (Equivalently for A029901 about `b n`, `b = 1 + sqrt(2)`.)

That single bound delivers **(B1)** of `GROUND_TRUTH/byrnes_audit.md` -- the one
quantity Byrnes' proof leaves uncomputable -- and hence an effective Byrnes.

---

## Session S20260921T0215 findings (do not re-derive)

### 1. H&L is a statement of the target, not a route (C0014)
Hegarty-Larsson Theorem 3.3 gives only the asymptotic density (L, l), **no error
term**: its proof says the convergence rate "is determined by M+, M-, S and the
choice of starting point N only" and "We omit any further details". Their
**Conjecture 5.1 is exactly our strip bound**, stated OPEN. So the Phase 0
pointer does not pay out directly. The only place an error term could come from
in their machinery is the Mobius-iteration contraction (Lemma 3.2), whose rate
kappa_n is not bounded below.

### 2. The strip bound = bounded discrepancy (C0016)
With `D(x) = #{A029902 <= x} - x/a`, the identity `A029902(n) - a n = -a D(A029902(n))`
holds exactly (since `#{A029902 <= A029902(n)} = n`). So

> `|A029902(n) - a n| <= K` for all n  ⟺  `|D(x)| <= K/a` for all x.

Measured: `D(x) in [-0.8710, +1.0855]` over all `x <= 50000`, saturating
(unchanged from x = 30000 to 50000). The whole job reduces to proving bounded
discrepancy of A029902 about slope `1/a`. This is the cleanest statement of the
target yet.

### 3. Exact self-similarity of the discrepancy (C0015) — the live lever
The Friedman-Landsberg self-similarity holds in **exact** form:

```
   D(x) + D(b x)  in  {-1, 0, 1}     for every integer x with b x <= 50000
```

equivalently `#{A029902 <= x} + #{A029902 <= b x} = 2x + {-1,0,1}`, with
`b = sqrt(2) a = 1 + sqrt(2)`. This is the renormalization fixed point the
picture predicts, but as an *O(1)* statement rather than an asymptotic one. The
density part (`~ x/a + bx/a = 2x`) is trivial; the content is that the error is
bounded by 1. This is the single most promising lever: a self-similarity of the
discrepancy is exactly the kind of input a discrepancy bound follows from.

### 4. Bridge to the diagonal (C0017)
`A029902(n) = f(n,n) + O(1)` with `A029902(n) - f(n,n) in {-3..1}` (mode -2),
and `A029901(n) = 2 A029902(n) - n + O(1)` (correction in {-1..3}). Since
`2a - 1 = b` exactly, this is the algebraic source of `b = 1 + sqrt(2)` from
`a = 1 + sqrt(2)/2`. The stale rows and the diagonal are the *same* sequence up
to O(1), so a strip bound on either gives the other.

### 5. The word is chaotic, not Sturmian (C0018) — negative result
The indicator word `w(n) = [n is a stale constant]` has essentially maximal
factor complexity (c(k) reaches min(2^k, N-k+1) by k~40). It is **not**
Sturmian/balanced/morphic-of-low-complexity. So the bounded discrepancy does NOT
come from any low-complexity structure. The "chaos" in Zeilberger's title is
real: bounded discrepancy coexists with maximal subword complexity.

## Where this leaves the island

The target is now a **bounded-discrepancy theorem about a single set** A029902
(equivalently A029901), with the exact self-similarity `D(x) + D(bx) in {-1,0,1}`
as the structural input. Two concrete routes are visible:

- **Route A (self-similarity → discrepancy bound).** The relation
  `D(x) + D(bx) in {-1,0,1}` is a functional equation on D. Combined with
  `D(x) - D(x-1) = [x in A029902] - 1/a` and the fact that D is piecewise-linear
  with slope `-1/a` and jumps `+1`, this may pin D to a bounded set directly
  (a self-similarity + boundedness argument, no Beatty/morphic assumption).
- **Route B (diagonal bridge).** `A029902(n) = f(n,n) + O(1)` means the strip
  bound is equivalent to a strip bound on the diagonal `f(q,q) ~ a q`, which is
  the object Byrnes' Lemma 5 already bounds linearly (`f(r,r) <= 4r-1`). The
  diagonal recurrence `f(q,q) = mex({f(a,q):a<q} u {f(q,b):b<q})` is a self-map
  that might be contractive in the strip metric.

Route A is the one most faithful to this island's charter and most likely to
produce a constant. Judge any approach by whether it can produce a *constant*;
abandon early if it only yields density.

## Settled tension with MISSION

`LEDGER/mission_disputes.md` records, and the project owner has approved, that
the primary line of attack is the one in `GROUND_TRUTH/byrnes_audit.md`
section 3. For this island that means the strip bound above is the target, not
a side quest. Do not spend tokens relitigating it.

## Using the solver

Never modify `GROUND_TRUTH/`. File a `solver_bug` claim with a reproducing input.

```
GROUND_TRUTH/solver census --rmax 20000 --out /tmp/c.tsv
python -m GROUND_TRUTH.seed_check --census GROUND_TRUTH/cache/<your census>.tsv
```

`GROUND_TRUTH/cache/` is restored from the phase0 Actions cache (recomputing
r=50000 costs 436 s). Columns:
`r, class, period, N, dvals, deathq, dconst, qend`. For stale rows `dconst` is
the `A029901` value and `r` is the `A029902` value, so the two sequences are one
`awk` away. Horizons of `3r`, `4r`, `6r` give identical output -- these are not
artefacts.

Other measured constants, free for the taking: `f(r,r) = a r + O(1)` with
`f(q,q) - a q in [-1.153, +2.050]` for `q <= 2000` (Brouwer: `[-1.310, +2.141]`
below 130000); `max_q (f(q,r) - q) = (sqrt(2)/2) r + O(1)`.

## Scratch code

`islands/02-renorm/scratch/diag_solver.py` -- self-contained Python solver for
`f(q,r)` (O(n^2) memory, n <= ~3000), validated against the table. Useful for
diagonal/mex experiments without touching GROUND_TRUTH.
`GROUND_TRUTH/data/` holds the fetched papers (pypdf installed; extract with
`pypdf.PdfReader(...).pages`).

## Session S20260929T0957 findings (do not re-derive)

### 1. Beatty-perturbation reformulation of the strip bound (C0025)
A029902/A029901 (and the live rows) are BOUNDED PERTURBATIONS of the
complementary Beatty pair (floor(a n), floor(b n)) with a=1+sqrt(2)/2,
b=1+sqrt(2), 1/a+1/b=1:
- r_n - floor(a n) in {-1,0,1} for ALL n <= 29289 (sup of |r_n - floor(an)| = 1).
- p_n - floor(b n) in {-1,0,1,2}; live_n - floor(b n) in {-2..2} (99.97% in {-1,0,1}).
Since |r_n - a n| <= |r_n - floor(a n)| + 1, the strip bound reduces to proving
|r_n - floor(a n)| <= 1, a nearest-integer formulation. Max |r_n - a n| = 1.853
exactly reproduces Brouwer's strip. This is a cleaner target than real-slope
discrepancy: it is about an integer sequence staying within 1 of a Beatty floor.

### 2. The cocycle is exponentially weak (C0026) -- Route A is dead at word level too
Exhaustive enumeration of all 0-1 words satisfying the exact cocycle
N(x)+N(floor(bx))=2x+e(x), e in {-1,0,1}: solution count grows exponentially
(1288 / 11696 / 105550 / 1286320 / 11993136 at K = 12/16/20/24/28) and
max|D| over ALL solutions grows (3.03 -> 4.60) while the true word has |D|<=0.9.
So the self-similarity alone does not even narrow the word to a small class.
The mex/greedy generation is the only selecting input (consistent with C0020).

## Where this leaves the island
Two new handles:
- **Nearest-integer Beatty formulation (C0025):** prove r_n = floor(a n) + O(1)
  with the O(1) actually ={-1,0,1}. This is a classic "bounded perturbation of a
  Beatty sequence" statement and may be attackable by the known machinery for
  Beatty sequences / Sturmian return words (note: the WORD is chaotic C0018, but
  the perturbation of the VALUE sequence may still be tractable).
- **Encode the greedy mex rule as prefix-sum constraints** and re-run the
  backtracking (islands/02-renorm/scratch/cocycle_maxdisc.py). If the solution
  set collapses under the mex constraint, that is evidence the greedy rule is
  sufficient; if not, a new counterexample is found (kill test, cheap).

The single best next step is the mex-constraint augmentation of the cocycle
backtracking: test whether greedy-mex + cocycle forces |D| bounded. The mex rule
for the stale rows is exactly the 3-row recurrence restricted to diagonal
P-positions (f(q,q) = mex({f(a,q):a<q} u {f(q,b):b<q})); via C0017,
A029902(n) = f(n,n)+O(1), so r_n is directly mex-generated.

Scratch: islands/02-renorm/scratch/{structure.py, cocycle_exact.py,
cocycle_maxdisc.py, cocycle_findmax.py, cocycle_heuristic.py,
cocycle_search.py}; /tmp/t3000.txt = diagonal f(q,q), q<=3000.

## Session S20261001T1016 findings (do not re-derive)

### 1. (B1) IS CLOSED by published prior art: N(r) <= 3r for stale rows (C0029)
The single gap (B1) in `byrnes_audit.md` -- an explicit K(r) bounding the last
P-position of a stale row -- is closed by **BHMS §8.8**, which proves
`q_n <= 3n-1` for the constant-row values `q_n = A029901(n)`. Chain:
`N(r_n) = q_n + 1 <= 3n <= 3 r_n` (using `r_n >= n`). So `N(r) <= 3r` for all
29289 stale rows, equality only at r=1. This is PROVED, not conjectural: the
ingredient is in print. The audit's own section 3 lists `3r` as acceptable but
did not notice BHMS already supplies `q_n <= 3n-1`. Proof:
`islands/02-renorm/proofs/C0029.md`.

### 2. Numerically N(r) <= 3r for ALL rows, N(r) <= 2r for r >= 2 (C0030)
Over all 50001 rows to r=50000: N(r) <= 3r with equality only at r=1 (N=3);
N(r) <= 2r for all r >= 2. Stale rows: proved (C0029). Live rows (20712):
observed, max N/r = 1.7273 at r=11. A uniform closed-form bound N(r) <= 3r is
now proved for ~59% of rows and conjectural/observed for the rest.

### 3. A029900 and A029901 are exactly complementary (C0031, prior art Sheiner Prop 4.4)
The diagonal `d_n = f(n,n)` (A029900) and the constant-row values `q_n`
(A029901) are disjoint and together cover all positive integers except 1 (the
poison). Verified to n=3000: complement of {d_1..d_3000} in [1, d_3000] equals
A029901 terms <= d_3000 exactly (0 overlap, 0 gaps). This is the algebraic
backbone: the diagonal is mex-generated, A029901 is its complement, and the
strip bound on A029902 (r_n) is equivalent to a strip bound on the
mex-generated diagonal.

### 4. Dead ends this session
(a) The diagonal discrepancy `D_d(x)=#{d_n<=x}-x/a` has NO clean self-similarity
cocycle (measured drift [-2.77,-0.42], not {-1,0,1}); the cocycle C0015 is a
property of the STALE SET A029902, not the raw diagonal.
(b) The "overlap identity" `d_n = 2n+1-overlap_n` for the diagonal mex is false
(fails at n=52); the mex is genuinely 2-dimensional and the dip structure
(d_n-d_{n-1}=-1 at 43 places <=3000) breaks the naive count.

## Where this leaves the island (updated)

The renormalisation/strip-bound target remains open for the *sharp* constant
(`N(r) ~ sqrt(2) r`), but the *effectivity* target (any computable K(r)) is now
**closed for stale rows** by C0029, and numerically supported for all rows by
C0030. The remaining gaps for a complete closed-form bound on ALL rows are:
- **(live rows):** prove N(r) <= 3r (or any linear bound) for live rows. The
  Zeilberger route needs (Z1) [closed: C0021 gives p-q <= 3r-1] and (Z2)
  [lcm of periods below r, still open]. Alternatively a direct argument for
  live rows analogous to BHMS §8.8.
- **(Z2):** bound lcm{period(c) : c < r}. Observed periods {1,2,3,4,6,8,9},
  lcm 72, to r=50000. A bound like lcm <= 2^{O(r)} or even a polynomial would
  give a complete effective Byrnes.

The sharp strip bound |A029902(n)-a n| <= K remains the "renormalisation"
prize and is still open; C0029 shows it is NOT needed for effectivity (a cruder
3r bound already closes B1). The island should now weigh: (i) close live rows
by a direct argument (cheap, completes the closed form), vs (ii) continue the
renormalisation route for the sharp constant (harder, the original charter).