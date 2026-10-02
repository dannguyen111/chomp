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

## (Z2) IS NOW CLOSED TOO (session S20260930T0949): C0027

The previous session's handoff said "(Z2) remains open". It does not: **C0024's
part (iv) is itself an a priori bound on `q_r`**. Because `q_1 = 1` and (iv)
plus the prior-art `m_r <= r+1` never consults the actual periods, the recursion
unrolls to a closed form:

> `g(1)=1, g(r+1)=g(r)^2 (r+2)^(r+1)`  =>  `q_r <= g(r)`  (Lemma A; this IS (Z2)).
> `h(r)=11+r+sum_{k=2}^r g(k)(k+2)^(k+1)`  =>  `u_r=N(r)-r <= h(r)`  (Lemma B).
> Hence `N(r) <= r + h(r)` for ALL rows, live and stale.

`g(r)=2^{Theta(2^r)}`, so `N(r) <= 2^{2^{O(r)}}`: a double-exponential but fully
explicit computable bound — a genuine closed form, with no quantity on the right
defined by a recursion over the actual rows. **The MISSION target (section 4) is
met.** Proof in `proofs/C0027.md`; verification in `scratch/verify_closed_form.py`
(exact big-int r<=12, log-space r<=60). Sharpening to `C·r` remains open and is a
different question (equivalent to bounded discrepancy of A029902, C0016).

## C0028 sharpens C0027 (same session): lcm recursion is LINEAR

C0027's `q_{r+1} <= q_r^2 (r+2)^{r+1}` lost a factor `q_r` unnecessarily. The
pigeonhole's repeated state carries the phase `a mod q_r`, so the repeated-period
`s` satisfies `q_r | s` AND `p_r | s`, hence `q_{r+1} = lcm(q_r, p_r) | s <=
q_r(m_r+1)^{m_r}` **directly** — no need to multiply (ii)'s `p_r` bound by `q_r`.
This gives `g(r+1)=g(r)(r+2)^{r+1}` and `N(r) <= 2^{O(r^2 log r)}` instead of
`2^{2^{O(r)}}`. Proof in `proofs/C0028.md`; verified exact r<=12, log-space r<=60.
**C0027 is superseded for the bound's exponent by C0028** (the linear lcm recursion
is the correct one); C0027 remains correct as a bound, just weaker.

## What is actually left (final for this session)

1. **Referee C0024 and C0028** (and C0027 if desired). All `lemma` + proof,
   refereeable; C0027 and C0028 have restatements in `LEDGER/restatements.json`.
2. **(Z2) is closed** by C0027/C0028 (now `2^{O(r^2 log r)}`). Only *sharpening*
   remains: `N(r) <= C·r` for explicit `C` (MISSION's "full success"), which is
   the discrepancy question C0016/C0025, not a finite-state pigeonhole.
3. **(B1)**, a computable `K(r)` for the last stale P-position, still open for
   Byrnes' proof specifically; C0024/C0028 bound it only via the Zeilberger route.

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
## Session S20261002T0953: the merged-trail machine (C0032-C0038) and the flagship conjecture

This session did NOT re-referee C0024/C0028 (two attempts hit session wall-clock
caps mid-run; the referee needs ~40-60 min unbounded and writes its verdict only
at the end -- run it with no timeout wrapper). Instead it built the
recurrence-internal attack's concrete form. All claims logged (C0032-C0038).

### The machine (C0032, proved, `proofs/C0032_machine.md`)

Zeilberger's Fundamental Recurrence collapses to ONE machine. The instant-winner
family splits `W_r(a) = V''(a) u V'(a)` and the V' family decays exactly like
the mex-trail (`V'(a+1) = dec(V'(a))`), so merge them:

```
    H_0 = V'(0),   k_a = mex(V''(a) u H_a),   H_{a+1} = dec(H_a) u {k_a - 1}
    L_a = B_r(a) = k_a    (k=0 terminates = stale row)
```

Validated against the solver exactly (all rows r<=300, all a). The whole row-r
dynamics is driven by `V''(a)` alone.

### Determinism onset (C0033, proved)

`V''(a) = {B_c(a+r-c) : c<r}` is `q_r`-periodic from
`a = sigma_r = max_{c<r} N(c) - r` -- strictly earlier than C0024's `t_r = r`,
because the V' family no longer needs to extinguish. `sigma_r ~ 0.414 r`, and
the true preperiod `u_r = N(r)-r ~ 0.414 r` tracks it.

### FLAGSHIP CONJECTURE (C0037): N(r) <= max_{c<r} N(c) + 6

`u_r - sigma_r = N(r) - max_{c<r} N(c)` lies in [-4,+6] over ALL r<=50000
(C0034), max 6 saturating since r=15000. If this O(1) is proved as a machine
locking lemma, then `N(r) <= max_{c<r} N(c) + K` inducts to `N(r) <= K r` --
MISSION's "full success". Empirically K=2 suffices (C0030). THIS IS THE NEXT
PROOF TARGET: show the C0032 machine locks within K steps of determinism onset.

Lock delay by class (50000 rows): live p=1 max 6, p=2 max 5, p=3 max 4,
p=4 max 5, p=6..9 <= 2, stale max 3.

### Mechanism (C0036) and what is NOT the mechanism (C0035, C0038, dead ends)

- Attractors: fixed points `H*=[0,k-1]` for every `k not in u_phases V''`
  (infinitely many coexisting!), the termination attractor `H=0`, and p-cycles
  whose H is p descending arithmetic progressions mod p (r=120: H alternates
  [0-70] / [0-69,71], k alternates 72/70).
- A descending hole (plug staircase) = a fixed p* occurring as valid f-value in
  consecutive columns (C0035). Table runs reach length 177 (p*=425, cols
  249..425) while delays are <=6 -- so "delay <= staircase length" is FALSE as
  stated; long runs sit at heights far from the mex band or involve c>=r.
- The abstract machine has transient ~2.4*M even at q=1,p=1 (C0038): the O(1)
  lock is genuinely chomp-specific. Holes at sigma_r sit at depths up to 175
  below the mex, so the state is not "naively clean" either.

### C0028 proof fixes (adversarial self-review)

Addendum appended to `proofs/C0028.md`: (1) Lemma A' needs a live/stale
case-split (stale rows have p_r:=1 so the bound is trivial there; the repeated
state doesn't exist post-termination); (2) Lemma C' needs `h(r-1) >= r+1`
(induction from `h(r) >= h(r-1)+1`), not the false `12 > r+1`; (3) Zeilberger's
Lemma Bounded (source line ~612) justifies `L_a <= m_r` for the current row, and
C0012 alone suffices for the closed form. Bound unchanged.

### Referee status

C0024 and C0028 remain `open` (unrefereed). Two dispatch attempts this session
were killed by session wall-clock caps mid-run (the referee runs up to 80 LLM
turns, ~40-60 min). NEXT SESSION: run
`python -u -m harness.referee C0028 --root . --max-spend 0.45` FIRST THING with
no timeout wrapper (unbuffered, so partial progress is visible). C0028 has a
provenance-free restatement in `LEDGER/restatements.json`; C0024 does not --
add one before refereeing it, or the dependency statements leak narrative.

### Addendum (end of S20261002T0953): C0039, the sharp plug-run conjecture

`scratch/postonset_runs.py` measured the post-onset plug runs (the quantity
controlling lock delay): with witnesses `c < r` and columns `q >= max_{c<r}N(c)`,
max run length is **<= 5 on every row r<=400** (358/400 hit exactly 5, zero
clipped by the window), while dropping the `c < r` restriction lets runs reach
the window edge (unbounded). So the conjecture to prove is exactly:

> Valid P-positions `(p*, q+i, c_i)`, consecutive `q+i >= max_{c<r}N(c)`,
> witnesses `c_i < r`, heights `p*-(q+i)` descending 1 per step: length <= c0.

Observed c0 = 5. Proving it gives lock delay <= c0+2 and **N(r) <= (c0+2) r =
7r** (C0037 with K=7). The proof must exploit BOTH `c_i < r-1` and `q+i >=
1.41r` against `p* <= q+i+r` (C0012): a fixed p* then forces `q+i` into
`[p*-r, p*]`, and `c_i` into `[0, r)` while the mex defining `f(q+i, c_i)` sees
the whole row below. Long global runs (C0035) all have witnesses `c` close to
`q`, outside this window — that is why they do not contradict c0=5.

### Final addendum (S20261002T0953, landing): C0039 counterexample hunt

`scratch/c0039_hunt.py` (table r<=800, q<=2200) enumerated ALL raw plug runs:
raw runs reach 459 but every run of length >= 7 is inadmissible for every row
(the per-column min-witnesses grow along the run, cstar ~ q0+t, while post-onset
needs q0 >= max_{c<=cstar}N(c) ~ 1.41 cstar -- quantitatively far off, e.g.
len-459 needs q0>=1107 vs actual 648). MAX ADMISSIBLE RUN = 6, so c0 drifted
5 -> 6 with table size: state the conjecture as 'absolute constant c0', and
the C0037 consequence as N(r) <= (c0+2) r. Witness-floor identity: f(q,c)=q+h
forces c >= h-1 by C0012 (f(q,c) <= q+c+1). PROOF WARNING (dead_ends): the
measured inadmissibility uses the sqrt(2) LOWER slope of N -- the hard half of
the strip law; a proof of C0039 must either find a slope-free squeeze
(witness-floor + structural witness growth along runs) or prove N(c) >= alpha c
(alpha>1) from the recurrence first.

**Route update (C0040):** the slope-free proof route is the plane-antichain
reframing -- a run of fixed `p*` is a set of P-positions `[c,a,b]` with
`c+a+b = p*` constant and consecutive `q = c+a`; bound how many consecutive q
the P-position antichain can meet inside such a plane, using explicit profile
move combinatorics. Long runs die of validity (`q > p*`), medium runs of
coincidence failure (some column has no witness row at all). See C0040.

**Route update 2 (C0041, C0042):** the pure-poset plane-antichain route is
REFUTED (the c=0 line is an antichain of size p*; P-position plane sections
reach 459). Proved instead: **C0041, the single-row run lemma** -- post-onset
each witness row covers <= p_c consecutive columns of a plug run (periodicity
vs unit-descent contradiction). Long runs survive only PRE-onset for their
witness rows (they feed on transients). C0039 therefore reduces to the
INTERLEAVE question (C0042): can level sets of different rows -- each a union
of <= p_c-consecutive pieces determined by the periodic tails B_c -- jointly
cover > c0 consecutive columns post-onset? Observed c0 = 6. This is the exact
finite combinatorial residue of the N(r) <= C*r problem on this route; a
post-onset run of length > 9 on a larger table would falsify C0039 outright.

**Falsifier hunt outcome (final, S20261002T0953):** table r<=1200, q<=3200,
389013 admissible runs -- max still exactly 6, same `p*=1182..1266, cstar=585`
family; no run >=7 at any scale tested. C0039 stands. Next: hunt r<=3000+ for
the cheap falsifier (admissible run >=7; >=10 would be multi-row interleave
and probe C0041's question directly), then attack the interleave bound via
SAT/ILP over periodic-tail shapes (each row contributes <=p_c<=9-consecutive
pieces; tails are finite computable objects).

**Falsifier hunt, 4th scale:** table r<=1800, q<=4600 (825367 admissible runs,
raw max 1056 all inadmissible): max admissible STILL exactly 6, same
cstar=585 family. No admissible run >=7 on any of four scales. C0039 stands;
hunt r<=3000+ for the >=7 falsifier, then SAT/ILP over tail shapes for the
interleave bound.

**Falsifier hunt, COMPLETE CENSUS (final word this session):** `hunt_full.cpp`
scans every periodic tail in the census (all 50000 rows, all q <= 72000):
max run of consecutive columns sharing a p* = **7** (75821 heptads, 0 octads),
and raw runs also max at 7 in the periodic world (the 1056-long runs fed on
transients only, C0041 exactly). So c0 = 7 on all available data (the earlier
5/6 constants were table-range-limited; heptad witnesses have cstar ~ 18718).
Consequence: N(r) <= 9r via the mechanism chain. PROOF TARGET: periodic tails
with periods p_c cannot interleave to cover 8 consecutive columns sharing p*;
FALSIFIER: an 8-run in any periodic-tail extension (needs rows beyond r=50000).

**Heptad anatomy (C0043):** the maximal runs are tail-onset alignments -- 7
distinct rows in a 13-wide c-band, one column each, all sampled just past
their own tail onset (q0-N(c) in [1,18], a-u_c in [0,20]), B matching the
descending heights exactly. The interleave question localises to the onset
values B_c(u_c): can 8 rows' onset windows align with 8 consecutive heights?

**Heptad anatomy, population-corrected (C0043):** confirmed -- exactly one
witness per column, 7 distinct rows one column each (150/150 sampled). REFUTED
-- the 'tail-onset alignment' story (offsets q0-N(c) spread from 69 upward, not
1..18; the single dissection was overfit). Correct picture: maximal runs are
one-row-per-column matchings of 7 scattered tail values against the descending
heights. The interleave proof must explain that matching and why 8 fails.

**Heptads saturate sqrt(2) (C0044):** min q0/cstar over all 10873 heptads =
1.4142475 = sqrt(2) to 5 digits; hexads spread freely. Maximal runs live where
the post-onset constraint binds tightest -- tying the interleave constant c0 to
the sqrt(2) law's lower edge. The interleave proof likely needs (or implies)
N(c) >= sqrt(2)c - O(1). Correlation, not proof; but it says WHERE to look.

**C0044 CORRECTION (same session, later):** the sqrt(2) 'saturation' is mostly
the admissibility filter speaking (heptads.txt holds only admissible runs, so
q0/cstar >= sqrt(2) by construction). Slack q0-M[cstar] spans 0..9521: typical
heptads are NOT boundary-pinned. Survives: the boundary is attained (slack
0..2 runs exist) and octads exist nowhere. Proof must work uniformly in slack;
the link to the N-law lower edge is speculation only.
