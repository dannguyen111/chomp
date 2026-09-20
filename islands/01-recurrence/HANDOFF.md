## State

Phase 0 (no model spend) built and validated the solver, tested the seed
conjecture to `r = 50000`, and read both periodicity proofs end to end. You are
the first explorer session on this island; nothing has been attempted yet.

The problem stands like this. Byrnes proved eventual periodicity of `p-q` for
fixed `r`. His proof loses effectivity at exactly one step -- the converse
direction of Lemma 4 -- and the quantity it fails to bound, `W(A,k)`, is the
*only* non-computable term in his final bound. Zeilberger's independent proof of
the 3-row case has no such step: its pigeonhole is over a counted state space,
so it yields an explicit (astronomical) bound the moment two auxiliary
quantities are bounded a priori. One of those two is already half-proved by
Byrnes' own Lemma 5. The truth is `N(r) = sqrt(2) r + O(1)`, with the error
never leaving `[-3.16, +5.70]` over 50000 rows; the proofs give `r^(O(r))`.

## This session

Phase 0, not an explorer session. Built `GROUND_TRUTH/solver.cpp` (streaming,
interval-compressed; `r <= 50000` in 436 s and ~200 MB), validated it against
Brouwer's 325-cell table, eight OEIS sequences, the r=120 anomaly, Nivasch's
period census and an independent brute-force game tree (25/25 tests pass).
Tested Conjecture N and found it true and much stronger than stated. Read
Byrnes and Zeilberger and localised the non-effectivity.

## Claims logged

- C0001 solver agrees with the literature everywhere tested
- C0002 rows split stale/live with densities `1/a`, `1/b`
- C0003 `N(r) = sqrt(2) r + O(1)`, error in `[-3.1565, 5.6959]` for `r <= 50000`
- C0004 the law is not specific to non-trivially-periodic rows
- C0005 on stale rows Conjecture N is *equivalent* to a strip bound for A029901/A029902
- C0006 periods 6 and 8 occur above `r = 10000` -- new, outside Nivasch's set
- C0007 Byrnes loses effectivity only at Lemma 4's converse; the pigeonhole is explicit
- C0008 Zeilberger's proof has no non-effective step
- C0009 Byrnes' Lemma 5 gives `(p-q)-(q-r) <= 3r-1`, hence `f(r,r) <= 4r-1`
- C0010 (open) target restatement: (B1), or (Z1)+(Z2)

## Next step

Prove that `max_q (f(q,r) - q)` is attained at, or within `O(1)` of, `q = r`
-- or bound `max_q (f(q,r) - q)` by `C r` for an explicit `C` any other way.
Byrnes' Lemma 5 already gives `f(q,r) - q <= (q-r) + 3r - 1`, which is the
bound at `q = r` and degrades only for large `q`, so this is the whole remaining
content of (Z1). Start from Brouwer's two proved lemmas (the diagonal is the
maximum of its column; at least `p/3` P-positions `(q,q,r)` with `q <= p`).
Data to check against: the max exceeds `f(r,r) - r` by at most 2 for all
`r <= 2000`.

Do **not** attack the pigeonhole in Byrnes' Lemma 9 or in Zeilberger's
Ultimate-Periodicity Theorem. Both are already explicit. That is the single most
likely way to burn this session.

## Confidence

The thesis is alive and unusually well posed for a first session: the target is
a bounded, checkable statement about one maximum, not an open-ended search.
What would kill it: if `max_q (f(q,r) - q)` turns out to be attained at `q`
genuinely far from `r` for some family of `r`, the cheap route closes and (Z1)
becomes as hard as the rest. Test that numerically before investing in a proof --
it costs one script.
