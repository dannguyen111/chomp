# Island 01 -- recurrence-internal attack

Phase 0 findings you should not re-derive. Everything here is backed by
`GROUND_TRUTH/byrnes_audit.md` and `GROUND_TRUTH/seed_check.md`; read those
before writing any code.

## The localisation is already done -- do not redo it

Both proofs have been read in full and the non-effective step is named.

- **Byrnes (INTEGERS 3 (2003) #G03).** Effectivity dies in exactly one place:
  the **converse direction of Lemma 4**, which produces integers `M`, `N` out of
  the bare finiteness of `{(m,n) : g(A_{m,n}) = k}`. That is the sole source of
  `T(A,k)`, hence of `W(A,k)`, and **`W(A,k)` is the only non-computable term in
  the final bound**.
- **The Lemma 9 pigeonhole is NOT the problem.** It is counted and explicit:
  `p_{A,k} <= 4^(|A|+k) p` and `N_{A,k} <= N + 4^(|A|+k) p`. Going after it is
  the single most likely way to waste this island's budget.
- **Zeilberger's exposition is a different proof and has no non-effective step
  at all.** Its state space is counted, giving
  `N(r) + period(r) <= p_r (M_r+1)^(M_r)`.
- The PDF at the URL in MISSION.md is **truncated at 6 pages**. Use the TeX
  source `https://sites.math.rutgers.edu/~zeilberg/mamarim/mamarimTeX/byrnes.tex`.
  `python -m GROUND_TRUTH.fetch_sources` downloads every primary source into
  `GROUND_TRUTH/data/` (they are not committed -- the repo is public).

## Your target, in order

**(Z1-residual) -- start here. This is the cheapest real theorem in the problem.**

Byrnes' **Lemma 5 is unconditional** and, in the 3-row reduction with the third
row fixed (`k=0`, `m=q-r`, `n=p-q`, `|A|=3r-1`), says

```
    (p - q) - (q - r)  <=  3r - 1       for every P-position (p,q,r)
```

verified against the solver over every P-position with `q,r <= 2000`, tight at
`(3,1,1)`. At `q=r` this already gives `f(r,r) <= 4r - 1`, explicit and proved.
What is missing is only that the bound degrades for large `q`. So:

> Prove that `max_q (f(q,r) - q)` is attained at, or within `O(1)` of, `q = r` --
> or bound `max_q (f(q,r) - q)` by `C r` any other way.

Data: the max exceeds `f(r,r) - r` by **at most 2** over all `r <= 2000`, and
`max_q (f(q,r)-q)/r` is at most 2 (at `r=1`), tending to `1/sqrt(2)`.
Brouwer's two proved lemmas are the natural materials: *the diagonal `f(q,q)` is
the largest element of column `q`*, and *for each `p` there are at least `p/3`
P-positions `(q,q,r)` with `q <= p`*. Both are on his page with proofs.

**(then) write out the chain.** (Z1) plus a bound on `p_r = lcm{period(c):c<r}`
gives, through Zeilberger's argument and nothing else,
`N(r) <= p_r (C r + 2)^(C r + 1)` -- an explicit computable bound of the form
`r^(O(r))`. MISSION section 4 counts *any* computable form as a success. Writing
this out carefully, with the constant pinned, is a real deliverable and is worth
logging even though the bound is astronomical.

**(B1) -- the harder and more interesting one.**

> Exhibit a computable `K` such that for every **stale** row `r` (finitely many
> P-positions), every P-position `(p,q,r)` has `q <= K(r)`.

This *is* `W(A,0)`. It is the one thing Byrnes leaves uncomputable, and an
explicit `K` of any shape (`3r`, `r^2`, `2^r`) makes his theorem effective with
no other change. Measured: `K(r) = sqrt(2) r + 4` suffices for all `r <= 50000`.

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
