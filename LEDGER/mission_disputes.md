# Disputes with MISSION.md

MISSION.md is immutable. Disagreements go here, with evidence, and the human
decides. One entry per dispute.

---

## 2026-09-20 (Phase 0) -- MISSION section 3's blanket non-effectivity claim is too strong for the 3-row case

**MISSION.md section 3 says:**

> **Byrnes (2003), poset game periodicity.** For each fixed `r`, the quantity
> `p - q` over P-positions `(p, q, r)` is *eventually periodic* in `q`. The
> proof is non-constructive in the relevant sense: it yields no computable bound
> on when periodicity begins or how long the period is. Zeilberger wrote an
> exposition.

**The dispute.** The first sentence of the second claim is right about
*Byrnes' general poset-game proof*. It is not right about *Zeilberger's
exposition*, which is a different proof of the 3-row case, and the difference
changes what this project should spend money on.

**Evidence.** See `GROUND_TRUTH/byrnes_audit.md` for quotes and page numbers.
In summary:

1. In Byrnes' proof the only non-computable quantity is `W(A,k)`, which traces
   back to a single step -- the converse direction of Lemma 4, which extracts two
   integers `M`, `N` from the bare finiteness of a set. Everything else,
   including the Lemma 9 pigeonhole, is explicit. So MISSION's claim is correct
   for Byrnes, but it is correct for a *narrower and more actionable* reason
   than "the proof is non-constructive".

2. Zeilberger's proof does not contain that step. His Ultimate-Periodicity
   Theorem pigeonholes over the state space
   `S_a = (I_a ; L_{a-1}, ..., L_{a-M})`, which he counts explicitly, giving
   `N(r) + period(r) <= p_r * (M_r + 1)^{M_r}` where `M_r` bounds `p - q` below
   `r` and `p_r = lcm{period(c) : c < r}`. Zeilberger says so himself: *"The
   'theoretical' upper bound for the period is enormous, but is hardly (and
   perhaps never) achieved."* An enormous bound is still a computable bound, and
   MISSION section 4 explicitly counts *"a bound of any computable form"* as a
   success.

3. `M_r` and `p_r` are supplied by the induction but not bounded a priori. The
   `M_r` half is **already half-proved inside Byrnes' own paper**: his Lemma 5
   is unconditional and gives `(p-q) - (q-r) <= |A| = 3r - 1`, hence
   `f(r,r) <= 4r - 1`. The solver confirms this over every P-position with
   `q, r <= 2000`, with equality at `(3,1,1)`.

**What I am *not* claiming.** I am not claiming the target of this project is
already solved. The gap is real: Zeilberger's route still needs (a) that
`max_q (f(q,r) - q)` is attained near `q = r` rather than far out, and (b) a
bound on `lcm{period(c) : c < r}`, which is MISSION's own open secondary target.
Nor am I claiming the bound would be good -- it is `r^{Theta(r)}` against a truth
of `sqrt(2) r`.

**Why it matters for the budget.** MISSION section 3 says of the proven results
"do not attack these", and section 4 frames the target as making a
non-constructive proof effective. If an explorer reads section 3 literally it
will go hunting for a compactness step in Zeilberger that is not there, and burn
a session. The correct framing for both islands is in
`GROUND_TRUTH/byrnes_audit.md` section 3: three named, quantitative sub-targets,
two of which are partially discharged by lemmas already in print.

**Requested resolution.** No change to MISSION.md (it is immutable, and the
dispute is about emphasis rather than fact). The island NOTES.md files carry the
corrected framing, and `byrnes_audit.md` is prepended by reference. A human
should confirm this reading before an explorer session acts on it, because it
redirects the primary line of attack.

### RESOLVED 2026-09-20 -- approved by the project owner

The redirect is authorised. Explorer sessions should treat
`GROUND_TRUTH/byrnes_audit.md` section 3 as the operative statement of the
primary line of attack, and MISSION.md section 3's "yields no computable bound"
as true of Byrnes' general poset-game theorem only.

Concretely, the approved order of attack is:

1. **(Z1-residual)** show `max_q (f(q,r) - q)` is attained within `O(1)` of
   `q = r` (Byrnes' Lemma 5 already gives the `q = r` case);
2. then write out the Zeilberger chain for an explicit `N(r) <= r^(O(r))`,
   conditional on (Z2);
3. **(B1)** bound the last `q` at which a stale row carries a P-position --
   this is `W(A,0)`, the one quantity Byrnes leaves uncomputable.

Island 02 opens on the equivalent form of (B1): an explicit strip bound
`|A029902(n) - a n| <= K`.

Neither island is to attack the pigeonhole in Byrnes' Lemma 9 or in
Zeilberger's Ultimate-Periodicity Theorem. Both are already explicit; that is
the trap this dispute exists to close off.
