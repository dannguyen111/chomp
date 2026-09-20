"""Gabriel Nivasch's period census to r = 10000, and Brouwer's pattern table.

Nivasch's lists (quoted on Brouwer's page) are exhaustive: every r <= 10000
whose row has period 2, 3, 4 or 9.  So this test checks the census in both
directions -- no published r missing, and no unpublished r claimed.
"""
from __future__ import annotations

from .common import Fail, check, brouwer_patterns, nivasch_periods


def test_period_lists_exact(ctx) -> str:
    if ctx.max_r < 10000:
        return f"SKIP (max_r={ctx.max_r} < 10000)"
    ref, cen = nivasch_periods(), ctx.census
    got: dict[int, list[int]] = {}
    for c in cen.values():
        if c["r"] <= 10000 and c["cls"] == "live" and c["period"] > 1:
            got.setdefault(c["period"], []).append(c["r"])
    for p in got:
        got[p].sort()
    for p in sorted(set(ref) | set(got)):
        a, b = ref.get(p, []), got.get(p, [])
        if a != b:
            raise Fail("period %d: solver has %d rows, Nivasch %d; "
                       "solver-only %s, Nivasch-only %s"
                       % (p, len(b), len(a),
                          sorted(set(b) - set(a))[:6], sorted(set(a) - set(b))[:6]))
    return ("periods to r=10000 exact: " +
            ", ".join(f"p{p}={len(ref[p])}" for p in sorted(ref)))


def test_no_other_periods(ctx) -> str:
    """Nivasch found only 2, 3, 4, 9.  Anything else below 10000 is a bug."""
    seen = {c["period"] for c in ctx.census.values()
            if c["r"] <= 10000 and c["cls"] == "live"}
    check(seen <= {1, 2, 3, 4, 9},
          f"unexpected periods below r=10000: {sorted(seen - {1, 2, 3, 4, 9})}")
    return f"periods observed below r=10000: {sorted(seen)}"


def test_period9_exactly_6541_and_8767(ctx) -> str:
    if ctx.max_r < 8767:
        return f"SKIP (max_r={ctx.max_r} < 8767)"
    nine = sorted(c["r"] for c in ctx.census.values()
                  if c["r"] <= 10000 and c["cls"] == "live" and c["period"] == 9)
    check(nine == [6541, 8767], f"period-9 rows are {nine}, expected [6541, 8767]")
    return "period 9 occurs exactly at r = 6541 and r = 8767"


def test_brouwer_pattern_table(ctx) -> str:
    """(r, start, period, pattern) for the 19 rows Brouwer tabulates.

    Brouwer lists the pattern starting at q = start; ours is listed from q = N.
    With start == N the two must agree as sequences, not merely as cyclic
    rotations, so this also pins the phase.
    """
    cen, checked = ctx.census, 0
    for r, start, period, pat in brouwer_patterns():
        if r > ctx.max_r:
            continue
        c = cen[r]
        check(c["cls"] == "live", f"r={r}: classified {c['cls']}, expected live")
        check(c["period"] == period,
              f"r={r}: period {c['period']}, Brouwer publishes {period}")
        check(c["N"] == start,
              f"r={r}: N={c['N']}, Brouwer publishes start={start}")
        # Brouwer's pattern is the deviation of d from its mean, so compare
        # differences around the mean rather than absolute d.
        d = c["dvals"]
        off = [x - min(d) for x in d]
        ref = [x - min(pat) for x in pat]
        check(off == ref,
              f"r={r}: pattern {d} (normalised {off}) != published {pat} ({ref})")
        checked += 1
    check(checked > 0, "no Brouwer pattern rows were in range")
    return f"{checked} published (r, start, period, pattern) rows match exactly"


TESTS = [test_period_lists_exact, test_no_other_periods,
         test_period9_exactly_6541_and_8767, test_brouwer_pattern_table]
