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

### 2026-09-28 -- C0013's closed-form bound was wrong (superseded, don't reuse)
**Tried:** C0013 asserted N(r) <= Q(r-1)(r+2)^(r+1) with Q(r)<=Q(r-1)^2(r+2)^(r+1),
chaining C0012 into Zeilberger's state count as if it were a closed form.
**Failed because:** The state count `p_r(M_r+1)^(M_r)` omits the preperiod a_0(r) of the
instant-winner sequence W_r, so the displayed form is not a valid bound (C0023). Also it
omitted the phase `a mod q_r` needed to make the state transition deterministic.
**Revisit if:** not needed as-is -- C0024 is the correct recursion. A closed form still
requires (Z2) (an a priori lcm bound); C0024 supplies the recursion, not the closure.

### 2026-09-29 -- Word-level cocycle enumeration shows the self-similarity is exponentially weak
**Tried:** Enumerate ALL 0-1 words satisfying the exact integer cocycle N(x)+N(floor(bx))=2x+e(x), e in {-1,0,1} (C0019), to see if it pins down the stale word or at least forces |D| bounded.
**Failed because:** The cocycle admits exponentially many solutions (1288 at K=12 growing to ~12M at K=28), and the max |D| over all solutions grows with K (3.03 -> 4.60), while the true word has |D| <= 0.9. So the self-similarity does not even narrow the word to a small class, let alone force bounded discrepancy (C0026). The mex/greedy generation of A029901/A029902 is the only input that selects the realized word.
**Revisit if:** someone can encode the greedy mex rule as a constraint on prefix sums that can be added to this backtracking (then measure whether the solution set collapses to O(1) words with bounded D).

### 2026-09-29 -- Random/animated local search cannot find better cocycle words
**Tried:** Simulated-annealing / random-flip search over 0-1 words to find the max-discrepancy cocycle-compatible word at larger K (32..56).
**Failed because:** The search landscape is too rugged; best |D| found (3.75..4.12) is below the exhaustive result at K=28 already (4.60). Not a useful estimator of the true supremum.
**Revisit if:** a better repair operator (block moves) or LP/SAT encoding of the cocycle with a discrepancy objective.

### 2026-10-01 -- Diagonal discrepancy has no clean self-similarity cocycle
**Tried:** Transfer the exact cocycle `D(x)+D(floor(bx)) in {-1,0,1}` (C0015, valid for the STALE set A029902) to the DIAGONAL sequence A029900 `d_n=f(n,n)`, hoping to get a cleaner mex-recurrence + self-similarity pair on the diagonal (since the diagonal is mex-generated and A029901 is its complement).
**Failed because:** The diagonal discrepancy `D_d(x) = #{d_n<=x} - x/a` does NOT satisfy a bounded cocycle: measured `D_d(x)+D_d(floor(bx))` ranges over [-2.77, -0.42] for x<=1242, drifting, not in {-1,0,1}. The self-similarity is a property of the STALE SET A029902 (equivalently of the complement pairing), not of the raw diagonal. The diagonal only acquires the structure through the complement relation (C0031) and the bridge `A029902(n)=f(n,n)+O(1)` (C0017).
**Revisit if:** someone finds the correct "renormalization" object on the diagonal (e.g. a cocycle for the COMPLEMENT of the diagonal rather than the diagonal itself), or if the mex recurrence is reformulated directly in terms of A029901/A029902 without going through the diagonal discrepancy.

### 2026-10-01 -- The "overlap identity" d_n = 2n+1-overlap is false
**Tried:** Derive a clean closed form for the diagonal mex `d_n = mex({d_0..d_{n-1}} u {f(n,b):b<n})` by counting the overlap between the diagonal prefix and the row-n value set, hoping for `d_n = 2n+1 - overlap_n`.
**Failed because:** The identity fails at n=52 (d_52=88 but 2·52+1-overlap=89). The overlap set includes stale-row values (f(n,b)=dconst_b for stale b) that are NOT all below d_n, and the dip structure (d_n - d_{n-1} = -1 at 43 places <= 3000, caused by d_{n-1}-1 being a row value at n-1) breaks the naive count. The mex is genuinely 2-dimensional (row and column interact), no single overlap scalar closes it.
**Revisit if:** the overlap is decomposed by live/stale b and the stale contribution understood separately; the identity may hold with a correction term equal to the number of "dip" events, which is itself governed by the complement relation.
