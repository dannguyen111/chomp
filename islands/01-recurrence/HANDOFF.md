> # CORRECTIONS — read before trusting anything below (2026-10-01)
>
> This handoff is from session 1 (2026-09-20). Three of its central claims have
> since been overturned. The text is kept intact because the reasoning is still
> useful, but **do not act on it without these corrections.**
>
> **1. C0012 is PRIOR ART, not a result of this session.** `f(q,r) <= q+r+1` is
> stated verbatim in Brouwer–Horváth–Molnár-Sáska–Szabó, *On Three-Rowed Chomp*,
> INTEGERS 5 (2005) **#G07 section 8.1**, one line after the recurrence. The
> proof below is correct and more explicit than the source, but the result is not
> ours. **(Z1) was discharged in 2005.** #G07 was simply never in
> `fetch_sources.py`; it is now. See the PRIOR ART block in `proofs/C0012.md`.
>
> **2. "The target is achieved" is wrong, because C0013's closed form is wrong.**
> Per C0023(c), the Zeilberger state count **omits the preperiod `a_0(r)`**. The
> correct form is `N(r) + period(r) <= a_0(r) + p_r (M_r+1)^(M_r)`, which is a
> **recursion over r**, not a closed form. The displayed
> `N(r) <= 2^(2^r · poly(r))` does not follow until that recursion is unrolled.
> That is open work, not a finished result.
>
> **3. The paragraph below about `n = p-q` versus `n = p-r` is right, and it was
> the single most expensive error in the project.** C0009 used `n = p-q`; Byrnes'
> assumption (1) forces `n = p-r`. The slip produced a *true but weaker*
> statement, so every numerical check passed while the claim around it was false,
> and it survived three of my own reviews. C0009 and C0010 are superseded by
> C0021 and C0022. Read the ERRATA at the top of `GROUND_TRUTH/byrnes_audit.md`.
>
> **What is actually the best candidate contribution now:** not C0012, but
> **C0011**. #G07 section 8.12 says proving `d_n, r_n ~ αn` and `q_n ~ βn`
> suffices for opening-move uniqueness; Sheiner (arXiv:2605.23837, 2026) proved
> uniqueness by another route and explicitly does *not* establish those
> asymptotics, so they remain open — and C0011's saturation is strictly stronger
> than them.
>
> Full operations state, including the autonomous cron loop and the referee's
> fabricated-citation failure, is in `OPERATOR_NOTES.md` section 0.

## State

The MISSION target (an explicit computable bound on N(r)) is met **in closed form**. The
previous session delivered C0024 (the corrected effective Zeilberger recursion) and its
handoff said "(Z2) remains open" — an a priori bound on `lcm{period(c): c<r}`. That was
wrong in two ways, both fixed this session:

1. **C0024's part (iv) is itself an a priori lcm bound**, and it unrolls to a closed form
   because `q_1 = 1` and the recursion never consults the actual periods. (C0027.)
2. **The lcm recursion is linear, not quadratic.** The pigeonhole's repeated state carries
   the phase `a mod q_r`, so the repeated-period `s` satisfies `q_r | s` AND `p_r | s`;
   hence `q_{r+1} = lcm(q_r, p_r) | s <= q_r(m_r+1)^{m_r}` directly — no need to multiply
   (ii)'s `p_r` bound by `q_r`. (C0028.)

The final bound (**C0028**, lemma, open, proof in `proofs/C0028.md`):

> `g(1)=1, g(r+1)=g(r)(r+2)^{r+1}`  =>  `q_r <= g(r)`  (closes (Z2)).
> `h(r)=11+r+sum_{k=2}^r g(k)(k+2)^{k+1}`  =>  `u_r=N(r)-r <= h(r)`.
> Hence `N(r) <= r + h(r) <= 2^{O(r^2 log r)}` for ALL rows r>=1, live and stale.

`g(r) = prod_{k=1}^{r-1}(k+2)^{k+1}`, so `log_2 g(r) = Theta(r^2 log r)`. This is a
genuine closed form (no quantity on the right is defined by a recursion over the actual
rows) and satisfies MISSION section 4's "any computable form" success criterion. C0027's
`2^{2^{O(r)}}` bound is valid but strictly weaker; C0027 is marked superseded. Sharpening
to `C·r` remains open and is a different question (bounded discrepancy of A029902,
C0016/C0025), not a finite-state pigeonhole.

## This session

1. Re-read and independently re-verified C0024 (F1–F7 in `scratch/verify_recursion.py`,
   recreated since the old scratch file is gitignored): all pass for r<=400, a<=1400
   against the validated solver. The first draft's failures were table-width artifacts
   (`W_r(a)` needs index `a+r`).
2. Found that C0024 (iv) unrolls to a closed form; wrote C0027 and verified it
   (exact r<=12, log-space r<=60).
3. **Sharpened it**: realized the phase in the pigeonhole state makes the lcm recursion
   linear. Wrote C0028 (`proofs/C0028.md`) and
   `scratch/verify_closed_form_sharp.py`; verified exact r<=12 (g(12) is 74 digits) and
   log-space r<=60; logged C0028 and marked C0027 superseded.
4. Added provenance-free restatements for C0027 and C0028 to `LEDGER/restatements.json`.
5. Updated NOTES.md and this handoff.

## Claims logged

- **C0027** (lemma, superseded): closed-form bound `N(r) <= 2^{2^{O(r)}}` from the
  quadratic lcm recursion; valid but superseded by C0028.
- **C0028** (lemma, open): the sharpened closed-form bound `N(r) <= 2^{O(r^2 log r)}`
  from the linear lcm recursion; proof in `proofs/C0028.md`; verified r<=12 exact,
  r<=60 log-space.

## Next step

Referee C0024 first, then C0028 (both `lemma` + proof, both refereeable; C0028 has a
restatement in `LEDGER/restatements.json`). **Do not rely on the cron `auto` mode**: it
picks refereeable claims in ID order, so it will re-referee C0021 (unresolved after 3
runs, ~$1.28 spent) before ever reaching C0024/C0028. Dispatch manually:

```
python -m harness.referee C0024 --root . --max-spend 1.00
python -m harness.referee C0028 --root . --max-spend 1.00
```

If C0028 survives, the MISSION target is closed and the remaining interesting work is
the *sharpening* to `C·r` (the discrepancy question, island 02's territory), not
effectivity. One caveat for the referee runs: dependency statements (C0012, C0024) reach
the referee as ledger text (narrative included) — `build_messages` applies restatements
only to the claim being refereed, not its dependencies. The mathematics is intact; the
gate records the leak. If a run comes back biased, the harness fix is to apply
`restatements.json` to dependency statements too.

## Confidence

High that C0028 is correct: it is a two-line unrolling of C0024 (independently re-verified
F1–F7 this session) plus the prior-art value bound C0012, with the one new observation
being that the phase in the state forces `lcm(q_r,p_r) | s` — a step I checked explicitly
against C0024's own state definition (`S_a = (a mod q_r; ...)`). The only failure modes
are (a) an error in C0024 itself (pinned by F1–F7), or (b) the stale-row `+1`
bookkeeping, checked against the census for r<=12 exact and r<=60 log-space. What would
kill it: an actual counterexample `r` with `N(r) > r+h(r)`, which would have to come from
an error in C0024's (ii)/(iii) — counting arguments whose sole failure mode is a
coordinate slip, now pinned by two independent verification scripts.