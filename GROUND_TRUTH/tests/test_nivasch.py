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


def test_fg7_period_claim_is_wrong(ctx) -> str:
    """#G07 section 8.2 claims two periods that do not exist.  Pin the conflict.

    Brouwer, Horvath, Molnar-Saska & Szabo, "On Three-Rowed Chomp",
    INTEGERS 5 (2005) #G07, section 8.2, immediately after correctly giving
    period 2 for r = 120, says:

        "Later one finds larger periods, like period 25 for r = 782
         and period 720 for r = 7751."

    Both rows are below r = 10000, where Nivasch's census -- which Brouwer
    endorses on his own maintained page ("Gabriel Nivasch wrote (and I
    agree)") -- finds periods 2, 3, 4 and 9 only, and lists neither row.
    No period 25 or 720 appears anywhere on that page.

    Our solver says r = 782 is live with period 1 (a plain linear row, which
    is why it is in no pattern table) and r = 7751 is STALE -- finitely many
    P-positions, so no period at all.  The indexing is not in doubt: #G07 and
    the solver agree that r = 120 has period 2.

    So section 8.2 is an error, silently superseded by the later census.
    This test does not assert #G07 is wrong as a matter of taste; it pins what
    the solver says, so that a future reader who finds that sentence gets an
    explanation instead of a scare.
    """
    if ctx.max_r < 7751:
        return f"SKIP (max_r={ctx.max_r} < 7751)"
    cen = ctx.census
    a, b = cen[782], cen[7751]
    check(a["cls"] == "live" and a["period"] == 1,
          f'r=782 expected live/period 1, got {a["cls"]}/period {a["period"]}')
    check(b["cls"] == "stale",
          f'r=7751 expected stale, got {b["cls"]}/period {b["period"]}')
    return ("#G07 section 8.2 contradicted as expected: r=782 is period 1 "
            "(not 25), r=7751 is stale (not period 720)")


TESTS = [test_period_lists_exact, test_no_other_periods,
         test_period9_exactly_6541_and_8767, test_brouwer_pattern_table,
         test_fg7_period_claim_is_wrong]
