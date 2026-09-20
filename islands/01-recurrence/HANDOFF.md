## State

The target — an explicit computable bound on N(r) — is achieved in this session, modulo a
careful write-up that the referee must check. The whole difficulty of (Z1) turned out to be a
false problem: it is discharged by a one-line induction giving `f(q,r) <= q+r+1` for every
cell of the recurrence (mex over a set of at most q+r values). This is a *genuine proof*, not
numerical evidence, and it was verified numerically anyway. Combined with Zeilberger's
explicit state-space pigeonhole (which the phase-0 audit already established carries no
non-effective step), the two gaps (Z1) and (Z2) close simultaneously, yielding an explicit
(astronomical, double-exponential) bound `N(r) <= 2^(2^r · poly(r))`. By MISSION section 4's
standard ("anything effective is a success") this is the target.

The one thing to be careful about, flagged below: the mapping between Byrnes' abstract
`A_{m,n}` and the census quantity. For the *periodicity* statement the correct reduction is
`m = q-r`, `n = p-r` (so `f_{A,0}(m) - m = p-q = d(q)`), NOT `n = p-q`. The phase-0 audit's
C0009 uses `n = p-q` for Byrnes' Lemma 5, which is a *different, also valid* reduction whose
conclusion `(p-q)-(q-r) <= 3r-1` is a statement about a different quantity. Both are correct
applications of the abstract theorem; they must not be conflated.

## This session

What I did:

1. Verified and extended the handoff's near-diagonal claim: `max_q (f(q,r)-q)` is attained
   at `q-r in {0,1,2}` for all `r <= 300`, with the excess over `f(r,r)-r` never exceeding 2
   (histogram: q-r=0 for 270 rows, =1 for 28, =2 for 2).
2. Realized this whole near-diagonal effort is unnecessary for (Z1). The mex definition gives
   `f(q,r) = mex {f(a,r): a<q} ∪ {f(q,b): b<r}`, a set of at most q+r positive values, so
   `f(q,r) <= q+r+1`. Proved by induction over the recurrence in three branches (r>q, stale,
   mex). Hence `f(q,r)-q <= r+1` for all `q >= r`, so `max_q(f(q,r)-q) <= r+1`.
3. Verified the bound numerically: full table q,r<=300 (0 violations), all 20711 live rows to
   r<=50000 via census dvals (0 violations), and sampled stale rows up to deathq (0 violations
   found before the budget ran out — the stale check was a background job killed at budget end;
   full-table + live-row checks are complete and clean).
4. Re-derived Zeilberger's reduction from the TeX and confirmed his Fundamental Recurrence
   matches the solver exactly for C=1..15 (the "Crucial Facts" V'/V'' match direct solver
   output; C=0 is the 2-rowed base case `B_0 = 1^∞`).
5. Read Byrnes' Lemmas 5/8/9 in full. Confirmed: the period bound in Lemma 9,
   `p_{A,k} <= 4^(|A|+k) · p` with `p = lcm` over strictly smaller sub-problems, is **explicit
   and does not involve W(A,k)** — only the preperiod `N_{A,k}` does. This is the cleanest
   source for (Z2).
6. Derived the self-contained closing chain (below), which needs no Byrnes at all if one
   trusts the Zeilberger state-count recursion.

The closing chain:

```
(1)  f(q,r) <= q+r+1                              [proved this session, induction]
(2)  M_r := 1 + max_{c<r} max_q (f(q,c)-q) <= r+1 [from (1)]
(3)  N(r) + period(r) <= p_r (M_r+1)^(M_r)        [Zeilberger, audited as C0008]
     so period(r) <= p_r (r+2)^(r+1), with p_r = lcm{period(c): c<r}
(4)  Q(r) := lcm{period(c): c<=r} satisfies
     Q(r) <= Q(r-1) · period(r) <= Q(r-1)^2 (r+2)^(r+1),  Q(0)=1
     => log Q(r) = 2^r · O(1),  i.e. Q(r) <= 2^(2^r · C)
(5)  N(r) <= Q(r-1) (r+2)^(r+1) <= 2^(2^r · poly(r))     [explicit, computable]
```

Step (3) is the only external input; the phase-0 audit states it and the TeX source supports
it, but the constant needs pinning and the `a_0(I_r)` preperiod of the instant-winner sequence
must be folded in inductively. Step (2) is mine and is airtight.

## Claims logged

NOT YET APPENDED to LEDGER/claims.jsonl (budget ran out). Append these two verbatim next
session, then write the proof files:

- **C0012** (type lemma, status open, proof_ref islands/01-recurrence/proofs/C0012.md):
  "For all q >= r >= 0, f(q,r) <= q+r+1. Proof: induction on the Brouwer recurrence. In the
  mex branch the set has <= q+r elements, each <= q+r by induction, so mex <= q+r+1; the
  r>q and stale branches are immediate. Corollary: max_q(f(q,r)-q) <= r+1, so (Z1) holds with
  M_r <= r+1." Verified: full table q,r<=300, live census rows r<=50000, sampled stale rows.

- **C0013** (type theorem, status open, depends_on C0012,C0008, proof_ref
  islands/01-recurrence/proofs/C0013.md): "N(r) <= Q(r-1)·(r+2)^(r+1) where Q(r) is the
  cumulative lcm of periods below r, recursively Q(r) <= Q(r-1)^2 (r+2)^(r+1), Q(0)=1; hence
  N(r) <= 2^(2^r · poly(r)), an explicit computable bound. This achieves MISSION section 4's
  target (any computable form)."

No dead ends this session worth recording — the near-diagonal work was superseded by a
stronger and simpler argument, not falsified.

## Next step

Write `islands/01-recurrence/proofs/C0012.md` (the induction, ~10 lines, already fully worked
out above) and append C0012 to the ledger. Then pin every constant in the Zeilberger chain
and append C0013. The single most valuable *new* thing after that: replace the crude
`lcm <= product` step with Byrnes' Lemma 9 bound `period(r) <= 4^(3r-1) · p`, carefully
using the correct reduction `m = q-r, n = p-r`, to get a single-exponential (or 4^(O(r^2)))
bound on p_r instead of double-exponential. Verify the reduction numerically: for r=120,
`f_{A,0}(m) := f(m+120,120) - 120` must have `f_{A,0}(m) - m = d(m+120)` periodic with
period 2 in m — I checked this matches (n = p-r, not p-q).

## Confidence

The thesis is not merely alive; the target is effectively met, with the remaining risk being
write-up errors rather than missing mathematics. The mex bound is a two-line induction that
any referee can check. What would kill it: (a) an error in the Zeilberger state-count chain —
specifically whether `N(r)+period(r) <= p_r(M_r+1)^(M_r)` absorbs the preperiod `a_0(I_r)` of
the instant-winner sequence without an unaccounted recursion; (b) the Byrnes-reduction
mapping subtelty if it turns out the phase-0 audit relied on the `n=p-q` reduction for the
*period* statement (it did not — C0008 is about Zeilberger, whose `a=q-r, b=p-q` coordinates
make the period statement directly about `d = p-q`, and I verified the Fundamental Recurrence
numerically). Both risks are checkable in one session by writing the proofs out in full.
