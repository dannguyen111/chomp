"""An independent game-tree solver, checked against A069001 and against f.

Every other test in this directory checks that the solver implements the
Brouwer recurrence correctly.  This one checks something different and more
important: that the recurrence describes the actual game.  It plays 3-row Chomp
out by brute force from the rules -- chomp a square, remove its up-set, whoever
takes (1,1) loses -- with no reference to the recurrence at all, and then
demands that

  * its Grundy values reproduce A069001 (Grundy value of the 3 x n rectangle),
  * its P-positions are exactly the (f(q,r), q, r) with f(q,r) >= q.

A solver that passed everything else but failed here would be a correct
implementation of the wrong object.
"""
from __future__ import annotations

import sys
from functools import lru_cache

from .. import chomp
from .common import Fail, check, oeis


def _moves(p: int, q: int, r: int):
    """Every position reachable in one chomp from (p,q,r), poison included."""
    lam = (p, q, r)
    for i in range(3):
        for j in range(1, lam[i] + 1):
            nl = list(lam)
            for k in range(i, 3):
                nl[k] = min(nl[k], j - 1)
            yield (nl[0], nl[1], nl[2])


@lru_cache(maxsize=None)
def wins(p: int, q: int, r: int) -> bool:
    """True if the player to move wins.  The empty board means the opponent
    just ate the poison, so it counts as a win for whoever faces it."""
    if p == 0:
        return True
    return any(not wins(*m) for m in _moves(p, q, r))


@lru_cache(maxsize=None)
def grundy(p: int, q: int, r: int) -> int:
    """Grundy value of the game with (1,1) deleted: a move chomps any square
    other than the poison, and a player with no move loses."""
    s = set()
    for m in _moves(p, q, r):
        if m != (0, 0, 0):                 # taking (1,1) is not a legal move
            s.add(grundy(*m))
    g = 0
    while g in s:
        g += 1
    return g


def test_grundy_A069001(ctx) -> str:
    """Grundy value of the 3 x n rectangle, from the raw game tree."""
    ref = oeis("A069001")
    n = max(6, min(ctx.grundy_n, max(ref)))
    got = {k: grundy(k, k, k) for k in range(1, n + 1)}
    bad = [(k, got[k], ref[k]) for k in range(1, n + 1) if got[k] != ref[k]]
    if bad:
        raise Fail("A069001: %d of %d terms disagree; first n=%d brute=%d oeis=%d"
                   % (len(bad), n, *bad[0]))
    return f"A069001: Grundy(3 x n) matches for every n <= {n}"


def test_game_tree_agrees_with_f(ctx) -> str:
    """The real game's P-positions are exactly the ones f predicts."""
    n = max(6, min(ctx.grundy_n, 34))
    tab = chomp.table(n, n)
    bad = []
    for p in range(1, n + 1):
        for q in range(0, p + 1):
            for r in range(0, q + 1):
                actual = not wins(p, q, r)
                predicted = (tab[q][r] == p and tab[q][r] >= q)
                if actual != predicted:
                    bad.append((p, q, r, actual, predicted))
    if bad:
        raise Fail("game tree and f disagree on %d positions; first "
                   "(p,q,r)=(%d,%d,%d) actually-P=%s f-says-P=%s"
                   % (len(bad), *bad[0]))
    return (f"game tree and f agree on all {(n + 1) * (n + 2) * (n + 3) // 6} "
            f"positions with p <= {n}")


def test_grundy_zero_is_p_position(ctx) -> str:
    n = max(6, min(ctx.grundy_n, 30))
    for p in range(1, n + 1):
        for q in range(0, p + 1):
            for r in range(0, q + 1):
                check((grundy(p, q, r) == 0) == (not wins(p, q, r)),
                      f"({p},{q},{r}): grundy={grundy(p, q, r)} "
                      f"but P={not wins(p, q, r)}")
    return f"Grundy = 0 iff P-position, for every position with p <= {n}"


TESTS = [test_grundy_A069001, test_game_tree_agrees_with_f,
         test_grundy_zero_is_p_position]

sys.setrecursionlimit(100000)
