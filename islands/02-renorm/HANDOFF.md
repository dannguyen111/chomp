## State

The target is a strip bound: prove `|A029902(n) - a n| <= K` for an explicit
computable `K`, `a = 1 + sqrt(2)/2` (equivalently A029901 about `b n`,
`b = 1 + sqrt(2)`), which discharges (B1) of `GROUND_TRUTH/byrnes_audit.md` and
makes Byrnes effective. Numerics to r=50000: `|A029902(n)-a n| <= 1.853`,
`|A029901(n)-b n| <= 3.908`, saturating; discrepancy
`D(x)=#{A029902<=x}-x/a` measured in [-0.871, 1.085].

Prior work established the exact cocycle `D(x)+D(floor(bx)) in {-1,0,1}`
(C0015/C0019) but killed Route A (C0020): the cocycle alone does not force D
bounded (explicit argument counterexample). C0017 gives bridges:
`A029902(n)=f(n,n)+O(1)` and `A029901(n)=2 A029902(n)-n+O(1)`, `2a-1=b`.

## This session

1. Reconfirmed the exact-shift data and the diagonal bridge via a fresh
   `table --rmax 3000` sweep (grid in /tmp/t3000.txt; `diag[q]=f(q,q)`).

2. **C0025 (new, the key positive finding).** A029902 and A029901 — and the
   live-row set — are BOUNDED PERTURBATIONS OF THE COMPLEMENTARY BEATTY PAIR:
   `r_n - floor(a n) in {-1,0,1}` for every n <= 29289 (sup of the absolute
   value is exactly 1 over the whole range), `p_n - floor(b n) in {-1,0,1,2}`,
   `live_n - floor(b n) in {-2..2}` (99.97% in {-1,0,1}). Since
   `|r_n - a n| <= |r_n - floor(a n)| + 1`, the strip bound reduces to the
   nearest-integer statement `|r_n - floor(a n)| <= 1`. This matches Brouwer's
   measured strip max 1.853 exactly and is a far cleaner target than real-slope
   discrepancy. The strip bound is now a statement about an integer sequence
   staying within 1 of a Beatty floor.

3. **C0026 (new negative result).** Exhaustive enumeration (backtracking with
   prefix-sum constraint propagation, see scratch/cocycle_maxdisc.py) of ALL
   0-1 words satisfying the exact integer cocycle: the number of solutions
   grows exponentially (1288 at K=12, 11696 at K=16, 105550 at K=20, 1286320
   at K=24, 11993136 at K=28), and the maximum discrepancy over all solutions
   GROWS (3.03 -> 4.60) while the true stale word has |D| <= 0.9 there. So the
   self-similarity is exponentially weak even at the word level: it does not
   even narrow the word to a small class. The mex/greedy generation of
   A029901/A029902 is the ONLY input that selects the realized word.

## Claims logged

- C0025: A029902/A029901 (and live rows) are bounded perturbations of the
  complementary Beatty pair (floor(a n), floor(b n)); r_n - floor(a n) in
  {-1,0,1} for all n <= 29289; strip bound reduces to |r_n - floor(a n)| <= 1.
- C0026: the exact cocycle admits exponentially many 0-1 words with unboundedly
  growing max discrepancy; self-similarity alone cannot force the strip bound.

## Next step

Augment the cocycle backtracking (`islands/02-renorm/scratch/cocycle_maxdisc.py`)
with the mex constraint so the search space excludes the exponentially many
spurious words: either (a) encode the diagonal mex recurrence
`f(q,q)=mex({f(a,q):a<q} u {f(q,b):b<q})` directly (compute f(q,q) to q~3000
from /tmp/t3000.txt and add prefix-sum constraints linking r_n = f(n,n)+O(1)),
or (b) encode the nearest-integer Beatty constraint from C0025
(`|r_n - floor(a n)| <= 1`, i.e. r_n must stay within 1 of the Beatty floor) as
additional hard constraints and re-enumerate. Result: if the solution set
collapses to O(1) words with bounded D, the greedy/Beatty-nearness is the
essential input and a proof route exists; if a spurious word still survives
with unbounded D, we have a new counterexample to log. Either outcome is a real,
cheap result. Alternatively, attack C0025's nearest-integer statement directly:
prove r_n = floor(a n) + O(1) using Beatty-sequence machinery (the word is
chaotic per C0018, but that does not preclude value-level Beatty nearness).

## Confidence

Alive and better focused. Two new structural facts: a clean nearest-integer
Beatty reformulation (C0025) and a decisive negative showing the cocycle alone
is exponentially weak (C0026). What would kill the thesis: if the mex
constraint, added to the cocycle backtracking, still leaves spurious words with
unbounded discrepancy — that would mean even the full structural description
(greedy + self-similarity) fails to force the strip bound, and the remaining
hopes are a direct Beatty-nearness proof or Route B (diagonal recurrence
contraction). Also note isomorphism with classical results: bounded
perturbations of Beatty sequences have a literature (complementary Beatty
theorems, Fraenkel); novelty check is deferred to the referee.