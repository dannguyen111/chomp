## State

The project target is an effective Byrnes: an explicit computable bound on N(r)
(the preperiod of f(q,r)-q). Prior sessions localized the single non-effective
step in Byrnes to (B1) -- a bound on how far a stale row can run -- and showed
the Zeilberger route needs only (Z1) [closed by C0021: p-q <= 3r-1] and (Z2)
[lcm of periods below r, still open]. The renormalisation picture gives the
sharp law N(r) = sqrt(2) r + O(1) (verified to r=50000), equivalently a strip
bound on A029902/A029901 about the Friedman-Landsberg lines a=1+sqrt(2)/2 and
b=1+sqrt(2).

**This session's key result: (B1) is now CLOSED by published prior art.**
BHMS (INTEGERS 5 (2005) #G07) §8.8 proves `q_n <= 3n-1` for the constant-row
values `q_n = A029901(n)`. Chaining with the logged identity N(r_n) = q_n + 1
and the trivial `r_n >= n` gives **N(r) <= 3r for every stale row**, equality
only at r=1. This is a proof, not numerics -- the ingredient is in print and the
audit's own section 3 lists 3r as an acceptable K(r). Numerically N(r) <= 3r
holds for ALL rows (and N(r) <= 2r for r >= 2), so the only remaining gap for a
uniform closed-form bound is the live rows.

## This session

1. Recovered the census and the diagonal table (rmax=3000, 0.6s) and
   re-derived the A029901/A029902 pairing from the census.

2. **C0029 (the payload).** Read BHMS §8.8 in the fetched PDF and found the
   printed claim `q_n <= 3n-1`. Chained it: N(r_n) = q_n + 1 <= 3n <= 3 r_n.
   Verified all components over all 29289 stale rows (0 violations of each).
   Wrote the proof to islands/02-renorm/proofs/C0029.md. This closes (B1) with
   K(r) = 3r.

3. **C0030.** Verified N(r) <= 3r for all 50001 rows (equality only r=1), and
   N(r) <= 2r for r >= 2. Live rows: max N/r = 1.7273 at r=11, 0 violations.
   Logged as observation (proved for stale via C0029, numerical for live).

4. **C0031.** Verified A029900 (diagonal d_n=f(n,n)) and A029901 (constant-row
   values) are exactly complementary (disjoint, cover all positive integers
   except 1), consistent with Sheiner Prop 4.4. This is the algebraic backbone:
   A029901 is the complement of the mex-generated diagonal.

5. **Dead ends.** (a) Tried to transfer the exact cocycle C0015 from the stale
   set to the diagonal discrepancy -- it fails (drift [-2.77,-0.42], not
   {-1,0,1}); the cocycle is a property of the stale set, not the raw diagonal.
   (b) Tried a closed form d_n = 2n+1-overlap_n for the diagonal mex -- false at
   n=52; the mex is genuinely 2-dimensional and dips break the count. Both
   recorded in dead_ends.md.

## Claims logged

- C0029: N(r) <= 3r for every stale row, closing (B1) via BHMS §8.8 q_n<=3n-1.
- C0030: N(r) <= 3r for all rows (equality only r=1); N(r) <= 2r for r>=2;
  proved for stale, numerical for live.
- C0031: A029900 and A029901 are exactly complementary (disjoint, cover all
  positive integers except 1).

## Next step

Close the live rows to get a complete uniform closed-form bound N(r) <= 3r (or
any linear bound) for ALL rows. Two concrete options:
(a) **Direct argument** analogous to BHMS §8.8 for live (period-1 and higher)
rows: bound the last "junk" q of a live row by a linear function of r, using
the diagonal/complement structure (C0031) and the fact that live rows are the
complement of stale rows in the row index.
(b) **Zeilberger route with (Z2).** (Z1) is closed (C0021: p-q <= 3r-1, so
M_r <= 3r-2). The only remaining gap is (Z2), a bound on lcm{period(c) : c<r}.
Observed periods are {1,2,3,4,6,8,9} with lcm 72 to r=50000; prove lcm <= 2^{O(r)}
or polynomial and the Zeilberger chain gives an explicit N(r) <= r^{O(r)} for
all rows. This is the single most valuable remaining piece.

The sharp strip bound |A029902(n) - a n| <= K (the renormalisation prize) is
still open and is NOT needed for effectivity -- C0029 shows a crude 3r bound
already closes B1. Decide next session whether to chase the sharp constant
(island charter) or first complete the closed form on live rows (cheap and
completes the target).

## Confidence

The thesis is alive and has just delivered a concrete closure: (B1) is done
via prior art, and the effectivity target is now reduced to the live rows +
(Z2). What would kill it: nothing found this session threatens the main line;
the diagonal-cocycle and overlap-identity failures are negative results that
only narrow the route. The remaining risk is that live rows resist a linear
bound by a direct argument and (Z2) (lcm of periods) turns out to be the hard
part -- but even then the Zeilberger recursion C0024/C0028 is already effective
(computable from solved rows), so the project target (effective Byrnes) is
already met in the recursion sense; only the closed form needs (Z2).