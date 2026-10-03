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
## Session S20261003T0916 findings (do not re-derive)

### The whole target reduces to ONE statement about the mex-generated diagonal (C0046)
`|d_n - alpha n| <= K` for the diagonal `d_n=f(n,n)`, `alpha=1+sqrt(2)/2`. By
complementarity (C0031) + bridge (C0017) this ALONE gives `q_n=beta n+O(1)`,
`r_n=alpha n+O(1)`, and `N(r)=sqrt(2)r+O(1)` on stale rows (C0005, `beta/alpha=sqrt(2)`
exactly). BHMS 8.8's `q_n<=3n-1` is the same argument with the coarse diagonal density
`#diag<=2x/3` (giving `3=1/(1-2/3)`); the sharp `beta=1/(1-1/alpha)` needs
`#diag<=x/alpha` = the open half of #G07 8.12. So the diagonal density bound IS the
whole problem; the method (complementarity + density) is already right in the literature.

### Structural mex reduction (C0045)
`{f(a,n):a<n} = {d_a:a<n} = D_{<n}` EXACTLY (branch (A): `n>a => f(a,n)=f(a,a)=d_a`).
So `d_n = mex(D_{<n} u R_n)`, `R_n={f(n,b):b<n}`, `|D_{<n}|=n`, `|R_n|<=n`. The 2-D
diagonal mex collapses to 1-D + one row term. This is the object to attack.

### Exact block-count identity + almost-monotone diagonal (C0047, C0049)
`c_n := |(R_n\D_{<n}) cap [1,d_n)| = #{constants q_m<d_n} + fdip(n)` EXACT (mex
coverage + C0031; 0/1200 violations). Mex sandwich `d_n = n+1-delta_n+c_n` with
`delta_n=#{a<n:d_a>=d_n}`, `fdip(n)=#{a>=n:d_a<d_n}`. The diagonal is ALMOST-MONOTONE:
`delta_n<=1`, `fdip(n)<=1` for all `n<=5000`; descents are always single-step
(`d_n-d_{n-1}=-1`, 71 in 5000). Strip bound <=> block count `c_n=(sqrt(2)/2)n+O(1)`.
CAVEAT: bounded dips necessary but NOT sufficient (C0026 sorted sets have
delta=fdip=0 yet unbounded discrepancy) -- the mex is the essential selector.

### CORRECTION of the 2026-10-01 dead end: the diagonal HAS a self-similarity cocycle (C0048)
`D_d(x)+D_d(floor(bx))` for the mex-generated diagonal is BOUNDED, no drift
(`[-0.77,2.55]`, slope-vs-log 0.018, to x<=2473/n<=3500). The old dead end's
"drifting [-2.77,-0.42]" was the d_0-EXCLUDED normalisation (offset -1.63); both are
bounded. So C0015 self-similarity + C0045 mex coexist on the SAME object = the correct
Route A setup. NOTE: the cocycle is EQUIVALENT to the strip bound up to O(1) (it is the
strip bound in two-scale form), so it is a REFORMULATION, not a free input. C0020/C0026
stand: cocycle alone does not force bounded discrepancy; the mex must supply it.

## Where this leaves the island
The renormalisation target is now sharply: **prove the mex-generated diagonal has
bounded discrepancy `|d_n-alpha n|<=K`** (= #G07 8.12). Everything else (all three strip
bounds, the preperiod law on stale rows) follows. The pieces in hand: self-similarity
cocycle on the diagonal (C0048), the exact block-count decomposition (C0049), and
almost-monotonicity (dips <=1). The open step is to turn these into a proof that the mex
SELECTS the bounded-discrepancy word (C0026 shows the cocycle admits exponentially many
unbounded-discrepancy words; the mex must exclude them). This is the "rate of convergence
to the fixed point" the charter names; making it rigorous is the remaining work.

### C0050 -- NEGATIVE: the abstract Route A is DEAD; the answer lives in R_n's game structure
The abstract mex `d_n = mex(D_{<n} u R_n)` with `|R_n|<=n` does NOT constrain the slope
or discrepancy: adversarial `R_n = [1,t_n)\D_{<n}` forces any target `t_n` (any slope),
giving `|d_n-alpha n|` UNBOUNDED (explicit 400-step demo: slope 1.807 -> 40, slope 1.4 ->
123; the true alpha=1.707 -> 0.50; all `|R_n|<=n`). The block-count identity (C0049) holds
for EVERY mex-generated sequence (not a discriminator). And any increasing slope~alpha
sequence is mex-realisable (`R_n`=gaps, `|R_n|=d_n-n-1<=n`), so the C0026 cocycle words are
mex-realisable: even mex + cocycle allow unbounded discrepancy. CONCLUSION: NO abstract
renormalisation/mex argument proves the strip bound. The bounded discrepancy is forced ONLY
by the SPECIFIC GAME STRUCTURE of `R_n={f(n,b):b<n}` (the row-n P-position tops). (This
refines C0020/C0026 and kills "Route A" as an abstract combinatorial argument.)

### R_n composition (the real object)
For row n: `|R_n|=n` exactly (b=0..n-1 distinct), `R_n subset [1,d_n)` (ALL row-tops below
the mex), and `R_n` = ~0.707n constants (ALL constants < d_n, by C0049) + ~0.293n diagonal
values. The row tops `f(n,b)` form a staircase: mostly large "diagonal-tracking" values
(roughly consecutive up to d_n) with drops to the constant values at scattered b. The strip
bound <=> `c_n = #{constants<d_n} = (sqrt(2)/2)n + O(1)`, i.e. exactly the count of constants
row n witnesses below its mex. The live attack: find a self-similarity / counting law
SPECIFIC to how the constants are laid out in R_n across n (the real Friedman-Landsberg
renormalisation), not of the diagonal abstractly.

### C0051 -- NEGATIVE: row-profile rescaling is not a renormalisation; BHMS 8.10 is exact
Row profiles `f(n,b)/d_n` do NOT rescale across rows (n vs n/gamma): aligned match only
to staircase variance (~0.15, no preferred gamma) and the normalized CDF is UNIVERSAL
(all rows identical shape, mean|F_n-F_m|~0.001 for every pair incl. controls). So the
charter's "rescaling across r" is NOT row-profile geometry; the genuine self-similarity
is the VALUE-DOMAIN cocycle `D(x)+D(bx)` of the diagonal/stale sets (C0048, rescaling the
value sequence x->bx by b=1+sqrt(2)), not the row picture. DEAD END recorded.

POSITIVE (verified 25/25): BHMS 8.10's exact witness law -- the m-th constant `c=q_m` is
witnessed by EXACTLY m pairs (q,r) with q<c. This is a concrete game constraint on R_n:
each constant has exactly m row-witnesses. Together with C0047 (c_n=#{constants<d_n})
this is the count of constants row n witnesses below its mex, and a candidate counting
input for the R_n self-similarity. Next: combine BHMS 8.10 + C0047 + complementarity to
try to derive the block count c_n=(sqrt(2)/2)n+O(1) from the witness law.

## SESSION S20261003T0916 — FINAL SUMMARY (26 claims C0045-C0070)

**Project status:** primary goal (effective Byrnes, MISSION §4) ACHIEVED via C0028 (verified).
MISSION §5 seed conjecture verified exact (9/9) & saturated (C0069). The bonuses: linear
`N(r)<=C*r` (locking route C0068, -> island 01) and sharp `N(r)=sqrt(2)r+O(1)` (strip bound).

**Sharp strip bound (this lane):** reduced to one statement `|d_n-alpha*n|<=K`, sharp integer form
`|d_n-round(alpha*n)|<=2` (saturated, 0 viol to n=5000). Equivalent to constant density
`#const<x=x/beta+O(1)` and block count `c_n=(sqrt2/2)n+O(1)`. **IRREDUCIBLY HARD on this lane** —
every sub-problem (block count, overlap, almost-increasing delta_n<=1, dip covering) is CIRCULAR
(= the density), and the mex+complementarity loop is EXPANSIVE/NEUTRAL (C0059/C0062) so convergence
cannot force it. All shortcuts CLOSED: abstract mex (C0050), row scaling (C0051), BHMS sharpening
(C0054, circular), local cocycle (C0055), R_n structure (C0056), finite-state (C0058), morphic/word
(C0065), rate-of-convergence (C0062).

**One genuine finding:** the DIP MECHANISM (C0049) — every dip `d_n=d_{n-1}-1` is a row-(n-1) top
dropping out of R_n (universal 0/71 to n=5000). Exact mex-sandwich `d_n=n+1-delta_n+c_n` (C0060).

**Honest corrections (see dead_ends):** "tractable sub-lemma" delta_n<=1 is circular (= density);
"hole identity" is dip-calibrated (circular); rate-of-convergence = the strip bound (circular).

**Next step:** prove the C0037 locking `N(r)-N(r-1)<=6` => `N(r)<=6r` (mission full success) — this
is island 01's MACHINE (no Beatty signature in the increments), genuinely weaker/more tractable than
the strip bound. The sharp strip bound needs a genuinely new non-convergence mechanism. Do NOT
re-derive the closed shortcuts or circular sub-lemmas.

**Confidence:** renormalization thesis (self-similarity => strip bound) is essentially exhausted /
likely dead on this lane (20-yr open problem, no sub-problem is easier). BUT the project succeeds
regardless (primary goal achieved; linear bound via island 01). Contribution = complete map + dip
mechanism + rigorous closure of all wrong turns.
