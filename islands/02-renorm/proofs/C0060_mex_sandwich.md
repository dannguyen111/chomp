# Exact mex-sandwich identity for the diagonal (unconditional)

## Statement

Let `d_n = f(n, n)`, `D_{<n} = {d_a : 0 <= a < n}` and
`R_n = {f(n, b) : 0 <= b < n}`. Define

* `delta_n = #{a < n : d_a > d_n}`, the number of earlier diagonal values above
  `d_n`;
* `c_n = |(R_n \ D_{<n}) ∩ [1, d_n)|`, the number of values in column `n` below
  the diagonal that are not earlier diagonal values.

Then for every `n >= 1`,

```
   d_n  =  n + 1 - delta_n + c_n .                              (EXACT)
```

This is an exact identity. It asserts **no bound** and makes no effectivity
claim. It rewrites `d_n` as a count, so that a bound on `d_n` and a bound on
`c_n - delta_n` are the same question.

## Inputs (in print)

- **(Rec)** The recurrence, MISSION.md section 2 (#G07 section 8.1).
- **(S4.1) Sheiner, arXiv:2605.23837, Lemma 4.1 = #G07 section 8.3.** For every
  `q >= 0`, `f(q, q)` is the largest of `f(q, 0), ..., f(q, q)`, and
  `f(q, q) > q`.
- **(S2.3a) Sheiner, Lemma 2.3(a).** For fixed `q`, the values
  `f(q, 0), ..., f(q, q)` are pairwise distinct.

## Step 1: the diagonal cell is a mex cell, with mex set `D_{<n} ∪ R_n`

Fix `n >= 1`. The first branch of (Rec) needs `r > q`, which fails at `(n, n)`.
The second branch would need `f(n-1, n) < n`. But `f(n-1, n) = f(n-1, n-1) =
d_{n-1}` by the first branch, since `n > n-1`, and `d_{n-1} > n-1` by (S4.1).
So `d_{n-1} >= n` and the second branch does not fire. Therefore `d_n` is the
mex of

```
{f(a, n) : a < n}  ∪  {f(n, b) : b < n}.
```

For `a < n`, the first branch gives `f(a, n) = f(a, a) = d_a`, so the first set
is `D_{<n}`. The second set is `R_n`. Hence `d_n = mex(D_{<n} ∪ R_n)`, which
means:

1. `d_n ∉ D_{<n} ∪ R_n`, and
2. `[1, d_n) ⊆ D_{<n} ∪ R_n`.

## Step 2: the two side facts

- **The `d_a` are pairwise distinct.** By Step 1(1), `d_n ∉ D_{<n}` for every
  `n >= 1`, so each diagonal value differs from all earlier ones. In particular
  `|D_{<n}| = n`, and `d_a ≠ d_n` for `a < n`. So
  `#{a < n : d_a < d_n} = n - delta_n`, with `delta_n` counting the strict
  inequality `d_a > d_n`, which is the same as `d_a >= d_n` here.
- **(P) `R_n ⊆ [1, d_n)`.** By (S2.3a) the values `f(n, b)`, `b < n`, differ
  from `f(n, n) = d_n`. By (S4.1) none of them exceeds `d_n`. So each is
  `< d_n`, and each is `>= 1` because `f` is a positive integer.

## Step 3: the count

Count `[1, d_n)`, which has `d_n - 1` elements. By Step 1(2) it is covered by
`D_{<n} ∪ R_n`. Split it into the elements in `D_{<n}` and the elements in
`R_n \ D_{<n}`. These parts are disjoint, and by (P) every element of `R_n` lies
in `[1, d_n)`. So

```
d_n - 1  =  |D_{<n} ∩ [1, d_n)|  +  |(R_n \ D_{<n}) ∩ [1, d_n)|
         =  #{a < n : d_a < d_n}  +  c_n
         =  (n - delta_n)  +  c_n,
```

the middle step using distinctness of the `d_a` (Step 2). Rearranging gives
`d_n = n + 1 - delta_n + c_n`. ∎

## Remark (not part of the claim)

`delta_n, c_n >= 0`, so the identity turns any bound on `d_n - n` into a bound
on `c_n - delta_n`, and back. Numerically `delta_n <= 1` throughout the range
checked. Nothing here proves that.

## Verification (numerical, evidence not proof)

On a 500 x 500 table built from the recurrence alone (no solver), for every
`1 <= n < 500`: `d_{n-1} >= n`, `|R_n| = n` with `max R_n < d_n`,
`|D_{<n}| = n`, and the identity holds exactly. Earlier runs against the solver
covered `n <= 2500` with no violations.
