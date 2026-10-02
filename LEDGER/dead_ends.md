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

### 2026-10-02 -- Inductive increment bound u_r <= u_{r-1} + 1 is false
**Tried:** prove N(r) <= 2r by showing the preperiod grows by at most 1 per row.
**Failed because:** 18340 violations to r=50000; increments u_r - u_{r-1} range
{-5,...,+5} with mode +2. N is not Lipschitz in r.
**Revisit if:** never; the running-max form (C0037) is the viable inductive
statement (N(r) <= max_{c<r} N(c) + K does not need consecutive-row control).

### 2026-10-02 -- Machine transient bounded by f(p,q) alone (independent of M)
**Tried:** prove the mex-shift machine's L-transient depends only on the input
period q and realized period p; that plus bounded periods would give N(r)<=C*r.
**Failed because:** transient grows ~2.4*M even at q=1, p=1 (random search:
t=96 at M=40; exhaustive t=12 at M=4,q=3). Pathological starts are sparse V
plus sparse H0; the decaying junk crosses the mex band for Theta(M) steps.
**Revisit if:** a bound in terms of (p, q, junk measure) where the chomp state at
sigma_r has provably small junk -- but the junk at sigma_r is NOT small in the
naive sense (holes at depths up to 175 below the mex; see below).

### 2026-10-02 -- Lock delay <= staircase length of V'' plug runs (as stated)
**Tried:** bound the machine lock delay by the length of descending plug
staircases in V'', identified with runs of a fixed p* as valid f-values in
consecutive columns (C0035).
**Failed because:** the table has runs of length 177 (p*=425, columns 249..425)
while the observed delay is <= 6. Either the long runs sit at hole heights far
from the mex band, or involve c >= r for the row in question, or the descending
hole synchronises into a p-cycle (periodic holes are fine -- L can be periodic
while holes descend cyclically, e.g. the r=120 p=2 attractor). A refined
statement must track the hole height relative to k and the c<r restriction.
**Revisit if:** one can prove that plug runs at heights within O(1) of the mex
are short for c<r (a 'near-mex staircase bound'), or that a descending hole
syncs into the attractor within O(1) of determinism regardless of run length.

### 2026-10-02 -- 'Clean state at determinism onset' in the naive sense
**Tried:** show the machine state at a=sigma_r is an interval minus O(1) junk
near the mex, which would lock in O(1) steps.
**Failed because:** holes below the mex at sigma_r sit at scattered depths (187
holes over 287 rows to r=300, depths 1..175 below k), and some rows show big
excess (up to 45 chips above a small mex k=3, which nonetheless lock in <=3
steps). The state is NOT naively clean; the locking mechanism is subtler (a
hole at the mex position is filled by the injection within 1 step, and holes
plugged by V'' either descend into the mex and get filled, or sync into a
p-cycle).
**Revisit if:** a potential function on (k, hole multiset, excess) can be found
that decreases within O(1) steps on chomp inputs.

### 2026-10-02 -- C0039's constant is NOT pinned at 5 (do not hard-code it)
**Tried:** treat the observed post-onset plug-run constant c0=5 (r<=400) as the
conjectured value.
**Failed because:** the counterexample hunt on table r<=800, q<=2200 finds
admissible runs of length 6 (c0 drifts 5 -> 6 when the table grows). The
conjecture to prove is 'absolute constant', and the C0037 consequence should be
stated as N(r) <= (c0+2) r generically.
**Revisit if:** extended hunts (larger tables) settle the constant; record the
max admissible run at each scale before stating any sharp K.

### 2026-10-02 -- The q0 >= max_{c<=cstar}N(c) squeeze needs the HARD half of the strip law
**Tried:** prove C0039's run bound via the post-onset admissibility squeeze:
long runs force growing witnesses (cstar ~ q0+t), and post-onset q0 >=
max_{c<=cstar}N(c) ~ 1.41*cstar contradicts that.
**Failed because (as a proof route):** the observed inadmissibility is
quantitatively driven by N(c) ~ sqrt(2)c (the LOWER bound on N), which is the
hard direction of the C0003 strip law and is NOT available from proved lemmas
(N(c) >= c is all C0012 gives). So the squeeze as measured is circular for the
C0037 goal unless the sqrt(2) slope can be extracted from the mex structure.
**Revisit if:** (a) a slope-free squeeze is found -- e.g. combine the witness
floor c >= h-1 (from f(q,c) <= q+c+1) with a structural witness-growth lemma
along runs (the per-column min-witness grows with q in every measured run);
or (b) a lower bound N(c) >= alpha*c with alpha>1 is proved directly from the
recurrence (this alone plus the squeeze would prove C0039).

### 2026-10-02 -- C0040's pure-combinatorics plane-antichain route is REFUTED
**Tried:** prove C0039 (and hence N(r) <= C r) from the move poset alone:
bound how many consecutive q the P-position antichain can meet inside a plane
c+a+b = p*.
**Failed because:** (a) the pure poset does not bound ANY antichain there --
the c=0 line {(0,a,p*-a)} is an antichain of size p* (brute-force BFS
refutation, plane_antichain.py); (b) the P-position antichain itself has
consecutive-q plane sections of length 459 (C0040). So no move-structure-only
argument can work; the mex content is essential.
**Revisit if:** never as stated. The salvage is C0041 + the interleave target
(C0042): post-onset each witness row covers <= p_c consecutive columns, and
the question is whether different rows' level-set pieces can interleave to
cover > c0 consecutive columns. That is a statement about periodic tails only.

### 2026-10-02 -- Long runs as post-onset adversaries (they are not)
**Tried:** treat the 459-long runs (C0040) as counterexamples to the lock
bound.
**Failed because:** they live PRE-onset for their witness rows (p*=1106 run
starts q=648 vs N(647)~915); by C0041 post-onset each witness row covers at
most its period p_c <= 9 consecutive columns. Post-onset long runs require
interleave across many rows, never observed beyond c0=6.
**Revisit if:** a post-onset run of length > 9 appears on a larger table --
that would be a multi-row interleave and the direct falsifier of C0039 at
c0=9; extend c0039_hunt.py to r<=3000+ to look for exactly this.

### 2026-10-02 -- SUPERSEDED: "c0 = 5" and "c0 = 6" (the constant is 7 on complete data)
**Tried:** pin the post-onset plug-run constant c0 from table hunts (5 at
r<=400 windows, 6 at r<=800/1200/1800 tables).
**Failed because:** the constant DRIFTS WITH RANGE. The complete-census tail
scan (hunt_full.cpp, all 50000 rows, all q<=72000) finds 75821 heptads and
max run = 7; the earlier tables could not see them because the heptad witness
rows have cstar ~ 18718, outside every earlier table's range. Lesson: test
plug runs on the periodic TAILS (census dvals), never on small f-tables.
**Revisit if:** the census is extended past r=50000 -- re-run hunt_full and
record the max before stating any sharp K; an 8-run would falsify the
absolute-constant conjecture and is the cheapest disproof test available.

### 2026-10-02 -- "Heptads are tail-onset alignments" (overfit to one instance)
**Tried:** explain maximal plug runs as 7 rows whose periodic tails BEGIN just
at the run (q0-N(c) in [1,18], a-u_c in [0,20]) -- inferred from the single
dissection of p*=37438.
**Failed because:** population check over 150 heptads (1050 columns): onset
offsets q0-N(c) start at 69 and spread well beyond; 0/1050 witnesses within
30 of onset. The one-instance story was overfit. What IS confirmed
population-wide (150/150): exactly one witness per column, 7 distinct rows
one column each. So the correct object is the one-per-row matching of tail
VALUES at scattered arguments, not onset windows.
**Revisit if:** never as stated; the corrected C0043 line has the right
picture. Lesson: dissect at least a sample of the population before building
theory on a single extremal example.
