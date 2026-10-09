# Referee attempts that did not move a claim

Despite the directory name, **nothing here means the claim is invalid.** A file
lands here whenever a referee run ends without an agreed `accept` or `reject`.
The claim keeps its status and stays refereeable.

| suffix | meaning |
|---|---|
| `unresolved.N` | both passes finished but disagreed (e.g. `accept` vs `accept_with_gaps`). An open question, not a refutation. |
| `inconclusive.N` | at least one pass produced no verdict. A harness failure; says nothing about the mathematics. |
| `harness-failure`, `split-mishandled` | early runs (2026-09-21) whose verdicts were wrongly applied and then reverted; see OPERATOR_NOTES_ARCHIVE.md s3a, s3b. |

`N` counts the attempts on that claim (`../attempts.json`).

**A verdict here may describe text that no longer exists.** If the proof file
changed after the run, the quoted gaps refer to the old version. Check the
run's date against `git log` on the proof before acting on it. For example,
`C0032.unresolved.2` and `C0033.unresolved.2` judged the text before the
2026-10-07 rewrite.

The directory keeps its name because `harness/referee.py`, `ops/digest.py`
and `ops/recover_referee.py` all read it, and because every verdict since
2026-09-21 cites paths under it.
