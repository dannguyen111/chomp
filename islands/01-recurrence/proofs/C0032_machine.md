# C0032 / C0033 — the merged-trail machine and its determinism onset

This file proves two lemmas about Zeilberger's Fundamental Recurrence that
together re-found the preperiod analysis on a *deterministic machine with an
explicit start time*. Both lemmas are exact structural reformulations. **Neither
claims a bound on `N(r)`.**

**Scope: `r >= 1` throughout.** At `(r, a) = (0, 0)` the shift from the
recurrence's mex over positive integers to a mex over non-negative integers
needs `q = r + a >= 1`. There the machine would give `k_0 = mex(∅) = 0`, while
`f(0,0) = 1`. Row 0 is explicit and needs no machine: the mex set at `(q, 0)` is
`{f(a,0) : a < q}`, so induction gives `f(q, 0) = q + 1`. Hence `B_0 ≡ 1`, row 0
is live with period 1, and `N(0) = 0`.

**Convention for stale rows.** For a stale row `c` (finitely many P-positions
`[p, q, c]`, `p >= q`), `N(c)` is `1 +` the last such `q`. The row is constant
from `q0 = N(c) - 1` with value `q0` (C0029, Lemma 1). For `x >= u_c = N(c) - c`
we have `q = c + x > q0`, and `f(q, c) = q0 < q` encodes no P-position with
second row `q`. So `B_c(x)` is **undefined** there, and so is every
`V''_{r,c}` component that evaluates it.

Notation. Fix the third row `r >= 1`. For `c < r`:

```
  B_c(x)   = f(c+x, c) - (c+x)                  (loser coordinate of row c)
  u_c      = N(c) - c                           (row c preperiod, a-coords)
  p_c      = period of row c (p_c := 1 for stale rows)
  q_r      = lcm{ p_c : c < r }
```

Zeilberger's instant winners at `[r, a, .]` decompose as

```
  V''_{r,c}(a) = { B_c(a + r - c) }  if defined, else ∅
  V'_{r,c}(a)  = { B_c(0) - (r-c) - a }  ∩ Z_{>=0}
  W_r(a)       = V''(a) ∪ V'(a),     V''(a) = ⋃_{c<r} V''_{r,c}(a),
                                    V'(a) = ⋃_{c<r} V'_{r,c}(a),
```

and the Fundamental Recurrence is

```
  L_a = mex( W_r(a) ∪ { L_{a-1} - 1, L_{a-2} - 2, ... } ),      (FR)
```

mex over the **non-negative** integers, `L_a = B_r(a)`, `L_a = 0`
terminating the row (stale), all `L_a` defined and `>= 1` for live rows.
Write `dec(X) = { x-1 : x ∈ X, x >= 1 }`.

## C0032 (Lemma M — merged-trail machine)

**Claim.** Define `H_0 := V'(0)` and iterate

```
  k_a = mex( V''(a) ∪ H_a ),      H_{a+1} = dec(H_a) ∪ { k_a - 1 }.    (M)
```

(with the convention that `k_a = 0` terminates). Then, for every `r >= 1`,
`k_a = L_a` and `H_a = V'(a) ∪ T_a` for all `a`, where
`T_a = { L_{a-i} - i : i >= 1 } ∩ Z_{>=0}` is the trail of (FR). Moreover
`H_a ⊆ [0, m_r - 1]` and `k_a <= m_r`, where
`m_r = 1 + max{ B_c(x) : c < r, B_c(x) defined }`. By #G07 section 8.1
(`f(q,c) <= q + c + 1`) every `B_c(x) <= c + 1 <= r`, so `m_r <= r + 1`.

**Proof.** Two independent identities, both one line.

1. `V'(a+1) = dec(V'(a))`. Indeed `V'(a) = { B_c(0)-(r-c)-a : c < r } ∩ Z_{>=0}`
   and `dec` maps the singleton at value `v` to the singleton at `v-1`,
   discarding `v = 0`; that is exactly the `a ↦ a+1` shift of the family.

2. `T_{a+1} = dec(T_a) ∪ { L_a - 1 }` (for `L_a >= 1`; if `L_a = 0` the row
   terminates). Indeed
   `T_{a+1} = { L_{a+1-i} - i : i >= 1 } ∩ Z_{>=0}
            = ( { L_a - 1 } ∪ { L_{a-j} - (j+1) : j >= 1 } ) ∩ Z_{>=0}
            = { L_a - 1 } ∪ dec(T_a)`.

Both families therefore obey the *same* decay rule, so their union
`H_a := V'(a) ∪ T_a` obeys `H_{a+1} = dec(H_a) ∪ { L_a - 1 }`, and (FR)
reads `L_a = mex( V''(a) ∪ V'(a) ∪ T_a ) = mex( V''(a) ∪ H_a )`. With
`H_0 = V'(0) ∪ T_0 = V'(0)` (empty trail at `a = 0`), induction on `a` in (M)
gives `k_a = L_a` at every step. (FR) holds at every `(r, a)` with `r >= 1`,
since then `q = r + a >= 1`. That is why the scope excludes `r = 0`.

*The invariant.* Every element of `V''(a)` is some `B_c(x) <= m_r - 1`. Every
element of `V'(0)` is `B_c(0) - (r - c) <= m_r - 2`, so `H_0 ⊆ [0, m_r - 1]`.
If `H_a ⊆ [0, m_r - 1]`, then `V''(a) ∪ H_a ⊆ [0, m_r - 1]`. Since
`mex(S) <= max(S) + 1`, and `mex(∅) = 0`, this gives `k_a <= m_r`. Then
`H_{a+1} = dec(H_a) ∪ {k_a - 1} ⊆ [0, m_r - 1]`. ∎

**Consequences.** (a) The whole row-`r` dynamics is a deterministic machine
driven by the single input sequence `V''(a)`; the `V'` family needs no separate
handling. (b) The state `(τ; H)` with `τ = a mod q_r` is deterministic as soon
as `V''` is `q_r`-periodic. By the invariant there are at most
`q_r · 2^{m_r}` states `(τ; H)` with `H ⊆ [0, m_r - 1]`.

## C0033 (Lemma S — determinism onset)

**Claim.** For every `r >= 1`, `V''(a)` is `q_r`-periodic for all
`a >= max(σ_r, 0)`, where

```
  σ_r = max_{c<r} N(c) - r =: M_{r-1} - r,      M_{r-1} = max_{c<r} N(c).
```

`N(c)` follows the stale-row convention above. In particular the machine (M)
is autonomous (deterministic given its state and phase) from `a = max(σ_r, 0)`
on.

**What this does not claim.** `σ_r` is defined through the preperiods `N(c)`,
`c < r`. The lemma says *when* the machine becomes autonomous, given those
preperiods. It does not bound them, and it does not bound `N(r)`. It becomes
effective exactly to the extent that a computable bound on `N(c)` is supplied
from elsewhere.

**Proof.** Componentwise. Fix `c < r`. The component `V''_{r,c}(a) =
{ B_c(a + r - c) }` evaluates `B_c` at argument `x = a + r - c`, and `x >=
u_c = N(c) - c` iff `a >= N(c) - r`. On arguments `x >= u_c`, `B_c` is either
`p_c`-periodic (live `c`) or undefined forever (stale `c`); in both cases the
map `a ↦ V''_{r,c}(a)` is `p_c`-periodic on `a >= N(c) - r`. Since `p_c | q_r`,
it is `q_r`-periodic there. Taking the maximum over `c < r` of the thresholds
gives `σ_r = max_{c<r} (N(c) - r) = M_{r-1} - r`. ∎

**Remark (why σ_r, not t_r).** An earlier analysis made `W_r` periodic only
from `a >= max(U_r, r)`, because it waited for the `V'` family to die out
(`a >= r`). Lemma M absorbs `V'` into the state, so only `V''` matters for
autonomy. `V''` becomes periodic at `σ_r`, which is earlier: numerically
`σ_r ≈ (√2 - 1) r`, against `r`.

## Numerical validation

A validation script, run against the solver:

- machine (M) reproduces `f(r+a, r) - (r+a)` exactly for all rows
  `1 <= r <= 300` and all `a` in range, stale rows including their terminating
  `0`. Row 0 is excluded, as in the scope above;
- `V''` is `q_r`-periodic from `a = max(σ_r, 0)` on sample rows, with 0
  failures;
- independently, on a 700 x 700 table built from the recurrence alone (no
  solver): machine (M) equals `B_r(a)` at all 45905 steps over rows
  `1 <= r <= 199`, up to and including each stale row's terminating 0. At every
  step `H_a ⊆ [0, m_r - 1]` and `k_a <= m_r`.
