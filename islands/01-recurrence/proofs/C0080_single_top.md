# C0080 — Single-top-per-row lemma (each row serves at most one rung of a plug run)

**Claim.** Let `c >= 0` and `0 <= q1 < q2` with `f(q1,c) = f(q2,c) =: p*`. If
`p* >= q2` (the later occurrence is a genuine P-position top), this is
impossible. Equivalently: along any row `c`, each value `p` occurs at most once
among the cells `(q,c)` with `f(q,c) = p >= q`. Hence in a plug run
(`f(q+j, c_j) = p*` for consecutive columns, `p* >= q+j`), the witness rows
`c_j` are pairwise distinct — with no hypothesis on periods, onsets, or
post-onset status.

**Consequence.** Every fixed-top run has one witness per column and one column
per witness row. This supersedes C0041 (which allowed `<= p_c` consecutive
columns per row) with `<= 1` per row, globally in `q`.

## Proof

Write `f(q,c)` per the recurrence (MISSION §2), branches (A) `c > q`:
`f(q,c) = f(q,q)`; (B) `f(q-1,c) < q`: `f(q,c) = f(q-1,c)`; (C) otherwise:
`f(q,c) = mex( {f(a,c) : a < q} ∪ {f(q,b) : b < c} )`.

Suppose `f(q1,c) = f(q2,c) = p*` with `q1 < q2` and `p* >= q2`. Consider the
branch used at `(q2, c)`.

**Case (A): `c > q2`.** Then `q1 < q2 < c`, so branch (A) also applies at
`(q1,c)`: `f(qi,c) = f(qi,qi) = d_{qi}` for `i = 1,2`. The diagonal values are
pairwise distinct: `d_n = f(n,n)` is by branch (A)-collapse
`mex( {d_a : a < n} ∪ {f(n,b) : b < n} )` (C0045's identity
`{f(a,n) : a<n} = {d_a : a<n}`), so `d_n` avoids `{d_a : a < n}`; by induction
the `d_n` are distinct. Hence `p* = d_{q1} != d_{q2} = p*`, contradiction.

**Case (B): `f(q2-1,c) < q2`.** Then `f(q2,c) = f(q2-1,c) = p* < q2`,
contradicting `p* >= q2`.

**Case (C).** The mex is over `S = {f(a,c) : a < q2} ∪ {f(q2,b) : b < c}`.
Since `q1 < q2`, `f(q1,c) = p*` is an element of `S`. The mex of `S` is by
definition not an element of `S`, so `f(q2,c) = mex(S) != p*`, contradiction.

All cases are exhaustive, so no such pair exists. Note the argument is
uniform: no assumption on `c`, on the regime (transient/tail/stale), or on
periods. (For `q2 <= c` only cases (A) and (C)/(B)-chains occur; the
branch-(B) chain `f(q2,c) = f(q2-1,c) = ... = f(q1,c)` forces
`f(q1,c) < q1+1`, i.e. `p* <= q1 < q2`, again contradicting `p* >= q2`; but
this sub-case is already covered: case (B) at `q2` gives `p* = f(q2-1,c) < q2`
immediately.)

**Stale rows.** For a stale row all large-`q` cells carry the constant
`dconst < q`, so those occurrences are invalid (`p* < q`) and cause no
violation; the lemma's statement already excludes them via `p* >= q2`.

**Diagonal distinctness premise.** `d_n = mex(...)` and `d_n` appears in no
earlier `d_a` because the mex set contains `{d_a : a < n}`. (This is the
mex property applied to the collapsed form; verified computationally to
`n = 120` and by C0045 to `n = 60`.)

## Verification

- Full table sweep `chomp.table(rmax, qmax)`, rows `c <= 60` with `q <= 180`
  and `c <= 120` with `q <= 360`: **0 violations over 54722 cells**.
- Tail form (independent): no tail word has `v(psi+d) - v(psi) = -d` for any
  row, any `psi`, any `1 <= d <= 5` (0 of 20712 rows; and `d >= 6` is excluded
  by band width `<= 5`). Equal tops at columns distance `d` is exactly the
  relation `v(psi+d)-v(psi) = -d`, so this re-derives the lemma on the
  periodic world.
- Population fact explained: all 5666 maximal runs (len >= 6) have distinct
  witness rows (C0073), now a theorem rather than an observation.

## Note on C0041

C0041 (`<= p_c` consecutive columns per row, periodicity vs unit descent) is
correct but weak; this lemma replaces its conclusion (`<= 1` rung per row per
fixed `p*`) with a shorter proof (the mex alone, no periodicity needed).
C0041's proof used periodicity; the present lemma does not.

## Addendum: column form (the dual lemma) is PROVED too

**Claim (column form).** If `f(q,c1) = f(q,c2) = p*` with `c1 < c2 <= q` and
`p* >= q`, impossible. Proof: case the branch at `(q,c2)`. (A) `c2 > q`:
excluded by `c2 <= q`. (B) `f(q-1,c2) < q`: then `p* = f(q,c2) = f(q-1,c2) < q`,
contradicting `p* >= q`. (C) mex over `S = {f(a,c2) : a<q} u {f(q,b) : b<c2}`:
`f(q,c1) = p*` is in `S` since `c1 < c2`, so `mex(S) != p*`. QED.

**Consequence (matching form).** The cells `(q,c)` with a given top `p*`
(valid, `p* >= q >= c`) have pairwise distinct rows AND pairwise distinct
columns: same-top P-positions form a partial matching in the grid. Combined
with the run definition (consecutive columns sharing `p*`): each column has
at most one witness and each witness row serves at most one column. This is
the structural form of C0043's "exactly one witness per column" and C0073's
"distinct witness rows", both now theorems.

**Verification (extended).** Sweep `chomp.table(R,Q)` for (R,Q) =
(60,180), (120,360), (200,600): 0 row-form violations, 0 column-form
violations over 175523 cells. Edge cases: row 0 strictly increasing
(f(q,0)=q+1); stale-death repeats always have p* = dconst < q2 (0 violations
of the valid form over all rows <= 200, q <= 600).
