## State

The effectivity target is achieved on the Zeilberger route. The remaining piece was the
preperiod correction C0023 flagged: C0013's closed-form bound omitted the preperiod of the
instant-winner sequence. This session wrote out the corrected recursion in full, proved it,
and verified it numerically.

The corrected chain (C0024, proof `islands/01-recurrence/proofs/C0024.md`): in Zeilberger
coordinates `[c,a,b]` with `B_c(a) = f(c+a,c)-(c+a)`, `u_c = N(c)-c`, `p_c = period(c)`,
`q_r = lcm{p_c : c<r}`, `m_r = 1+max B_c(a) <= r+1`, `t_r = max(U_r, r)`, we have
`p_r <= q_r (m_r+1)^{m_r}` and `u_r <= max(t_r,m_r) + q_r(m_r+1)^{m_r}`. Hence an effective
recursion `N(r) <= r + max(t_r,m_r) + q_r(m_r+1)^{m_r}` for live rows (+1 for stale). Every
right-hand side is computed from solved rows `c < r`; nothing in the argument is
non-effective. The key new lemma (Lemma P) is that the instant-winner sequence
`W_r(a) = ⋃_{c<r} ({B_c(a+r-c)} ∪ {B_c(0)-(r-c)-a}∩Z>=0)` is `q_r`-periodic for `a >= t_r`.
One subtlety fixed during the session: the finite state must carry the phase `a mod q_r`
(otherwise `W_r(a+1)` is not determined); the state count `q_r(M+1)^M` is unaffected.

This is effectivity, not a closed form. `q_r` is defined by the recursion; a closed form
requires (Z2), a bound on `lcm{period(c): c<r}`, which remains open (observed lcm 72 to
r=50000).

## This session

1. Fetched all primary sources and re-read Zeilberger's TeX in full (the Fundamental
   Recurrence, Crucial Facts, Ultimate-Periodicity Theorem, and the "A Posteriori
   Justification" section). Confirmed the audit's coordinate reading `[c,a,b] = [r, q-r, p-q]`.
2. Wrote `scratch/verify_recursion.py`: verifies F1 (translation `B_r(a)=f(r+a,r)-(r+a)`
   matches census), F2 (preperiod exactness), F3 (Fundamental Recurrence reproduces `B_r`,
   live AND stale), F4 (preperiod of `W_r` at most `t_r`), F5 (all three inequalities). All
   pass for r<=400, a<=1400. Also verified stale-row termination exactly.
3. Wrote the full proof `proofs/C0024.md` in three drafts: the first two contained
   thinking-out-loud fragments and a stale-row boundary slip that were cleaned; the final
   version carries the phase-carrying state.
4. Logged C0024 (lemma, open) and marked C0013 superseded.

## Claims logged

- **C0024** (lemma, open): corrected effective Zeilberger recursion, with `p_r`, `u_r` bounds
  and the instant-winner preperiod Lemma P; proof in `proofs/C0024.md`; verified r<=400.
- **C0013** (conjecture -> superseded): the old bound, replaced by C0024.

## Next step

Referee C0024. The proof is complete and the numerical checks are scripted, but it has not
been through the referee gate; the highest-value action is to run the referee on it (the
claim restatement in `LEDGER/restatements.json` has no entry for C0024, so add one that
strips the project narrative before refereeing). If it survives, the target is met modulo a
formal closed form, and the remaining interesting work is (Z2): bound `lcm{period(c): c<r}`
a priori (observed periods are only 1,2,3,4,6,8,9 with lcm 72 to r=50000).

## Confidence

High that the recursion is correct: the only structural input is the prior-art value bound
C0012, and the counting argument's single failure mode (a coordinate slip) is pinned down by
F1–F5 against the validated solver. The thesis is not merely alive; effectivity is delivered.
The referee could still find a scope objection (it has done so before on C0012/C0021) — the
most likely is about whether the recursion qualifies as a bound of "computable form" given
that `q_r` is itself defined recursively; the proof file explicitly concedes this is a
recursion, not a closed form, and cites MISSION section 4's "any computable form" as the
standard. What would kill it: an error in Lemma P's use of C0012 at the diagonal (the
`2c+1-2r < 0` step), which is checkable in one line.