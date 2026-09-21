# Dead ends

Append here. Each entry: what was tried, why it failed, and what would have to
change for it to be worth revisiting. An idea re-derived from scratch by a
later session costs ~10% of the total project budget.

## Format
### <date> -- <one-line description>
**Tried:**
**Failed because:**
**Revisit if:**

### 2026-09-21 -- H&L Theorem 3.3 does not deliver an error term
**Tried:** Use Hegarty-Larsson (INTEGERS 6 (2006) #A03) Theorem 3.3 to get the strip bound, per the Phase 0 pointer.
**Failed because:** Theorem 3.3 only yields the asymptotic density (L, l) via a Mobius-iteration fixed point; its proof explicitly says the convergence *rate* "is determined by M+, M-, S and the choice of starting point N only" and "We omit any further details". Their Conjecture 5.1 *is* the strip bound, and it is stated OPEN. So H&L is a statement of the target, not a route to it.
**Revisit if:** someone proves H&L Conjecture 5.1, or if the Mobius-iteration (Lemma 3.2) can be made quantitative (it has a contraction rate kappa_n that might be bounded below the fixed-point argument; that is the only place an error term could come from).

### 2026-09-21 -- Sturmian/morphic route to the strip bound is dead
**Tried:** Test whether A029901 (stale constants, density 1/b) is Sturmian/balanced/low-complexity, which would give discrepancy O(1) (equivalent to the strip bound) for free.
**Failed because:** The indicator word has essentially maximal factor complexity (c(k) reaches min(2^k, N-k+1) by k~40); it is NOT Sturmian (c(2)=4 not 3) and not of linear complexity. So the bounded discrepancy we observe (C0016) does NOT come from any low-complexity/Beatty-morphic structure.
**Revisit if:** A different notion of structure (e.g. the exact self-similarity D(x)+D(bx) in {-1,0,1} from C0015) can be leveraged directly, which is the live lead.

### 2026-09-21 -- Route A (self-similarity alone) is insufficient
**Tried:** Use the exact cocycle D(x)+D(floor(bx)) in {-1,0,1} (C0015) as a functional equation to force D bounded, the natural renormalization route.
**Failed because:** Explicit counterexample D(x)=(-1)^k*k with k=floor(log_b x) satisfies the same cocycle with e in {-1,1} but D is unbounded (C0020). So bounded discrepancy does NOT follow from the self-similarity alone; the self-similarity is a consequence of the mex structure, not a sufficient condition.
**Revisit if:** the cocycle is augmented with the mex constraint D(x)-D(x-1)=[x in A902]-1/a and the greedy generation of A902; that is the full functional description and might be contractive. Route B (diagonal bridge, C0017) is the fallback.
