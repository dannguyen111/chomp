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

## BOTH HALVES OF (Z1) ARE CLOSED. Do not work on it.

Two independent results, from two different directions, and neither needs
anything further:

**C0012 (session 1).** `f(q,r) <= q + r + 1`, hence `max_q (f(q,r)-q) <= r+1`.
Four-line induction; branch (C) takes a mex over at most `q+r` positive
integers, so one of `1..q+r+1` is missing. Proof written out in
`proofs/C0012.md`. Re-verified: 0 violations over the full table `q,r<=400`
and all 20711 live rows to `r<=50000`; tight at 402 cells (the row `r=0`).

**C0021 (2026-09-21 correction).** Byrnes' Lemma 5, correctly specialised,
gives `p - q <= 3r - 1` for every P-position, uniformly in `q`. Proof in
`proofs/C0021.md`.

C0012 is the sharper of the two (`r+1` against `3r-1`). C0021 matters because
it corrects a **wrong coordinate in the Phase 0 audit**: C0009 read Byrnes'
`n` as `p-q`, but his assumption (1) forces `n = p-r`. The "residual half of
(Z1)" that the Phase 0 notes set as this island's opening target was an
artefact of that slip and never existed. C0009 and C0010 are superseded; read
the ERRATA block at the top of `GROUND_TRUTH/byrnes_audit.md` before using
that document.

C0013 chains C0012 into an explicit `N(r) <= 2^(2^r poly(r))`. It is logged as
a `conjecture`, not a lemma, and **its displayed closed form is wrong**: the
Zeilberger state count omits the preperiod `a_0(r)` of the instant-winner
sequence, so the true shape is the recursion
`N(r) + period(r) <= a_0(r) + p_r (M_r+1)^(M_r)` (C0023).

## What is actually left

Per C0022, exactly one gap for a closed-form bound:

> **(Z2)** an explicit bound on `lcm{period(c) : c < r}`.

And for *effectivity* alone, nothing: on the Zeilberger route `M_r` and `p_r`
are computed from the already-solved rows `c < r`, so the procedure is already
effective. (Z2) buys an a priori closed form, not computability. Be precise
about which of the two you are claiming.

The remaining worthwhile targets, in order:

1. **(Z2).** Observed periods to `r=50000` are `{1,2,3,4,6,8,9}`, lcm 72. A
   bound on the lcm suffices; you do not need to bound the periods themselves.
2. **Write the corrected chain out.** With `M_r <= min(r+1, 3r-2)` from C0012,
   the preperiod-corrected recursion of C0023, and (Z2), produce a single
   explicit `N(r) <= ...` and log it as a lemma with a proof file.
3. **(B1)**, a computable `K(r)` bounding the last `q` at which a stale row
   carries a P-position. Still open for Byrnes' proof specifically, and the
   more interesting question. Note it is a threshold in `p-r`, not in `q`.

## Facts about `f` you can use without recomputing

- Rows split into **stale** (finitely many P-positions; these `r` are exactly
  A029902; density `0.58578 = 1/(1+sqrt(2)/2)`) and **live** (density
  `0.41422 = 1/(1+sqrt(2))`). 29289 / 20711 out of 50000.
- A row goes stale exactly when `f(q,r) = q`; then `f` carries that constant
  forever, and `N(r) = f(q,r) + 1` for that `q`. Verified for all 29289.
- `N(r) = sqrt(2) r + O(1)`: `-3.1565 <= N(r) - sqrt(2) r <= 5.6959` over all
  50000 rows, and the sup stops moving after `r = 26475`.
- This holds for **every** class, not just the period `>= 2` rows that the
  literature happens to tabulate.
- `max_q (f(q,r) - q) = (sqrt(2)/2) r + O(1)`; `f(r,r) = (1+sqrt(2)/2) r + O(1)`.
- Periods to `r=50000`: 1 (19787), 2 (675), 3 (29), 4 (212), 6 (1), 8 (3),
  9 (4). Periods 6 and 8 are **new** -- not in Nivasch's published census, which
  stops at 10000. lcm of all observed periods is 72.

## Using the solver

Never modify `GROUND_TRUTH/`. File a `solver_bug` claim with a reproducing input.

```
python -c "from GROUND_TRUTH import chomp; print(chomp.table(24,24))"
GROUND_TRUTH/solver row    --r 120 --qmax 400     # q, f(q,r), f(q,r)-q
GROUND_TRUTH/solver column --r 6541               # period / preperiod
GROUND_TRUTH/solver census --rmax 20000 --out /tmp/c.tsv
```

`GROUND_TRUTH/cache/` is restored from the phase0 Actions cache and holds a
census at whatever `max_r` phase0 ran with. Recomputing is cheap: r=10000 takes
5 s, r=50000 takes 436 s and ~200 MB peak.
`--alpha`/`--margin` move the horizon; `alpha=6` changes nothing for `r<=6000`,
so the preperiods are not horizon artefacts.

## Settled tension with MISSION -- read this before you plan

`LEDGER/mission_disputes.md` records that MISSION section 3's blanket claim
("yields no computable bound") is right for Byrnes' general poset-game theorem
but too strong for Zeilberger's 3-row proof. **The project owner has resolved
this dispute in favour of the redirect** (see the RESOLVED block in that file,
dated 2026-09-20). The order of attack above is the authorised one; you do not
need to relitigate it, and you should not spend tokens re-reading Byrnes to
check. Read `GROUND_TRUTH/byrnes_audit.md` instead -- it has the quotes.
