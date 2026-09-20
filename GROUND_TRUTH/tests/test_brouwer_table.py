"""Brouwer's published table of f(q,r) for q, r <= 24, cell by cell.

Source: https://aeb.win.tue.nl/games/chomp.html, section "A small table".
This is the tightest check there is: 325 independently published cells.
"""
from __future__ import annotations

from .. import chomp
from .common import Fail, brouwer_table, check


def test_small_table(ctx) -> str:
    ref = brouwer_table()
    tab = chomp.table(24, 24)
    bad = [(q, r, tab[q][r], v) for (q, r), v in sorted(ref.items())
           if tab[q][r] != v]
    if bad:
        raise Fail("f(q,r) disagrees with Brouwer at %d of %d cells; first: "
                   "(q=%d,r=%d) solver=%d published=%d"
                   % (len(bad), len(ref), *bad[0]))
    return f"{len(ref)} published cells (r<=q<=24) all match"


def test_above_diagonal(ctx) -> str:
    """f(q,r) = f(q,q) for r > q -- the verticals-are-constant clause."""
    tab = chomp.table(24, 24)
    for q in range(25):
        for r in range(q + 1, 25):
            check(tab[q][r] == tab[q][q],
                  f"f({q},{r})={tab[q][r]} but f({q},{q})={tab[q][q]}")
    return "f(q,r)=f(q,q) for all r>q, q<=24"


def test_diagonal_is_column_max(ctx) -> str:
    """Brouwer: f(q,q) is the largest element of column q.  Proved on his page,
    so a violation means the solver, not the theorem, is wrong."""
    n = min(400, max(60, ctx.max_r))
    tab = chomp.table(n, n)
    for q in range(n + 1):
        m = max(tab[q][r] for r in range(q + 1))
        check(tab[q][q] == m,
              f"column q={q}: max is {m} but f(q,q)={tab[q][q]}")
    return f"f(q,q) = max of column q for all q <= {n}"


TESTS = [test_small_table, test_above_diagonal, test_diagonal_is_column_max]
