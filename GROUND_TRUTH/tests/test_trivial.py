"""The cases that were settled before anyone wrote a program.

If the solver gets these wrong it is not a subtle bug, it is the wrong game.
Sources: Schuh (1952), Gale (1974), and Brouwer's "Trivial cases" and
"3-by-n Chomp" sections.
"""
from __future__ import annotations

from .. import chomp
from .common import check

# Brouwer, verbatim: "If r = 1, the only P-positions are (3,1,1) and (2,2,1)."
SMALL_ROWS = {
    1: [(3, 1), (2, 2)],
    3: [(6, 3), (7, 4), (5, 5)],
    4: [(8, 4), (9, 5), (10, 6), (7, 7)],
}


def test_two_row_chomp(ctx) -> str:
    """r = 0 is 2-by-n Chomp: the P-positions are exactly (a+1, a)."""
    n = min(ctx.max_r, 5000)
    for q, p, _ in chomp.row(0, qmax=n):
        check(p == q + 1, f"f({q},0) = {p}, expected {q + 1}")
    return f"f(q,0) = q+1 for every q <= {n}  (2-by-n: P-positions are (a+1,a))"


def test_r_equals_two(ctx) -> str:
    """r = 2: the P-positions are exactly those with p = q + 2."""
    n = min(ctx.max_r, 5000)
    for q, p, _ in chomp.row(2, qmax=n):
        if q < 2:
            continue
        check(p == q + 2, f"f({q},2) = {p}, expected {q + 2}")
    return f"f(q,2) = q+2 for every 2 <= q <= {n}  (p-q = 2)"


def test_small_finite_rows(ctx) -> str:
    """r = 1, 3, 4: Brouwer lists every P-position; there must be no others."""
    for r, pairs in SMALL_ROWS.items():
        got = [(p, q) for q, p, _ in chomp.row(r, qmax=4000) if q >= r and p >= q]
        check(got == sorted(pairs, key=lambda t: t[1]),
              f"r={r}: P-positions {got}, Brouwer lists {sorted(pairs, key=lambda t: t[1])}")
    return "r=1 -> {(3,1,1),(2,2,1)}; r=3 -> 3 positions; r=4 -> 4 positions, exactly"


def test_r_equals_five(ctx) -> str:
    """Brouwer: r=5 gives (10,5,5), (9,6,5) and (a+11, a+7, 5) for a >= 0."""
    rows = chomp.row(5, qmax=4000)
    d = {q: (p, dd) for q, p, dd in rows}
    check(d[5][0] == 10, f"f(5,5) = {d[5][0]}, expected 10")
    check(d[6][0] == 9, f"f(6,5) = {d[6][0]}, expected 9")
    for a in range(0, 3990):
        q = a + 7
        check(d[q][0] == a + 11, f"f({q},5) = {d[q][0]}, expected {a + 11}")
    return "r=5: (10,5,5), (9,6,5), then (a+11,a+7,5) for every a <= 3989"


def test_square_boards_are_N_positions(ctx) -> str:
    """m-by-m Chomp is a first-player win, so (q,q,q) is never a P-position:
    equivalently f(q,q) > q for every q."""
    n = min(ctx.max_r, 3000)
    tab = chomp.table(n, n)
    for q in range(n + 1):
        check(tab[q][q] > q, f"f({q},{q}) = {tab[q][q]}, must exceed q")
    return f"f(q,q) > q for every q <= {n}  (no square board is a P-position)"


def test_p_position_antichain(ctx) -> str:
    """For fixed r, at most one p per q and at most one q per p -- otherwise
    one P-position would be reachable from another."""
    n = min(ctx.max_r, 2000)
    tab = chomp.table(n, n)
    for r in range(0, min(n, 400) + 1):
        seen: dict[int, int] = {}
        for q in range(r, n + 1):
            p = tab[q][r]
            if p < q:
                continue                      # not a genuine P-position
            check(p not in seen,
                  f"r={r}: (p={p}) occurs for q={seen.get(p)} and q={q}")
            seen[p] = q
    return f"P-positions form a partial matching in (p,q) for every r <= {min(n, 400)}"


TESTS = [test_two_row_chomp, test_r_equals_two, test_small_finite_rows,
         test_r_equals_five, test_square_boards_are_N_positions,
         test_p_position_antichain]
