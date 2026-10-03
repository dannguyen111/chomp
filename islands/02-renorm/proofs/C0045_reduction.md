# C0045 / C0046 — Reduction of the whole renormalisation target to the mex-generated diagonal

Throughout, `f` is the recurrence of MISSION §2. Notation (BHMS / OEIS):

* `d_n = f(n,n)` — the diagonal, **A029900**, conjectured `d_n = alpha n + O(1)`,
  `alpha = 1 + sqrt(2)/2 = (2+sqrt(2))/2`.
* `q_n` — the constant-row values, **A029901**, conjectured `q_n = beta n + O(1)`,
  `beta = 1 + sqrt(2)`.
* `r_n` — the stale-row indices, **A029902**, conjectured `r_n = alpha n + O(1)`.
* `D_{<n} = {d_a : 0 <= a < n}` (the diagonal values before index `n`; `d_0 = f(0,0) = 1`).

Two exact algebraic facts (used freely, checked symbolic):
`alpha*beta = alpha + beta` (Beatty pair: `1/alpha + 1/beta = 1`) and
`beta/alpha = sqrt(2)`, `1 - 1/alpha = 1/beta`, `2*alpha - 1 = beta`.

---

## C0045 (lemma) — Structural mex reduction of the diagonal

**Claim.** For every `n >= 1`,

```
   { f(a,n) : 0 <= a < n }  =  { d_a : 0 <= a < n }  =  D_{<n}          (exact)
```

and consequently

```
   d_n = f(n,n) = mex( D_{<n}  u  R_n ),      R_n := { f(n,b) : 0 <= b < n }.
```

**Proof.** The recurrence's branch (A) (`r > q` gives `f(q,r)=f(q,q)`) applies to
`f(a,n)` whenever `n > a`. For `0 <= a < n` we have `n > a`, so `f(a,n) = f(a,a) = d_a`.
Taking the set over `0 <= a < n` gives `{f(a,n):a<n} = {d_a : a<n} = D_{<n}`. The
recurrence's mex branch for `f(n,n)` is over `{f(a,n):a<n} u {f(n,b):b<n}`; substituting
the first set gives `d_n = mex(D_{<n} u R_n)`. No monotonicity of `d_n` is used or
implied. This is a one-line consequence of branch (A); verified against the solver
table for all `n <= 60`.  (In particular the 2-dimensional mex defining the diagonal
collapses to the 1-dimensional set `D_{<n}` plus a single row term `R_n`.)

---

## C0046 (observation) — Reduction: one diagonal strip bound implies everything

**Claim.** Assume the **diagonal strip bound**

```
   (DSB)      | d_n - alpha*n |  <=  K      for all n, some explicit K.
```

Then each of the following follows rigorously (using only C0005, C0017, C0031):

1. `#{ d_m <= x } = x/alpha + O(1)` (diagonal counting function, both halves);
2. `q_n = beta*n + O(1)`  (the A029901 strip bound, both halves);
3. `r_n = alpha*n + O(1)`  (the A029902 strip bound, both halves);
4. `N(r) = sqrt(2)*r + O(1)` for every **stale** row `r` (Conjecture N on stale rows).

**Proof.**

(1) From `|d_m - alpha m| <= K`: `d_m <= alpha m + K` gives `#{d_m <= alpha m + K} >= m`,
and `d_m >= alpha m - K` gives `#{d_m <= x} <= (x+K)/alpha`. Together
`#{d_m <= x} = x/alpha + O(1)`.

(2) Complementarity (C0031): `{d_m}` and `{q_n}` partition the positive integers
except 1. Hence for all `x`, `#{q_n <= x} = x - #{d_m <= x} + O(1)`. By (1) this is
`x - x/alpha + O(1) = x/beta + O(1)` (since `1 - 1/alpha = 1/beta`). Inverting,
the `n`-th constant satisfies `n = q_n/beta + O(1)`, i.e. `q_n = beta*n + O(1)`.

(3) The bridge (C0017): `r_n = d_n + O(1)`. By DSB `d_n = alpha n + O(1)`, so
`r_n = alpha n + O(1)`.

(4) C0005: for a stale row `r = r_n`, `N(r) = q_n + 1`. By (2), `q_n = beta n + O(1)`,
and by (3) `n = r_n/alpha + O(1)`. So
`N(r_n) = beta n + O(1) = beta*(r_n/alpha) + O(1) = (beta/alpha) r_n + O(1) = sqrt(2) r + O(1)`
because `beta/alpha = sqrt(2)` exactly.

Thus a single inequality `|d_n - alpha n| <= K` on the mex-generated diagonal delivers
the entire Friedman–Landsberg strip picture and the preperiod law on stale rows. The
three independent-looking strip bounds in the literature are one statement about the
diagonal. Live rows are not covered by (4) (they need the period machinery, C0024/C0028);
the reduction is exact for the stale rows, which are `59%` of all rows.

---

## Why this is the right place to attack (localisation)

BHMS §8.8 proves `q_n <= 3n - 1` by showing "at least `n` constants `c <= 3n-1`".
Via complementarity this is exactly the diagonal **density upper bound**
`#{d_m <= x} <= (2/3) x + O(1)`: the constant `3 = 1/(1 - 2/3)`. The sharp constant
`beta = 1/(1 - 1/alpha)` would follow from the conjectured `#{d_m <= x} <= x/alpha + O(1)`.
So the whole gap between BHMS's `3` and the sharp `beta` is the diagonal density bound
`1/alpha` versus `2/3`; and that density bound is precisely the still-open half of
#G07 §8.12. The method (complementarity + density) is already correct in the literature;
only the diagonal density input is missing, and it is missing because it *is* the target.

Equivalently (C0045): `d_n = mex(D_{<n} u R_n)` with `|D_{<n}| = n`, `|R_n| <= n`, so
`d_n - 1 = |D_{<n} u R_n \cap [1,d_n)| = n + |(R_n \ D_{<n}) \cap [1,d_n)| - delta_n` where
`delta_n = #{a<n : d_a >= d_n}` is the dip deficit (bounded, `d_n` is not monotone).
The DSB `d_n = alpha n + O(1)` is therefore *equivalent* to the row-top count
`|(R_n \ D_{<n}) \cap [1,d_n)| = (alpha-1) n + O(1) = (sqrt(2)/2) n + O(1)`. Measured
count `-(alpha-1)n` over `n <= 400`: bounded in `[-1.26, 1.05]` (mean `0.06`). So the
renormalisation target is exactly: **the number of non-diagonal row-`n` tops below the
diagonal mex grows like `(sqrt(2)/2) n` with `O(1)` error.** This is a purely combinatorial
counting statement about the mex, the natural handle for the self-similarity/mex attack.

---

## C0049 — Exact block-count identity (proof)

**Claim.** With `c_n = |(R_n \ D_{<n}) \cap [1,d_n)|`, `fdip(n) = #{a>=n : d_a < d_n}`,
`delta_n = #{a<n : d_a >= d_n}`:

```
   c_n = #{constants q_m < d_n} + fdip(n)        (EXACT)
   d_n = n + 1 - delta_n + c_n                   (EXACT, mex sandwich)
```

**Proof of the identity.** By the mex, `[1, d_n) subseteq D_{<n} u R_n` and
`d_n notin D_{<n} u R_n`. Take `v in [1,d_n)`. Every integer is a diagonal value
`d_a` or a constant (complementarity C0031).

* If `v = d_a` with `a < n`, then `v in D_{<n}` (removed by `\ D_{<n}`).
* If `v = d_a` with `a >= n`, then `v notin D_{<n}`, so mex coverage forces
  `v in R_n`; thus `v in R_n \ D_{<n} \cap [1,d_n)`, and it is counted by `fdip(n)`.
* If `v` is a constant, `v notin D_{<n}`, so coverage forces `v in R_n`; thus
  `v in R_n \ D_{<n} \cap [1,d_n)`, counted by `#{constants < d_n}`.

Conversely any `v in R_n \ D_{<n} \cap [1,d_n)` is `<d_n`, not in `D_{<n}`, hence a
constant or a future-dip diagonal; both cases are counted above. So the two counts
match exactly. (Uses only mex coverage + C0031; no monotonicity of `d_n` needed.)

**Mex sandwich.** `d_n - 1 = |[1,d_n) \cap (D_{<n} u R_n)| = |{a<n: d_a<d_n}| + c_n`
`= (n - delta_n) + c_n`, giving `d_n = n + 1 - delta_n + c_n`.

**Bounded dips (evidence).** To `n<=3500` (solver table): `delta_n<=1`, `fdip(n)<=1`,
`d_n` has only `50` single-step descents (`d_n - d_{n-1} = -1`). So the diagonal is
almost-monotone. CAVEAT: necessary, not sufficient (C0026 sorted sets have
`delta=fdip=0` yet unbounded discrepancy); the mex remains the essential selector.
Substituting the identity into the sandwich is circular (returns `d_n=d_n`); the
strip bound still needs the diagonal density `#{d_a<=x}=x/alpha+O(1)`, which is
the open content of #G07 8.12.
