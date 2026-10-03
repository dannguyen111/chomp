# HANDOFF — session S20261002T0953 (island 01-recurrence)

## State

The MISSION target (any computable bound on `N(r)`) is met in closed form by
**C0028** (`N(r) <= 2^{O(r^2 log r)}`, proof in `proofs/C0028.md`; two addenda
this session fixed presentation gaps and the referee's one named gap `p_r | s`,
now proved via the subtraction-closed set of periods). C0024 and C0028 remain
`open` pending the referee: one run completed, t=0.3 died to harness/network
flakiness, t=0.8 returned **accept_with_gaps** with no objection to the bound.
The remaining frontier is the sharpening **`N(r) <= C r`**. This session built
the recurrence-internal attack's concrete form: an exact finite machine for
each row (C0032, proved), an explicit determinism onset
`sigma_r = max_{c<r} N(c) - r` (C0033, proved), the flagship locking conjecture
`N(r) <= max_{c<r} N(c) + 6` (C0037, inducts to `N(r) <= 6r`), and the plug-run
conjecture (C0039) reduced to one falsifiable statement about periodic tails:
**no 8 one-per-row tail-value matches can cover 8 consecutive columns**
(c0 = 7 verified on the complete census: 75821 heptads, 0 octads). Proved
along the way: the single-row run lemma (C0041). Three attractive stories were
refuted and corrected in the ledger (pure-poset route C0042; onset alignment
C0043 correction; sqrt(2)-saturation C0044 correction).

## This session

1. Adversarial review of C0024/C0028: verified Zeilberger's Lemma Bounded
   (source ~line 612) carries the `m_r` step; patched C0028 (Addendum 1: stale
   case of Lemma A'; `h(r-1) >= r+1` by induction; Addendum 2: the `p_r | s`
   step the referee flagged — periods closed under subtraction).
2. Derived and validated the merged-trail machine (C0032): `V'` decays exactly
   like the mex-trail, so `H_{a+1} = dec(H_a) u {mex(V''(a) u H_a) - 1}`
   generates `B_r` exactly (validated vs solver, all rows r<=300).
3. Found the determinism onset `sigma_r` (C0033) and measured the lock delay
   (C0034): `u_r - sigma_r = N(r) - max_{c<r}N(c) in [-4,+6]` to r=50000.
4. Identified the mechanism (C0035 staircase = repeated-p* columns; C0036
   attractors; C0040 run-death: long runs die of validity q>p*, medium runs of
   coincidence failure) and refuted the naive routes (C0038, C0042).
5. Proved C0041 (single-row run lemma): post-onset each witness row covers at
   most `p_c` consecutive columns of a plug run (unit descent vs periodicity).
6. Plug-run hunts: tables r<=800/1200/1800 gave max 6; the complete-census
   scan (`scratch/hunt_full.cpp`, all 50000 rows' periodic tails, all
   q<=72000) gives **max 7, 75821 heptads, 0 octads** — the constant drifts
   with range (5->6->7), so always test on census tails, never small tables.
7. Heptad anatomy (C0043, population-corrected): exactly one witness per
   column, 7 distinct rows one column each (150/150 sampled); the
   "tail-onset alignment" story is refuted (offsets spread from 69 up).
8. C0044 and its correction: the sqrt(2) saturation of q0/cstar is mostly the
   admissibility filter speaking (slack q0-M[cstar] spans 0..9521); survives:
   the boundary is attained (slack 0..2 runs exist) and octads exist nowhere.
   The proof must work uniformly in slack; the N-law link is speculation only.
9. Referee C0028 run (INCONCLUSIVE overall; t=0.8 accept_with_gaps, gap
   patched). Two earlier dispatch attempts died to session wall-clock caps.

## Claims logged

- **C0032** (lemma, open, `proofs/C0032_machine.md`): merged-trail machine
  `H_{a+1}=dec(H_a) u {mex(V''(a) u H_a)-1}` generates `B_r` exactly.
- **C0033** (lemma, open, same proof): determinism onset
  `sigma_r = max_{c<r} N(c) - r`.
- **C0034** (observation, evidence): lock delay `u_r - sigma_r in [-4,+6]` to
  r=50000; abstract machines do NOT share this (transient ~2.4M, C0038).
- **C0035** (observation): `V''(a)` = column `q=a+r` of f minus q; plug
  staircases = fixed `p*` recurring in consecutive columns (runs reach 177+
  with transients; 7 without).
- **C0036** (observation): attractors — interval fixed points `[0,k-1]`,
  termination, p-cycles of AP-mod-p unions; basin-dependent.
- **C0037** (conjecture, open): `N(r) <= max_{c<r}N(c) + 6` => `N(r) <= 6r`;
  any explicit K gives `N(r) <= K r` (full success). THE flag.
- **C0038** (observation): abstract-machine transients grow ~2.4M even at
  q=1,p=1 — the O(1) lock is chomp-specific.
- **C0039** (conjecture, open): post-onset plug runs <= absolute c0; c0 = 7 on
  the COMPLETE census (75821 heptads, 0 octads at q<=72000); consequence
  `N(r) <= 9r` at c0=7. Cheap falsifier: an 8-run in extended tails.
- **C0040** (observation): run-death mechanism + plane antichain reframing.
- **C0041** (lemma, open, `proofs/C0041_single_row.md`): single-row run lemma —
  post-onset a witness row covers <= p_c consecutive columns.
- **C0042** (observation): refutation of the pure-poset route (c=0 line is an
  antichain of size p*; P-position plane sections reach 459) + the interleave
  target.
- **C0043** (observation, population-corrected): heptad anatomy — one witness
  per column, 7 distinct rows one column each; onset-alignment story refuted.
- **C0044** (observation, corrected): heptads touch the admissibility boundary
  (slack 0..2 exist) but are not pinned there (slack up to 9521); sqrt(2)
  saturation was mostly the filter. Proof must be uniform in slack.
- **C0028 evidence update**: referee t=0.8 accept_with_gaps; the named gap
  `p_r | s` proved in Addendum 2.

## Next step

1. **Do not run the referee.** (Operator, 2026-10-03.) Your shell no longer
   has the API key, so `harness.referee` will fail, and refereeing your own
   claims is not your job: the scheduled `referee.yml` runs it daily and
   C0024, C0028 are next in its queue. C0024 already has a restatement.
   Spend the session on the mathematics below.
2. **The 8-run falsifier hunt** (cheapest disproof of C0039): extend the
   census past r=50000 and re-run `scratch/hunt_full.cpp`; record the max
   before stating any sharp K. An octad falsifies the absolute-constant
   conjecture and with it the `N(r) <= K r` route via plug runs.
3. **The interleave proof** (if no octad): no 8 one-per-row tail-value
   matches (rows c, values `g_c(q)=q+B_c(q-c)`, one column per row) can cover
   8 consecutive columns — uniformly in slack (per C0044's correction), with
   the 75821 heptads as the sharp cases. Attack via SAT/ILP over
   (period, phase, values) tuples or the mex structure of the tails directly.
   At c0=7 this yields `N(r) <= 9r` (empirically `N(r) <= 2r`).

## Confidence

High in C0032/C0033/C0041 (algebraic proofs, solver-validated). C0039 is the
load-bearing conjecture: verified on every datum that exists (complete census,
zero counterexamples), falsifier precisely defined and cheap, sharp cases
enumerated. What would kill it: an 8-run in extended tails; note the constant
has drifted 5->6->7 with range, so do not hard-code 7 in any theorem statement
beyond "absolute constant (currently 7 on all available data)". C0028's bound
survived adversarial self-review and one referee pass (accept_with_gaps, gap
patched); its only remaining risk is referee scrutiny of C0024's (ii)-(iii),
whose mechanism (Zeilberger's Lemma Bounded) was verified against the source
this session. Session discipline note: three self-interpretations were
overturned by population checks (C0043, C0044, c0 constants) — the next
session should keep testing extremal-example stories on populations before
building on them.
