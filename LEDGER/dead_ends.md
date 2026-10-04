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

### 2026-10-03 -- CORRECTION: "diagonal has no clean cocycle" is WRONG (see C0048)
**Tried:** transfer the self-similarity cocycle to the diagonal discrepancy
(this is the 2026-10-01 dead end "Diagonal discrepancy has no clean
self-similarity cocycle", which concluded it drifts and is absent).
**Correction:** The diagonal DOES have a bounded cocycle. Measured
`D_d(x)+D_d(floor(bx))` over x<=2473 (diagonal to n=3500): bounded
`[-0.774,2.551]`, slope-vs-log-x = 0.018 (negligible drift), decade ranges
saturated. The old dead end's `[-2.77,-0.42]` was the d_0-EXCLUDED counting
(constant offset -1.63); with d_0 included it is `[-0.77,2.55]`. In both
normalizations it is BOUNDED (constant-offset, not literally {-1,0,1}, but no
drift). So the C0015 self-similarity and the C0045 mex coexist on the SAME
object (the mex-generated diagonal).
**Revisit if:** THIS IS THE LIVE ROUTE. Self-similarity + mex on one object is
the intended Route A setup. The remaining step is to prove the mex FORCES
bounded discrepancy given the bounded cocycle (C0020/C0026 show cocycle alone
is not enough). See C0048, C0045, C0047.

### 2026-10-03 -- Route A (abstract self-similarity + mex -> bounded discrepancy) is DEAD (C0050)
**Tried:** prove the strip bound from the abstract mex `d_n = mex(D_{<n} u R_n)` +
the self-similarity cocycle + monotonicity (C0049 dips<=1) + block-count identity +
complementarity -- i.e. every structure the prior claims assembled.
**Failed because:** the abstract mex does not constrain the slope/discrepancy at all.
Adversarial `R_n = [1,t_n)\D_{<n}` forces any target `t_n` (any slope), giving
`|d_n - alpha n|` unbounded (explicit: slope 1.807 -> 40, slope 1.4 -> 123, 400 steps,
all `|R_n|<=n`). The block-count identity (C0049) holds for EVERY mex-generated
sequence, so it is not a discriminator. And any increasing slope~alpha sequence is
mex-realisable (`R_n`=gaps, `|R_n|=d_n-n-1<=n`), so the C0026 cocycle-compatible
unbounded-discrepancy words are mex-realisable too: even mex + cocycle allow unbounded
discrepancy. So NO abstract renormalisation/mex argument can prove the strip bound.
**Revisit if:** never, as an abstract argument. The strip bound is forced ONLY by the
specific GAME structure of `R_n = {f(n,b): b<n}` (the row-n P-position tops). The live
route is to find a self-similarity / invariant / counting law SPECIFIC to R_n (how the
constants and row tops are laid out in row n), not of the diagonal abstractly. This is
the real content of the Friedman-Landsberg renormalisation and it lives in the game, not
in mex combinatorics. See C0050, C0045, C0049.

### 2026-10-03 -- Row-profile rescaling across r is NOT a renormalisation (C0051)
**Tried:** find the charter's "picture rescales across r" as an affine rescaling of
individual row profiles `f(n,b)/d_n` (row n vs row n/gamma, both aligned and via CDF).
**Failed because:** (a) aligned profiles match only to the natural staircase variance
(~0.13-0.17) with NO preferred gamma; (b) the normalized CDF F_n(v) is UNIVERSAL --
every row has the same shape (mean|F_n-F_m|~0.001 for ALL pairs, controls included), so
the CDF shows no rescaling scale at all. The row picture does not rescale.
**Revisit if:** never, as a row-profile statement. The genuine self-similarity is the
VALUE-DOMAIN cocycle D(x)+D(bx) of the diagonal/stale sets (C0048, a rescaling of the
value SEQUENCE x->bx by b=1+sqrt(2)), not of row geometry. Seek the self-similarity in
how the game lays out the value SETS across rows, not in row profiles.

### 2026-10-03 -- Positive note: BHMS 8.10 witness law is exact (do not re-derive)
Not a dead end but a verified constraint. For c=q_m (the m-th constant), the number of
pairs (q,r) with q<c and f(q,r)=c is EXACTLY m (25/25 verified). This is a concrete
game law on R_n (each constant has exactly m row-witnesses) and may be the counting
input the R_n self-similarity needs. See C0047 (c_n=#constants<d_n) + this = the count
of constants witnessed by row n below its mex.

### 2026-10-03 -- Sharpening BHMS 8.8 from 3 to beta is CIRCULAR (C0054)
**Tried:** push BHMS 8.8's contradiction from constant 3 to beta=1+sqrt(2) (the C0053
crux lower bound s(m)>=m/beta), using the exact witness law as the sharpening input.
**Failed because:** reconstructing BHMS 8.8 with general slope c shows the pigeonhole
needs the hole X - dcount(X) >= n where dcount(X)=#{i<2n-1: d_i<=X} is the DIAGONAL
COUNT. With the crude bound d_i>=i+1 (C0012) this forces c>=3 exactly (BHMS's 3 is
tight for the method, saturated at c=3). With the true diagonal density d_i~alpha*i the
threshold drops to c~beta -- so the gap 3->beta IS the diagonal strip bound (C0046).
Knowing dcount to that precision = knowing the diagonal density = the target. Circular.
Also the BHMS argument is stuck at c=3 under the crude bound (c in [a+1,2a-1] minimized
at a=2,c=3). So there is NO independent sharpening of BHMS 8.8.
**Revisit if:** never as an independent route. The target is the diagonal strip bound /
constant density (C0046/C0052) itself; attack it directly via the value-domain cocycle +
mex on the diagonal (C0048) or the game structure of R_n (C0050), not via BHMS 8.8.

### 2026-10-03 -- "Almost-increasing" sub-lemma (delta_n<=1) is CIRCULAR (= the strip bound)
**Tried:** prove the bounded-dip lemma delta_n = #{a<n: d_a>=d_n} <= 1 (diagonal almost-increasing)
as a "smaller true thing" toward the strip bound.
**Failed because:** delta_n = 2n - |D_{<n} cap R_n| - d_n + 1 exactly, so delta_n<=1 <=> overlap
|D cap R| >= 2n-d_n, and the overlap is the DENSITY (C0063) = the strip bound. Measured
overlap-(2n-d_n)=1 (delta_n=0 at non-dips). So proving delta_n<=1 requires the full strip bound.
NOT a smaller problem -- it is the target restated.
**Revisit if:** never as a "tractable sub-lemma". The strip bound has no easy sub-problem; the
density is irreducible. Only a genuinely new mechanism can prove it.

### 2026-10-03 -- "Hole identity" (2 holes = {f(n,b),f(n,b+1)}) is DIP-CALIBRATED (circular)
**Tried:** identify the 2 holes in S_b below d_n as the row values {f(n,b),f(n,b+1)} -- looked like
a structural (non-circular) identification.
**Failed because:** adversarial test at NON-dip columns refuted it: at n=144 b=140 holes=[242,244],
b=141 holes=[243], b=143 holes=[244] -- holes differ, count varies 1..7. Only at the dip column
b=n-2 are the holes exactly {f(n,b),f(n,b+1)}. So the identification is CALIBRATED to the dip
column = CIRCULAR (encodes d_n), not structural.
**Revisit if:** never as a non-circular identification. Lesson: an apparent mechanism that holds
only at extremal/dip columns is a coincidence, not a lemma. Always adversarially test at
neighboring columns.

### 2026-10-03 -- Rate of convergence / Beatty modulation of preperiod = circular or absent
**Tried:** (a) the charter's "rate of convergence to the fixed point" as an independent handle;
(b) a Beatty modulation of the preperiod increments N(r)-N(r-1) as a renormalisation structure.
**Failed because:** (a) the rate #{const<x}/x -> 1/beta has x*|diff| bounded = the strip bound
(circular); (b) the increment "wave" has amplitude ~2.3 for ALL theta (sqrt2,alpha,beta) = the
general spread, not a specific Beatty frequency. So no renormalisation signature in the
preperiod increments -- the locking is the machine's (island 01 C0032).
**Revisit if:** never for the locking from the renormalisation side; route it to the machine.

### 2026-10-04 -- Counting inequality over value-fibers is NOT the interleave proof
**Tried:** explain the run bound (max 7) by a pigeonhole over value-fibers: the
fiber of value v is the c-interval [(v-1.5)alpha, (v-0.5)alpha) (alpha = 1/(2-sqrt2)),
consecutive fibers are alpha-spaced and each contains the stale row r_{v-1}, so
8 consecutive values would need 8 fibers served by only ~6 live rows.
**Failed because:** (a) long G-runs of consecutive VALUES exist (up to 18, e.g.
v=29111..29128) with multi-period rows double-serving values (row 49558 serves
both 29030 and 29032), so value-count is not binding; (b) the binding constraint
is PHASE ALIGNMENT -- a period-p row offers its different values at different
phases, so it cannot occupy two rungs of one run; the run bound is about
anti-diagonals in the (phase, height) table, not value counts; (c) the premise
"each fiber contains stale row r_{v-1}" has 89 exceptions in 28999 (the strip
error 1.853 exceeds the fiber half-margin 0.5*alpha = 0.854), so it is not even
true uniformly and any proof using it needs a sharper strip (|r_n - alpha n| <
0.85) or a direct argument.
**Revisit if:** a phase-aware counting lemma is found: e.g. bound the number of
consecutive anti-diagonal cells coverable by rows whose phase-value functions
v_c(phi) are p_c-periodic with v_c = round((2-sqrt2)c)+{0,1}. The phase-injectivity
(c -> v_c(phi) injective at each phi, C0075) is the constraint a pigeonhole must use.

### 2026-10-04 -- Greedy generation of the p1 value sequence from the Beatty skeleton is FALSE
**Tried:** generate the period-1 tail values from the row index alone: v_c =
round((2-sqrt2)c)+1 if free else round((2-sqrt2)c) (and lo-first variants), with
multi-period rows contributing their value sets as they arrive in c-order.
**Failed because:** the rule mispredicts exactly the 866 dip rows, and at EVERY
dip row the preferred (high) value was FREE (866/866) -- the dips are not
collision-forced; the offset choice carries extra mex/basin information (C0036:
which fixed point the machine reaches is basin-dependent). So the sharp value
law C0077 (v_c = round(theta*c)+{0,1}) does NOT close into a generation rule,
and the interleave bound cannot be proved from value law + injectivity + fill.
**Revisit if:** the dip set is characterized (necessary conditions known:
both neighbours stale 866/866, frac(2 theta c)<=0.5 for 859/866, density
0.04376 ~ theta^2/8 = 0.04289; not sufficient). A closed dip rule would turn
the value law into a generation rule and make the run bound pure combinatorics.

### 2026-10-04 -- Naive SAT over (value law + free deltas) is trivially SAT (do not run it)
**Tried:** decide the interleave bound by SAT over rows = (period | 72, phase
offset, {0,1}-dip) with the measured laws as constraints, asking for an 8-long
anti-diagonal.
**Failed because:** with the class pattern (stale/live) and the delta pattern
free, the model admits 8-runs immediately -- the census contains 36 explicit
windows where 8 consecutive values are assignable under free deltas (C0083),
e.g. rows 3202..3217 carrying 1877..1884. So SAT returns SAT and tells you
nothing; the real content is the delta pattern (and the multi-period phase
alignment), which the abstract model does not constrain. Constraining the
stale pattern to its real form = re-checking the data; constraining it to
"discrepancy <= K" = the strip bound (the hard open target).
**Revisit if:** the delta rule (C0082) is known -- then SAT over the remaining
freedom (multi-period band shapes + phases) is a meaningful decision problem.
The finite dissection (36 windows, all failing on the real delta pattern) is
the replacement task; see C0083 and the handoff.

### 2026-10-04 -- Cheap correlates of the dip set delta_c=0 all fail
**Tried:** characterize the 866 dip rows (v_c = round(theta*c), C0082) via
N(c) parity, (N(c)+c) parity, (N(c)-c) mod 3, and proximity to the diagonal's
own dip events (C0049's d_n = d_{n-1}-1 rows, 43 of them <= 3000).
**Failed because:** parity and mod-3 are balanced in both classes (dips
385/481 on N-parity vs norm 9733/9189; mod-3 284/293/289 vs 6240/6322/6360);
distance to nearest diagonal dip: p1 dips sit 1-13+ away (3 at distance 1,
spread out), while NORMAL rows are at distance 0-7 at least as often (17 at
distance 0 in a 2000-row sample). So the delta rule is not a parity/N/diagonal-
dip function; it is basin content of the C0032 machine (C0036, C0082).
**Revisit if:** someone has a global characterization (e.g. via the machine's
attractor selection or the value-set holes G of C0076); local correlates are
exhausted at this level of generality.

### 2026-10-04 -- Dip rule is NOT diagonal-avoidance (A029900 not a forbidden set)
**Tried:** explain the delta choice (C0082) as avoidance of the diagonal set:
v_c takes lo (dips) when hi = round(theta*c)+1 collides with a diagonal value.
**Failed because:** p1 values are diagonal values FREELY (693 of 1182 p1 rows
<=3000 have v_c in the diagonal); at dips only 26/49 have hi diagonal (vs ~50%
baseline), and normal rows take a diagonal value as hi 662/1133 times. So the
diagonal is not avoided and carries no selection information for delta.
**Revisit if:** never as avoidance. The dip rule remains basin content of the
C0032 machine; the C0085 tie-in (stale-cluster fibres) is the live handle.

### 2026-10-04 -- Dip rule is not a local function of the class word, u_c, or conservation
**Tried:** (a) decide delta_c from the class-word window (stale/p1/multi) on
c-k..c+k, k<=5, with and without the frac(2 theta c) bin; (b) delta_c as a
function of u_c = N(c)-c alone or (u_c, round(theta c) parity); (c) value law
as a function of the preperiod via conservation, v_c = 2c - N(c) + eps.
**Failed because:** (a) ambiguity persists and GROWS with k (k=5: 17 ambiguous
patterns still cover 9503 of 19788 rows); even the dominant pattern SPS|frac-L
is mixed 9135/859. Real signal exists but is non-deterministic: all dips are
SPS (both neighbours stale), and the k=2 dip rate is 13.3% at PSPSS vs 1.3% at
PSPSP (the c+2 class matters). (b) u_c -> delta has 384 conflicting rows;
(u_c, parity) -> delta has 183. (c) v_c - (2c-N(c)) spans {-2..6} with counts
{0:4707, 1:9581, 2:3912, 3:918, 4:473, 5:176, 6:16} -- O(1) but not a function.
**Revisit if:** someone has the machine-level basin selection rule (C0032/C0036);
every finite-window and single-variable correlate at this level is now ruled
out, so do not re-test them. The C0085 stale-cluster fibre configuration and
the k=2 asymmetry (PSPSS vs PSPSP) are the surviving partial signals.

### 2026-10-04 -- CORRECTION: "dip rule is not a local function of the class word" is only true for SMALL k (see C0086)
**Correction to the entry above ("Dip rule is not a local function of the class
word, u_c, or conservation"):** the k<=5 verdict was right but the conclusion
"determined by global structure" was WRONG. Extending the same test to k<=32
with shuffle controls shows delta IS a deterministic function of the class word
on [c-30, c+30] (W_30 groups pure at 100k: 39356 groups, 0 mixed; shuffled
control gives 16.4 mixed groups -- not vacuous). The u_c/conservation and
diagonal-avoidance negatives stand unchanged. Lesson: when an ambiguity count
decreases monotonically with the window (96.6%->48% for k=1..5), run the window
to its resolution point with a shuffle control before calling the route dead.
**Revisit if:** this IS the live route (C0086): enumerate the class-word windows
admitting the delta staircase and prove the recurrence cannot realize them.

### 2026-10-04 -- CAVEAT (not a dead end): 'absolute c0=7' vs 'probabilistic c0 drift' is NOT decided by current data
**Tried:** use the pair-surrogate (C0092) to argue the run bound follows from
the pair potential.
**Failed because (as a proof):** the staircase pattern's pair energy under J is
FAVORABLE (3-dip suffix: 2J(1)+J(2) = +1.9), so under the pair measure the
per-window octad probability is ~p^3 e^{1.9} (1-p)^5 ~ 6e-4 -- rare, NOT
forbidden. Over the 36 windows of the 100k census that predicts 0.02 expected
octads (observed 0: trivially consistent); extrapolated rate ~2e-7/row puts
the first octad near rows 5e5..1e6 -- REMARKABLY close to the threshold-ladder
extrapolation R_8 ~ 5.6e5. So the current data cannot distinguish:
(A) an absolute bound c0=7 (C0039 as stated), from
(B) a probabilistic c0 that drifts 5->6->7->8... at extreme r (same range-drift
    lesson as C0003/C0037 sup-saturation and the c0 drift itself).
If (B) holds, the plug-run route yields N(r) <= (c0(r)+2) r with c0(r) growing
like log-ish -- NOT a constant C, so MISSION's 'full success' would need a
different argument (though N(r) = O(r log log r)-ish would still beat C0028).
**Revisit if:** the census is extended past 5e5 rows (the decisive range for an
octad). An octad at ANY r falsifies the absolute-constant form of C0039 but
NOT the locking C0037 (which needs O(1) runs at each r, and would then need
runs bounded by a slow function). State the C0039 consequence as 'c0 absolute
(currently 7)' only with this caveat attached.

### 2026-10-04 -- PITFALL: machine simulation needs QMAX >= 2*cmax (table truncation fakes law failures)
**Tried:** verify the C0093 envelope/wobble laws at 4x scale (rows c in
[700,1124]) using chomp.table(cmax, cmax+60).
**Failed because:** the machine probes q = a + c up to ~2c+10; with QMAX =
cmax+60 the table is truncated and B(cp, a+c-cp) silently returns None, so
k* gets stuck at a constant (523) and M-c collapses (-59..-233), faking 4
wobble-decomposition 'failures'. Rerun with QMAX >= 2*cmax + margin: all 14
rows pass every law, k* matches the census exactly. Lesson: when simulating
row c, always set QMAX >= 2c; cross-check k* against the census tail value
(it must equal v_c) before trusting any statistic.
**Revisit if:** never -- the pitfall is documented; the census cross-check
(k* == v_c) is the cheap guard.

### 2026-10-04 -- LESSON (third occurrence): a sampled maximum is not a supremum
**Tried:** treat max top - 2c = +3 (from a 5% sample sweep over c in [300,5000])
as the constant in the 2c peak law.
**Failed because:** a targeted 200-row scan over [200,1500] found +4 at 2 rows
(~1% rate) the sweep missed. C0094's O(3) corrected to O(4) (true sup unknown).
Same failure mode as c0 drift (5->6->7) and C0003's strip sup (5.696->5.755):
every 'saturated/maximum' claim on this project must carry its sampling rate.
**Revisit if:** never -- always report the sample size next to any maximum, and
state 'at least K' rather than 'K'.
