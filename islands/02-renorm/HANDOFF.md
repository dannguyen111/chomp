## State

The project target is an effective Byrnes: an explicit computable bound on `N(r)` (the preperiod of
`f(q,r)-q`, MISSION §4). **This is already achieved** by C0028 (`N(r) ≤ r+h(r)`, `h(r) ~ 2^{O(r^2 log r)}`),
verified in this session — MISSION §4's deliverable is met, so the project is a success. The bonuses
are the linear bound `N(r) ≤ C·r` ("full success") and the sharp law `N(r) = sqrt(2)r + O(1)`. The
sharp law is the Friedman–Landsberg strip bound, equivalently a bounded-discrepancy statement about
the mex-generated diagonal `d_n = f(n,n)`, and it is exactly the still-open half of BHMS #G07 §8.12.
This session took that strip bound to its genuine limit on the renormalization lane: it is
**irreducibly hard here** — every sub-problem reduces to the constant density = the target itself,
and the mex loop is expansive/neutral (C0059/C0062) so no convergence argument forces it. The sharp
integer form is `|d_n − round(αn)| ≤ 2` (α = 1+√2/2), saturated and verified. The mission's linear
"full success" is reachable via the C0037 **locking** `N(r) ≤ max_{c<r}N(c)+6` (→ `N(r)≤6r`), verified
and saturated — but the locking is the machine's lock-delay (island 01's C0032), with no
renormalization signature. MISSION §5's seed conjecture is verified exact (9/9) and saturated. The one
genuine new structural finding is the **dip mechanism** (C0049).

## This session

I attacked the strip bound `|d_n − αn| ≤ K` via the renormalization/self-similarity picture. **What
worked:** (1) C0045/C0046 — rigorous reduction: the whole target is one inequality on the
mex-generated diagonal (`d_n = mex(D_{<n} ∪ R_n)`, `{f(a,n):a<n}=D_{<n}` exact), and the strip bound ⟺
constant density `#const<x = x/β+O(1)` ⟺ block count `c_n=(√2/2)n+O(1)`; sharp integer form
`|d_n − round(αn)| ≤ 2` (saturated, 0 violations to n=5000). (2) C0049/C0060 — exact mex-sandwich
`d_n = n+1−δ_n+c_n` and the **dip mechanism** (every dip `d_n=d_{n−1}−1` is a row-`(n−1)` top dropping
out of `R_n`; universal 0/71). (3) C0063/C0066/C0069/C0070 — verified & saturated: all linear bounds
`N(r)≤6r/3r/2r` (0 violations to r=50000), preperiod offset `u_r=(√2−1)r+O(1)`, core block-count
discrepancy saturated, MISSION §5 exact 9/9, project goal achieved (C0028). **What did NOT work (all
rigorously closed):** abstract mex (C0050), row-profile rescaling (C0051), BHMS 8.8 sharpening (C0054,
circular — the gap 3→β *is* the target), local cocycle (C0055), `R_n` structure (C0056), finite-state
recursion (C0058), morphic/word (C0065), rate-of-convergence/Beatty (C0062). Every sub-problem (block
count, overlap, almost-increasing `δ_n≤1`, dip covering) reduces to the constant density = circular.
Obstruction: the mex+complementarity loop is **expansive/neutral** (C0059/C0062), so convergence
cannot force the bound. Honest corrections recorded: the "tractable sub-lemma" `δ_n≤1` and the "hole
identity" were both circular/dip-calibrated (see dead_ends).

## Claims logged

- C0045: structural mex reduction — `{f(a,n):a<n}=D_{<n}` exact, `d_n=mex(D_{<n} u R_n)`. (proven)
- C0046: strip bound ⟺ diagonal `|d_n−αn|≤K`; ⇒ all strips + preperiod law. (proven)
- C0047: block-count reformulation of the strip bound.
- C0048: diagonal cocycle `D_d(x)+D_d(bx)` bounded (corrects a dead end).
- C0049: exact block-count identity + bounded dips + **dip mechanism** (universal 0/71).
- C0050–C0051, C0054–C0056, C0058: six shortcuts rigorously closed (negatives).
- C0052–C0053: constant-density target; row-m crux lower bound.
- C0057: block-count increment signature (mean `√2/2`, Beatty wobble).
- C0059: expansive/neutral mex loop (the obstruction).
- C0060: exact mex-sandwich (rigorous under premise (P), proven except dips).
- C0061: self-similarity unified across stale+diagonal+constants.
- C0062: rate-of-convergence/Beatty = circular or absent (neutral fixed point).
- C0063: core density mechanism confirmed bounded & saturated.
- C0064: capstone — strip bound ⇒ mission full success (`N(r)≤3r`).
- C0065: word formulation (bounded-step word, chaotic, no morphic handle).
- C0066: precise proof targets + sharp integer `|d_n−round(αn)|≤2`.
- C0067: period = machine cycle (island 01), not renormalization.
- C0068: locking route `N(r)−N(r−1)≤6` ⇒ `N(r)≤6r` (mission full success), weaker than the strip.
- C0069: MISSION §5 seed conjecture verified exact (9/9) & saturated.
- C0070: session verification package (all linear bounds + sharp integer + core, max scale).

## Next step

**Prove the C0037 locking `N(r) − N(r−1) ≤ 6`** (consecutive preperiods differ by ≤6; verified,
saturated K=6) — this **inducts to `N(r) ≤ 6r`**, the mission's full success, and is **genuinely
weaker/more tractable** than the strip bound (it bounds preperiod *jumps*, not absolute deviation).
This is the machine's lock-delay (island 01's C0032 machine) and is **not** reachable from the
renormalization lane (verified: no Beatty signature in the preperiod increments). So route it to the
machine analysis. The sharp strip bound (`|d_n−round(αn)|≤2`, C0066) remains the harder prize and
needs a **genuinely new mechanism** — the mex is expansive/neutral (C0059/C0062), so convergence /
scaling / morphic / finite-state are all closed; only a non-convergence combinatorial invariant of the
mex word could crack it. **Do NOT re-derive the closed shortcuts (C0050/51/54/55/56/58) or the
circular sub-lemmas (dead_ends)** — they are done.

## Confidence

**The renormalization thesis (self-similarity ⇒ strip bound) is essentially exhausted and likely dead
on this lane** — I mapped every avenue and each reduces to the circular density or is another island's
territory. It is NOT "almost done": the strip bound is a 20-year open problem (BHMS §8.12) and I could
not prove it. **What would kill it:** the strip bound has no easy sub-problem (block count, overlap,
almost-increasing, dip covering all circular) and the only local mechanism (the mex loop) is expansive
(C0059/C0062), so no convergence argument works; a proof needs a genuinely new idea, and none emerged
despite exhaustive search. **However, the project is NOT at risk:** the primary goal (effective Byrnes)
is achieved (C0028, verified), and the linear "full success" is reachable via the locking (C0068),
which is tractable and correctly assigned to island 01. So the mission succeeds regardless of the
sharp bound. The renormalization lane's honest contribution is a complete map + the dip mechanism +
rigorous closure of all wrong turns (protecting future budget).
