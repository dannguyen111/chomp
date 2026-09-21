## State

The target is a strip bound: prove `|A029902(n) - a n| <= K` for an explicit
computable `K`, `a = 1 + sqrt(2)/2` (equivalently A029901 about `b n`,
`b = 1 + sqrt(2)`). This discharges (B1) of `GROUND_TRUTH/byrnes_audit.md` and
makes Byrnes effective. Numerics measured and saturating: `|A029902(n)-a n| <= 1.853`
and `|A029901(n)-b n| <= 3.908` over all 29289 stale rows to r=50000 (Brouwer's
strips match exactly).

This session sharpened the target and then stress-tested the main route:

- **C0016**: strip bound ⟺ bounded discrepancy `D(x) = #{A029902<=x} - x/a`,
  via `A029902(n) - a n = -a D(A029902(n))`; measured `D(x) in [-0.871, 1.085]`.
- **C0015/C0019**: the discrepancy satisfies the exact integer cocycle
  `D(x) + D(floor(bx)) in {-1,0,1}` (equiv `N(x)+N(floor(bx)) = 2x + {-1,0,1}`),
  verified for every x with bx <= 50000.
- **C0017**: `A029902(n) = f(n,n) + O(1)` (in {-3..1}), `A029901(n) = 2 A029902(n) - n + O(1)`
  (in {-1..3}); `2a-1 = b` exactly.
- **C0018**: the stale/live indicator word has maximal factor complexity (not
  Sturmian, not low-complexity).
- **C0014**: H&L Theorem 3.3 gives no error term; their Conjecture 5.1 is our
  strip bound, open.

## This session

Read Hegarty-Larsson in full (C0014): Theorem 3.3 gives only asymptotic density,
no error term; Conjecture 5.1 *is* the strip bound, stated open — so the Phase 0
pointer does not pay out directly.

Computed the structure of A029901/A029902 from the census and a self-contained
Python solver (scratch/diag_solver.py). Found the discrepancy reframing (C0016),
the exact integer self-similarity (C0015, sharpened to the clean integer form in
C0019), the diagonal bridge (C0017), and the negative result that the word is
maximal-complexity (C0018).

**Then ran the kill test I flagged in the previous handoff** (the most important
thing this session): does the self-similarity alone force D bounded? **No**
(C0020). The cocycle `D(x)+D(bx) in {-1,0,1}` is satisfied by the explicit
unbounded function `D(x)=(-1)^k k`, `k=floor(log_b x)`. So the self-similarity is
a *consequence* of the mex structure, not a sufficient condition. Route A as
stated is dead; the mex structure must be used.

## Claims logged

- C0014: H&L Theorem 3.3 gives no error term; their Conjecture 5.1 is our strip bound, open.
- C0015: exact self-similarity `D(x)+D(bx) in {-1,0,1}`.
- C0016: strip bound ⟺ bounded discrepancy, via `A902(n)-a n = -a D(A902(n))`.
- C0017: `A902(n)=f(n,n)+O(1)`, `A901(n)=2 A902(n)-n+O(1)`, `2a-1=b`.
- C0018: indicator word has maximal factor complexity (not Sturmian).
- C0019: exact integer cocycle `N(x)+N(floor(bx))=2x+{-1,0,1}`; alternating-sum formal solution.
- C0020: NEGATIVE — the cocycle alone does not force D bounded (explicit counterexample).

## Next step

Pursue **Route B (the diagonal bridge, C0017)** or augment the cocycle with the
mex structure. Two concrete options:

1. **(Augmented cocycle.)** The full functional description is
   `D(x) - D(x-1) = [x in A902] - 1/a` together with the greedy mex generation
   of A902 (which is exactly the 3-row recurrence restricted to diagonal
   P-positions). The counterexample in C0020 violates the jump condition
   (its jumps are not 0/1-valued in the right pattern). Test whether
   jump-condition + cocycle + `e in {-1,0,1}` forces D bounded; if a
   counterexample still exists, the mex *generation* (not just the jump pattern)
   is the essential input.
2. **(Diagonal strip via recurrence.)** `A902(n) = f(n,n) + O(1)` (C0017) means
   the strip bound is equivalent to a strip bound on the diagonal `f(q,q) ~ a q`.
   Byrnes' Lemma 5 gives the linear bound `f(r,r) <= 4r-1`; the recurrence
   `f(q,q) = mex({f(a,q):a<q} u {f(q,b):b<q})` is a self-map that may be
   contractive in the strip metric. Attack that directly.

Option 2 is the most likely to produce a constant and is closest to Island 01's
proved Lemma 5 territory; option 1 is the more faithful renormalization route.
Do whichever yields a *constant* first.

## Confidence

Alive, and one dead end is now cleanly identified (the self-similarity alone is
insufficient — this is real progress, not just a negative: it tells us the mex
structure is the essential input, not a decorative consequence). The target is
bounded discrepancy of one set, with the mex generation of A902 as the
constraint. What would kill the thesis: if the augmented cocycle (jump condition
+ self-similarity) also admits an unbounded counterexample, then the full mex
generation is needed and we should go straight to Route B's diagonal recurrence.