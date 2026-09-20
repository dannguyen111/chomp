# MISSION: Effective Byrnes for 3-Row Chomp

This file is immutable. It is prepended to every session, unchanged, byte for byte.
Do not edit it. If you believe it contains an error, write to `LEDGER/mission_disputes.md`.

---

## 1. The game

Chomp on a 3×n board. A position is a triple `(p, q, r)` with `p >= q >= r >= 0`,
denoting row lengths. A move removes a square and everything above and to the right.
The square `(1,1)` is poisoned; whoever takes it loses.

A **P-position** is one where the player to move loses under optimal play.

## 2. The recurrence (Brouwer, Horvath, Molnar-Saska, Szabo 2005)

Define `f(q, r)` = the unique `p` such that `(p, q, r)` is a P-position.

```
if r > q:                f(q,r) = f(q,q)
elif f(q-1,r) < q:       f(q,r) = f(q-1,r)
else:                    f(q,r) = mex over { f(a,r) : a < q } U { f(q,b) : b < r }
```

where `mex` is the smallest positive integer not in the set. This recurrence is the
single source of truth for this project. Everything you claim must be consistent with it.

## 3. What is already PROVEN (do not attack these)

- **Byrnes (2003), poset game periodicity.** For each fixed `r`, the quantity `p - q`
  over P-positions `(p, q, r)` is *eventually periodic* in `q`. The proof is
  non-constructive in the relevant sense: it yields no computable bound on when
  periodicity begins or how long the period is. Zeilberger wrote an exposition.
- **Sheiner (arXiv:2605.23837, May 2026).** Every 3×n Chomp rectangle has exactly one
  winning opening move. This settles the three-row case of Gale's 1974 uniqueness
  question and proves that A029900 and A029901 are complementary. **This is solved.
  Do not work on it.**
- **Brouwer et al. (2005).** A cubic-time algorithm for the P-positions, and: from the
  initial position there are infinitely many winning moves in the third row.
- 2×n Chomp: P-positions are exactly `(a+1, a)`. Square boards: take `(2,2)`, then mirror.

## 4. What is OPEN

- **Zeilberger's BIG PROBLEM.** A poly-log (in `p+q+r`) characterization of the losing
  positions. Out of scope — too hard for this budget.
- **THE TARGET (this project).** Make Byrnes effective. Specifically:

  > Let `N(r)` be the least `q0` such that for all `q >= q0`, the sequence `f(q,r) - q`
  > is exactly periodic. **Prove an explicit computable bound on `N(r)`.**

  A bound of the form `N(r) <= C·r` for any explicit constant `C` is a full success.
  A bound of any computable form (`C·r log r`, `C·r^2`, anything effective) is a
  success. A bound conditional on a clearly stated and numerically well-supported
  lemma is partial success and still worth writing up.

- **Secondary target** (pursue only if the primary stalls): bound the *period* itself.
  Observed periods up to `r = 10,000` are only 2, 3, 4 and 9. Whether periods are
  bounded as `r -> infinity` is open.

## 5. The seed conjecture

**Status: CONJECTURAL, verified only against the published table. Verify before use.**

From Brouwer's published `(r, start)` pairs for the first observed non-trivial patterns:

| r    | start | start/r |
|------|-------|---------|
| 120  | 170   | 1.4167  |
| 400  | 566   | 1.4150  |
| 422  | 597   | 1.4147  |
| 513  | 725   | 1.4133  |
| 576  | 814   | 1.4132  |
| 861  | 1217  | 1.4135  |
| 888  | 1255  | 1.4132  |
| 2027 | 2867  | 1.4144  |
| 6541 | 9250  | 1.4142  |

The ratio appears to converge to `sqrt(2)`, tightening as `r` grows. Hence:

> **Conjecture N.** `N(r) = sqrt(2)·r + o(r)`.

This is plausibly connected to the Friedman-Landsberg renormalization picture, in which
A029900 grows like `(1 + sqrt(2)/2)·n` and A029901 like `(1 + sqrt(2))·n`, both derived
from *unproven* scaling assumptions about P-positions lying on three lines in the p-q
plane. If those constants and this one share a source, a proof of one may illuminate
the others.

Note the asymmetry: proving `N(r) <= C·r` for a crude explicit `C` (say `C = 100`) is
worth far more than sharpening the constant to `sqrt(2)`. **Effectivity beats sharpness.**
Do not chase the exact constant at the expense of any bound at all.

## 6. Ground truth

`GROUND_TRUTH/` contains a solver implementing §2, validated against:
- Brouwer's small table of `f(q,r)` for `q, r <= 24`
- OEIS A029899, A029900, A029901, A029902, A029903, A029904, A029905, A069001
- The `r = 120` anomaly: for large `q`, `f(q,120) = q + const + (-1)^q`
- Nivasch's full period census to `r = 10,000` (periods 2, 3, 4, 9)

The solver is **read-only to you**. You may write new analysis code in your island's
`scratch/`, but you may not modify the solver. If you believe the solver is wrong, file
a claim of type `solver_bug` with a reproducing input; do not patch it yourself.

## 7. Verification standard

A claim is `PROVEN` only when it has a human-readable proof that survives an adversarial
referee who sees the proof but not its provenance. Numerical agreement is *evidence*, never
proof. The recurrence is checkable to `q, r <= 130,000` (Brouwer's published range), so any
false lemma about `f` is cheap to kill — kill your own lemmas before the referee does.

## 8. The ledger

`LEDGER/claims.jsonl`, append-only. One JSON object per line:

```json
{"id":"C0017","statement":"...","type":"lemma|conjecture|observation|solver_bug",
 "status":"open|evidence|proven|refuted|superseded","proof_ref":"islands/01/proofs/C0017.md",
 "evidence":"verified for r <= 20000, no counterexample","verified_range":"r<=20000",
 "depends_on":["C0003","C0011"],"novelty_checked":false,"session":"S07"}
```

Never edit a line. To change a status, append a new line with the same `id`; last write wins.
`LEDGER/dead_ends.md` is equally important — an idea that failed, with the *reason* it
failed, saves a future session real money.

## 9. Budget

This project has a hard total budget of $30 across all sessions, roughly 8-12 explorer
sessions in total. There is no "run it again tomorrow." Every session is a meaningful
fraction of the whole. Act accordingly: prefer one deep line of attack to five shallow ones,
and write down enough that the next session does not repeat your work.
