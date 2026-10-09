# The merged-trail machine and its determinism onset

This file proves two lemmas, Lemma M and Lemma S, that together re-found the
preperiod analysis on a *deterministic machine with an explicit start time*.
Both are exact structural reformulations of the recurrence of MISSION section 2,
which is derived below in the form (FR) they use. **Neither claims a bound on
`N(r)`.**

**Scope: `r >= 1` throughout.** At `(r, a) = (0, 0)` the shift from the
recurrence's mex over positive integers to a mex over non-negative integers
needs `q = r + a >= 1`. There the machine would give `k_0 = mex(∅) = 0`, while
`f(0,0) = 1`. Row 0 is explicit and needs no machine: the mex set at `(q, 0)` is
`{f(a,0) : a < q}`, so induction gives `f(q, 0) = q + 1`. Hence `B_0 ≡ 1`, row 0
is live with period 1, and `N(0) = 0`.

**Convention for stale rows.** For a stale row `c` (finitely many P-positions
`[p, q, c]`, `p >= q`), `N(c)` is `1 +` the last such `q`. The row is constant
from `q0 = N(c) - 1` with value `q0` (the cited stale-row lemma). For
`x >= u_c = N(c) - c` we have `q = c + x > q0`, and `f(q, c) = q0 < q` encodes no P-position with
second row `q`. So `B_c(x)` is **undefined** there, and so is every
`V''_{r,c}` component that evaluates it.

**Convention for live rows.** A row `c` with infinitely many such P-positions
has `f(q, c) > q` for every `q >= c`: if `f(q0, c) <= q0` for some `q0`, the
cited stale-row lemma makes the row constant from `q0`, hence stale. So `B_c(x)
>= 1` is defined for every `x >= 0`, and by Byrnes' eventual periodicity
(MISSION s3) it is periodic from some point on. Let `p_c` be its least eventual
period and `u_c` the least `x0 >= 0` with `B_c(x + p_c) = B_c(x)` for all
`x >= x0`. Set `N(c) = c + u_c`. This is MISSION s4's `N(c)`, the least `q0`
from which `f(q, c) - q` is exactly periodic (the onset does not depend on
which eventual period is used). For row 0 it gives `u_0 = 0` and `N(0) = 0`,
as above.

So `N(c)` is defined for every row, and in both cases `u_c = N(c) - c` is the
argument from which `B_c` is periodic (live) or undefined (stale). Existence is
all that is used; nothing here bounds `N(c)`.

Notation. Fix the third row `r >= 1`. For `c < r`:

```
  B_c(x)   = f(c+x, c) - (c+x)                  (loser coordinate of row c)
  u_c      = N(c) - c                           (row c preperiod, a-coords)
  p_c      = period of row c (p_c := 1 for stale rows)
  q_r      = lcm{ p_c : c < r }
```

Write `F(x, r) = f(x, r)` for `x >= r` and `F(x, r) = f(x, x)` for `x < r`
(the first clause of the recurrence), and decompose
```
  V''_{r,c}(a) = { B_c(a + r - c) }  if defined, else ∅
  V'_{r,c}(a)  = { B_c(0) - (r-c) - a }  ∩ Z_{>=0}   (∅ if B_c(0) is undefined)
  W_r(a)       = V''(a) ∪ V'(a),     V''(a) = ⋃_{c<r} V''_{r,c}(a),
                                    V'(a) = ⋃_{c<r} V'_{r,c}(a),
```

and let `L_a = B_r(a) = f(r+a, r) - (r+a)`. Call `a` *reached* if `L_{a'} >= 1`
for every `a' < a`; the row terminates at the first `a` with `L_a = 0`. The
recurrence in the form used below is

```
  L_a = mex( W_r(a) ∪ T_a ),   T_a = { L_{a-i} - i : 1 <= i <= a } ∩ Z_{>=0},   (FR)
```

mex over the **non-negative** integers, for every reached `a`. `T_a` is the
*finite* trail: `T_0 = ∅`.

**Derivation of (FR) from MISSION section 2.** Fix `r >= 1` and a reached `a`,
and put `q = r + a`, so `q >= r` and `q >= 1`.

1. *`f(q, r) >= q`.* Let `q0` be the least `q' >= r` with `f(q', r) <= q'`
   (if there is none, `f(q, r) > q` outright). Since `a` is reached,
   `f(q', r) > q'` for `r <= q' < q`, so `q <= q0`. If `q < q0` then
   `f(q, r) > q`. If `q = q0`, the row is stale: `f(q0, r) <= q0 < q0 + 1`
   triggers the copy branch, and inductively `f(q', r) = f(q0, r) < q'` for
   every `q' > q0`. So the cited stale-row lemma applies and gives
   `f(q0, r) = q0`, i.e. `f(q, r) = q`.
2. *The mex branch is taken.* `r > q` is false. The copy branch returns
   `f(q-1, r) < q`, which step 1 excludes. So `f(q, r) = mex_{>=1}(S)` with
   `S = { F(x, r) : x < q } ∪ { f(q, b) : b < r }`.
3. *Shift to a mex over `Z_{>=0}`.* By steps 1 and 2, `mex_{>=1}(S) >= q`, so
   `{1, ..., q-1} ⊆ S`. Hence `mex_{>=1}(S) = q + mex_{>=0}(S_q)` with
   `S_q = { s - q : s ∈ S, s >= q }`. This is the step that needs `q >= 1`.
   At `q = 0` the positive-integer mex of `∅` is `1`, not `0 + mex_{>=0}(∅)`.
4. *Identify `S_q`.* Split `S` into three families.
   - `x = r + a - i` with `1 <= i <= a` (so `r <= x < q`):
     `F(x, r) - q = L_{a-i} - i`. Kept iff `>= 0`. This gives `T_a`.
   - `x = c < r`: `F(c, r) = f(c, c)`, and `f(c, c) - q = B_c(0) - (r - c) - a`.
     Kept iff `>= 0`. This gives `V'(a)`. If `f(c, c) < c` the value is `< q`
     and is dropped, matching `V'_{r,c} = ∅`.
   - `b < r`: `q = b + (a + r - b)`, so `f(q, b) - q = B_b(a + r - b)` when
     `f(q, b) >= q` (the defined case). Otherwise the value is `< q` and is
     dropped. This gives `V''(a)`.

   So `S_q = V''(a) ∪ V'(a) ∪ T_a`, and `L_a = f(q, r) - q = mex_{>=0}(S_q)`,
   which is (FR). ∎

*The bound on `B_c`.* `f(q, c) <= q + c + 1` for all `q >= c >= 0`, by
induction on `q`. In the mex branch, `S` has at most `q + c` elements, and the
least positive integer missing from a set of `n` integers is `<= n + 1`. In the
copy branch, `f(q, c) = f(q-1, c) < q`. Hence every defined
`B_c(x) = f(c+x, c) - (c+x) <= c + 1`.

## Lemma M — merged-trail machine

**Claim.** Define `H_0 := V'(0)` and iterate

```
  k_a = mex( V''(a) ∪ H_a ),      H_{a+1} = dec(H_a) ∪ { k_a - 1 }.    (M)
```

(with the convention that `k_a = 0` terminates: `H_{a+1}` is not formed).
Then, for every `r >= 1`, `k_a = L_a` and `H_a = V'(a) ∪ T_a` for every
reached `a`, up to and including the terminating one, where `T_a` is the finite
trail of (FR). Moreover `H_a ⊆ [0, m_r - 1]` and `k_a <= m_r`, where
`m_r = 1 + max{ B_c(x) : c < r, B_c(x) defined }`. By the bound on `B_c` above,
every defined `B_c(x) <= c + 1 <= r`, so `m_r <= r + 1`.

**Proof.** Two independent identities, both one line.

1. `V'(a+1) = dec(V'(a))`. Indeed `V'(a) = { B_c(0)-(r-c)-a : c < r } ∩ Z_{>=0}`
   and `dec` maps the singleton at value `v` to the singleton at `v-1`,
   discarding `v = 0`; that is exactly the `a ↦ a+1` shift of the family.

2. `T_{a+1} = dec(T_a) ∪ { L_a - 1 }` (for `L_a >= 1`; if `L_a = 0` the row
   terminates). Indeed
   `T_{a+1} = { L_{a+1-i} - i : 1 <= i <= a+1 } ∩ Z_{>=0}
            = ( { L_a - 1 } ∪ { L_{a-j} - (j+1) : 1 <= j <= a } ) ∩ Z_{>=0}
            = { L_a - 1 } ∪ dec(T_a)`,
   using `L_a - 1 >= 0`.

Both families therefore obey the *same* decay rule, so their union
`H_a := V'(a) ∪ T_a` obeys `H_{a+1} = dec(H_a) ∪ { L_a - 1 }`, and (FR)
reads `L_a = mex( V''(a) ∪ V'(a) ∪ T_a ) = mex( V''(a) ∪ H_a )`. The base
case is `H_0 = V'(0) ∪ T_0 = V'(0)`, because the finite trail `T_0` is empty
(there is no `i` with `1 <= i <= 0`). Induction on `a` in (M) then gives
`k_a = L_a` at every reached step. (FR) holds at every reached `(r, a)` with
`r >= 1`, since then `q = r + a >= 1` (derivation, step 3). That is why the
scope excludes `r = 0`.

(Equivalently, the infinite trail `{ L_{a-i} - i : i >= 1 }`, read with
`L_{-j} := f(r-j, r-j) - (r-j) = B_{r-j}(0)` for `1 <= j <= r` from the first
clause, equals `T_a ∪ V'(a)`. Its terms with `a < i <= a + r` are exactly the
`V'` family. Here `V'` is
kept separate and the trail is finite.)

*The invariant.* Every element of `V''(a)` is some `B_c(x) <= m_r - 1`. Every
element of `V'(0)` is `B_c(0) - (r - c) <= m_r - 2`, so `H_0 ⊆ [0, m_r - 1]`.
If `H_a ⊆ [0, m_r - 1]`, then `V''(a) ∪ H_a ⊆ [0, m_r - 1]`. Since
`mex(X) <= max(X) + 1`, and `mex(∅) = 0`, this gives `k_a <= m_r`. If
`k_a = 0` the machine stops there, and no `H_{a+1}` is formed. Otherwise
`k_a >= 1`, so `k_a - 1 ∈ [0, m_r - 1]` and
`H_{a+1} = dec(H_a) ∪ {k_a - 1} ⊆ [0, m_r - 1]`. ∎

**Consequences.** (a) The whole row-`r` dynamics is a deterministic machine
driven by the single input sequence `V''(a)`; the `V'` family needs no separate
handling. (b) The state `(τ; H)` with `τ = a mod q_r` is deterministic as soon
as `V''` is `q_r`-periodic. By the invariant there are at most
`q_r · 2^{m_r}` states `(τ; H)` with `H ⊆ [0, m_r - 1]`.

## Lemma S — determinism onset

**Claim.** For every `r >= 1`, `V''(a)` is `q_r`-periodic for all
`a >= max(σ_r, 0)`, where

```
  σ_r = max_{c<r} N(c) - r =: M_{r-1} - r,      M_{r-1} = max_{c<r} N(c).
```

`N(c)` follows the stale-row and live-row conventions above. At `r = 1` the max and lcm are
over `c < 1`, i.e. only `c = 0`: `σ_1 = N(0) - 1 = -1` and `q_1 = p_0 = 1`.
Indeed `V''(a) = { B_0(a+1) } = {1}` is constant. (With an empty index set the
conventions `max ∅ = -∞` and `lcm ∅ = 1` would apply, but `c = 0 < r` always
occurs.) In particular the machine (M) is autonomous (deterministic given its
state and phase) from `a = max(σ_r, 0)` on.

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

- the machine and the derivation of (FR), re-checked on an independent table
  built from MISSION section 2 alone for `q < 400`: (M) equals `B_r(a)` at all
  20469 reached steps of rows `1 <= r <= 132`; `{1, ..., q-1} ⊆ S` at every
  one of them, so the mex branch is taken with value `>= q`; and
  `f(q, c) <= q + c + 1` at every cell;
- machine (M) reproduces `f(r+a, r) - (r+a)` exactly for all rows
  `1 <= r <= 300` and all `a` in range, stale rows including their terminating
  `0`. Row 0 is excluded, as in the scope above;
- `V''` is `q_r`-periodic from `a = max(σ_r, 0)` on sample rows, with 0
  failures;
- independently, on a 700 x 700 table built from the recurrence alone (no
  solver): machine (M) equals `B_r(a)` at all 45905 steps over rows
  `1 <= r <= 199`, up to and including each stale row's terminating 0. At every
  step `H_a ⊆ [0, m_r - 1]` and `k_a <= m_r`.
