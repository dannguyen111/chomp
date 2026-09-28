# Island 01 -- recurrence-internal attack

Phase 0 findings you should not re-derive. Everything here is backed by
`GROUND_TRUTH/byrnes_audit.md` and `GROUND_TRUTH/seed_check.md`; read those
before writing any code.

## The localisation is done -- do not redo it

Both proofs have been read in full, twice, and the second read corrected the
first. See the ERRATA block at the top of `GROUND_TRUTH/byrnes_audit.md`.

- **Byrnes (INTEGERS 3 (2003) #G03).** The quantitative chain loses
  effectivity at the **converse direction of Lemma 4**, which produces `M`, `N`
  from the bare finiteness of `{(m,n) : g(A_{m,n}) = k}`; that is the sole
  source of `T(A,k)` and hence `W(A,k)`. Two further non-effective steps exist
  outside that chain (C0023): Lemma 10's enumeration (p.17), which presupposes
  deciding `k in Q(A)`; and the reduction to assumption (3) on pp.15-16, which
  enlarges `A` with no bound -- and `|A|` sits in the exponent of `4^(|A|+k)`.
- **The Lemma 9 pigeonhole is NOT the problem.** It is counted and explicit:
  `p_{A,k} <= 4^(|A|+k) p` and `N_{A,k} <= N + 4^(|A|+k) p`. Verified against
  the paper. Going after it is the single most likely way to waste a session.
- **Zeilberger's exposition is a different proof with no non-effective step.**
  But he never counts the state space: the count
  `N(r) + period(r) <= a_0(r) + p_r (M_r+1)^(M_r)` is the audit's own
  derivation, and it needs the preperiod term `a_0(r)`, making it a recursion
  over `r` rather than a closed form (C0023). Do not cite the count to him.
- The PDF at the URL in MISSION.md is **truncated at 6 pages**. Use the TeX
  source `https://sites.math.rutgers.edu/~zeilberg/mamarim/mamarimTeX/byrnes.tex`.
  `python -m GROUND_TRUTH.fetch_sources` downloads every primary source into
  `GROUND_TRUTH/data/` (they are not committed -- the repo is public).

## (Z1) WAS CLOSED IN 2005, IN PRINT. Do not work on it, do not claim it.

**C0012 is prior art.** Brouwer, Horvath, Molnar-Saska & Szabo, "On Three-Rowed
Chomp", INTEGERS 5 (2005) #G07, section 8.1, states `1 <= f(q,r) <= q+r+1` one
line after giving the recurrence. That is exactly C0012, in the paper the
recurrence comes from. Our proof is correct and more explicit; the result is
not ours. Cite #G07. See the PRIOR ART block at the top of `proofs/C0012.md`.

Read `fg7.pdf` (now in `fetch_sources.py`) before claiming ANY property of
`f(q,r)`. It was missing from the source list until 2026-09-23, which is the
whole reason C0012 went proved -> refereed -> promoted before anyone checked.

## BOTH HALVES OF (Z1) ARE CLOSED. Do not work on it.

Two independent results, from two different directions, and neither needs
anything further:

**C0012 (session 1).** `f(q,r) <= q + r + 1`, hence `max_q (f(q,r)-q) <= r+1`.
Four-line induction; branch (C) takes a mex over at most `q+r` positive
integers, so one of `1..q+r+1` is missing. Proof in `proofs/C0012.md`.

**C0021 (2026-09-21 correction).** Byrnes' Lemma 5, correctly specialised,
gives `p - q <= 3r - 1` for every P-position, uniformly in `q`. Proof in
`proofs/C0021.md`.

C0012 is the sharper of the two (`r+1` against `3r-1`). C0021 matters because
it corrects a **wrong coordinate in the Phase 0 audit**: C0009 read Byrnes'
`n` as `p-q`, but his assumption (1) forces `n = p-r`.

## The recursion IS NOW CLOSED (session S20260928T0956): C0024

C0013 (the old closed-form bound) was **wrong** — it omitted the preperiod of
the instant-winner sequence, exactly as C0023 flagged. **C0024 is the honest
repair, and it is a `lemma` with a complete proof** (`proofs/C0024.md`):

> In Zeilberger coordinates `[c,a,b]` with `B_c(a) = f(c+a,c)-(c+a)`,
> `u_c = N(c)-c`, `p_c = period(c)` (1 for stale rows), `q_r = lcm{p_c:c<r}`,
> `m_r = 1 + max{B_c(a):c<r,a>=0}`, `t_r = max(max u_c, r)`:
> `p_r <= q_r(m_r+1)^{m_r}` and
> `u_r <= max(t_r,m_r) + q_r(m_r+1)^{m_r}`.
> Hence an **effective recursion** `N(r) <= r + max(t_r,m_r) + q_r(m_r+1)^{m_r}`
> (stale rows: `+ 1`), with every right-hand quantity computed from the solved
> rows `c < r`.

The preperiod bound for the instant winners is **Lemma P** in the proof:
`W_r(a) = ⋃_{c<r}({B_c(a+r-c)} ∪ {B_c(0)-(r-c)-a} ∩ Z>=0)` is `q_r`-periodic
for `a >= t_r`. This is the piece that was missing; there is nothing
non-effective anywhere in the chain. Verified numerically r<=400, a<=1400
(F1–F5; see `scratch/verify_recursion.py`), live and stale rows both.

This achieves **effectivity** (MISSION section 4's "any computable form" is a
success) but **not** a closed form: `q_r` is defined by the recursion. Closing
to a closed form is exactly (Z2), still open. The state-machinery subtlety:
the state must carry the phase `a mod q_r` (otherwise `W_r(a+1)` is not
determined by the state); the count `q_r(M+1)^M` is unchanged by this.

## What is actually left (updated)

1. **(Z2).** An a priori bound on `lcm{period(c) : c < r}` is the only gap
   between C0024's recursion and a closed form. Observed lcm to r=50000 is 72.
   Periods observed: {1,2,3,4,6,8,9}.
2. **(B1)**, a computable `K(r)` bounding the last `q` at which a stale row
   carries a P-position. Still open for Byrnes' proof specifically. C0024
   bounds it (`q-r <= max(t_r,m_r)+q_r(m_r+1)^{m_r}`) but only through the
   Zeilberger route.
3. **Referee C0024.** The proof is written and numeric checks scripted, but it
   has not been through the referee gate.

## Facts about `f` you can use without recomputing

- Rows split into **stale** (finitely many P-positions; these `r` are exactly
  A029902; density `0.58578 = 1/(1+sqrt(2)/2)`) and **live** (density
  `0.41422 = 1/(1+sqrt(2))`). 29289 / 20711 out of 50000.
- A row goes stale exactly when `f(q,r) = q`; then `f` carries that constant
  forever, and `N(r) = f(q,r) + 1` for that `q`. Verified for all 29289.
- `N(r) = sqrt(2) r + O(1)`: `-3.1565 <= N(r) - sqrt(2) r <= 5.6959` over all
  50000 rows, and the sup stops moving after `r = 26475`.
- `max_q (f(q,r) - q) = (sqrt(2)/2) r + O(1)`; `f(r,r) = (1+sqrt(2)/2) r + O(1)`.
- Periods to `r=50000`: 1 (49077), 2 (675), 3 (29), 4 (212), 6 (1), 8 (3),
  9 (4). lcm = 72. Periods 6 and 8 are **new**, not in Nivasch's census
  (which stops at 10000).

## Using the solver

Never modify `GROUND_TRUTH/`. File a `solver_bug` claim with a reproducing input.

```
python -c "from GROUND_TRUTH import chomp; print(chomp.table(24,24))"
GROUND_TRUTH/solver row    --r 120 --qmax 400     # q, f(q,r), f(q,r)-q
GROUND_TRUTH/solver column --r 6541               # period / preperiod
GROUND_TRUTH/solver census --rmax 20000 --out /tmp/c.tsv
```

`GROUND_TRUTH/cache/` holds the r=50000 census (`census_50000.tsv`).
Recomputing is cheap: r=10000 takes 5 s, r=50000 takes 436 s and ~200 MB peak.
`--alpha`/`--margin` move the horizon; `alpha=6` changes nothing for `r<=6000`.

## Settled tension with MISSION -- read this before you plan

`LEDGER/mission_disputes.md` records that MISSION section 3's blanket claim
("yields no computable bound") is right for Byrnes' general poset-game theorem
but too strong for Zeilberger's 3-row proof. **The project owner has resolved
this dispute in favour of the redirect** (see the RESOLVED block, dated
2026-09-20). The order of attack above is the authorised one; do not relitigate
it. Read `GROUND_TRUTH/byrnes_audit.md` instead -- it has the quotes.