# C0060 — Exact mex-sandwich identity (rigorous, one isolated game premise)

## Setup

For the mex-generated diagonal `d_n = f(n,n)` (C0045):
`d_n = mex(D_{<n} u R_n)` where `D_{<n} = {d_a : 0<=a<n}` and `R_n = {f(n,b) : 0<=b<n}`.

Define:
* `delta_n = #{a<n : d_a >= d_n}`  (number of earlier diagonal values not below `d_n`);
* `c_n = | (R_n \ D_{<n}) \cap [1,d_n) |`  (new row tops below the mex).

## Single game premise (P)

**(P)** For every `n`, `R_n \subseteq [1, d_n)`, i.e. `f(n,b) < f(n,n)` for all `b<n`.

(P) is a game monotonicity (every row-`n` P-position top with third coordinate `b<n` lies
strictly below the diagonal top `f(n,n)`). It is **verified with 0 violations for all
`n <= 2500`** against the validated solver. It is *not* a consequence of the mex alone
(the mex permits elements of `R_n` above `d_n`); it is a property of the game and is the
one input this lemma takes on trust. Everything else below is exact.

Also used: `|R_n| = n` and the `f(n,b)` are pairwise distinct (`0<=b<n`), verified 0
violations to `n<=2500`; and mex coverage `[1,d_n) \subseteq D_{<n} u R_n` (definitional).

## Lemma (exact mex sandwich)

**Under (P):** for every `n>=1`,

```
   d_n  =  n + 1 - delta_n + c_n .                              (EXACT)
```

### Proof

Since `d_n = mex(D_{<n} u R_n)`, by definition of mex:
1. `d_n \notin D_{<n} u R_n`, and
2. `[1, d_n) \subseteq D_{<n} u R_n`.

Count `[1,d_n)`, which has `d_n - 1` elements. By (P), `R_n \subseteq [1,d_n)`, so
`D_{<n} u R_n` intersected with `[1,d_n)` splits as the disjoint union of
`D_{<n} \cap [1,d_n)` and `(R_n \ D_{<n}) \cap [1,d_n)`. By (2) their union is all of
`[1,d_n)`, so

```
   d_n - 1  =  |D_{<n} \cap [1,d_n)|  +  |(R_n \ D_{<n}) \cap [1,d_n)|
           =  (n - delta_n)  +  c_n .
```

Here `|D_{<n} \cap [1,d_n)| = #{a<n : d_a < d_n} = n - delta_n`, and the second term is
`c_n` by definition. Rearranging gives `d_n = n + 1 - delta_n + c_n`. All steps are
counting identities under (P) and mex coverage. QED.

## Corollary (strip bound reformulation)

Since `delta_n, c_n >= 0` and (empirically) `delta_n <= 1`, `fdip(n) <= 1` (C0049), the
diagonal strip bound `d_n = alpha*n + O(1)` is **equivalent** to the block count
`c_n = (alpha-1) n + O(1) = (sqrt(2)/2) n + O(1)`. The identity is exact and reduces the
strip bound to a pure count of non-diagonal row tops below the mex.

## Status

The identity is **rigorous conditional on (P)**. (P) is verified to `n<=2500` (0
violations) and is a clean game monotonicity, but is NOT proved here. If (P) is proved
independently (it should follow from the P-position structure / BHMS 8.11-type row
monotonicity), this becomes an unconditional exact lemma. The boundedness of `delta_n`
and `c_n`'s slope is the open content (= C0052 strip bound).
