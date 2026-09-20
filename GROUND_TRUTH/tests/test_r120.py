"""The r = 120 anomaly -- the first row whose pattern is not constant or linear.

Brouwer: "after an initial amount of junk ending in (172,169,120) we get a
pattern a, a-1, a+2, a+1, a+4, a+3, ... that is, p = q + constant + (-1)^q",
and his (r, start, period, pattern) table records start = 170, period 2.
"""
from __future__ import annotations

from .. import chomp
from .common import Fail, check, r120_pvalues


def test_r120_published_values(ctx) -> str:
    """Every p that Brouwer printed for q = 120.. , value by value."""
    ref = r120_pvalues()
    got = {q: p for q, p, _ in chomp.row(120, qmax=max(ref))}
    bad = [(q, got[q], ref[q]) for q in sorted(ref) if got.get(q) != ref[q]]
    if bad:
        raise Fail("f(q,120) disagrees at %d of %d published q; first q=%d "
                   "solver=%d published=%d" % (len(bad), len(ref), *bad[0]))
    return f"{len(ref)} published values f(q,120), q=120..{max(ref)}, all match"


def test_r120_parity_law(ctx) -> str:
    """f(q,120) = q + const + (-1)^q for large q, and NOT before q = 170."""
    rows = chomp.row(120, qmax=1200)
    d = {q: dd for q, _, dd in rows}
    # the law, with const fixed from the tail
    tail = [d[q] for q in range(600, 1200)]
    const = (max(tail) + min(tail)) // 2
    check(max(tail) - min(tail) == 2,
          f"tail of d(q,120) spans {min(tail)}..{max(tail)}, expected exactly 2")
    for q in range(170, 1201):
        want = const + (1 if q % 2 == 0 else -1)
        check(d[q] == want,
              f"f({q},120)-{q} = {d[q]}, expected {want} = {const}+(-1)^q")
    return f"f(q,120) = q + {const} + (-1)^q for every 170 <= q <= 1200"


def test_r120_preperiod_is_170(ctx) -> str:
    """N(120) = 170: the law fails at q = 169, so 170 is least."""
    c = ctx.census[120]
    check(c["cls"] == "live", f"row 120 classified {c['cls']}, expected live")
    check(c["period"] == 2, f"row 120 has period {c['period']}, expected 2")
    check(c["N"] == 170, f"N(120) = {c['N']}, Brouwer publishes 170")
    d = {q: dd for q, _, dd in chomp.row(120, qmax=400)}
    check(d[169] != d[171],
          f"d(169)={d[169]} equals d(171); then N(120) would be < 170")
    check(d[170] == d[172] and d[171] == d[173],
          "period 2 does not actually hold from q=170")
    return "N(120)=170 with period 2, and the pattern genuinely breaks at q=169"


def test_r120_junk_ends_at_172_169(ctx) -> str:
    """Brouwer: the junk ends in the P-position (172,169,120)."""
    got = {q: p for q, p, _ in chomp.row(120, qmax=200)}
    check(got[169] == 172,
          f"f(169,120) = {got[169]}, Brouwer's last junk entry is (172,169,120)")
    return "last pre-periodic P-position is (172,169,120), as published"


TESTS = [test_r120_published_values, test_r120_parity_law,
         test_r120_preperiod_is_170, test_r120_junk_ends_at_172_169]
