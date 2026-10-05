# Lean

The Lean work lives in a **private** repo, `dannguyen111/chomp-lean`,
cloned into this folder as `chomp-lean/`. Everything here except this
README is gitignored.

It is private because it builds on Erez Sheiner's Lean 4 formalization of
arXiv:2605.23837v2, which he shared by email on 2026-10-03 and has not
published. Nothing from that archive goes into this public repo or into its
Actions logs. That includes source, excerpts and build output.

    gh repo clone dannguyen111/chomp-lean GROUND_TRUTH/lean/chomp-lean

## What is machine-checked

Sheiner's archive proves the following for the function defined by the
actual game, not just for a recurrence model. It uses Lean 4.29.1, the
standard library only, and the standard axioms only:

- f(q,r) is well defined: the encoded P-position exists, is unique and is
  complete (Lemma 2.1);
- f satisfies the two-branch Brouwer recurrence, including its mex branch;
- f(q,0..q) are distinct (Lemma 2.3(a)), and Lemma 2.3(b), printed with "="
  where "≠" is meant;
- the diagonal is the column maximum, and f(q,q) > q (Lemma 4.1);
- every 3×n rectangle has exactly one winning opening move (Theorem 1.1).

For the ledger, this means:

| claim | status |
|---|---|
| C0045 | Sheiner's recurrence at q=r=n: formalized upstream |
| C0080 | Lemma 2.3(a)-(b): formalized upstream |
| C0060 | its premise (P) is Lemma 4.1, which is formalized upstream |

Our own Lean lemmas go in `chomp-lean/ChompPreperiod/`, on top of
`ChompPreperiod/Base.lean`. CI there checks every push.
