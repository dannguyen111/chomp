"""The eight OEIS sequences named in MISSION.md section 6, against their b-files.

The identifications used here (each verified term by term below):

  A029899(n) = #{P-positions (p,q,r) of 3-row Chomp with p <= n}
  A029900(q) = f(q,q)                     -- p where (p,q,q) is a P-position
  A029901    = sorted {p : (p,p,r) is a P-position} = the stale constants
  A029902    = sorted {r : (p,p,r) is a P-position} = the r whose rows die
  A029903    = c,  A029904 = q0,  A029905 = r, over exactly those r for which
               f(q,r) = q + c for all q >= q0 (i.e. live rows of period 1;
               note 120 is deliberately absent -- its row has period 2)
  A069001(n) = Grundy value of the 3 x n rectangle  [see test_grundy.py]
"""
from __future__ import annotations

from .. import chomp
from .common import Fail, check, oeis


def _cmp(name: str, got: dict[int, int], limit: int | None = None) -> str:
    ref = oeis(name)
    idx = sorted(ref)
    if limit is not None:
        idx = [i for i in idx if i <= limit]
    idx = [i for i in idx if i in got]
    if not idx:
        raise Fail(f"{name}: no overlapping indices to compare")
    bad = [(i, got[i], ref[i]) for i in idx if got[i] != ref[i]]
    if bad:
        raise Fail("%s: %d of %d terms disagree; first n=%d solver=%d oeis=%d"
                   % (name, len(bad), len(idx), *bad[0]))
    return f"{name}: {len(idx)} terms (n<={idx[-1]}) match"


def test_A029900_diagonal(ctx) -> str:
    n = min(ctx.max_r, max(sorted(oeis("A029900"))))
    tab = chomp.table(n, n)
    return _cmp("A029900", {q: tab[q][q] for q in range(n + 1)})


def test_A029899_counts(ctx) -> str:
    """Cumulative count of P-positions with first coordinate <= n."""
    n = min(ctx.max_r, max(sorted(oeis("A029899"))))
    tab = chomp.table(n, n)
    cnt = [0] * (n + 2)
    for q in range(n + 1):
        for r in range(q + 1):            # P-position iff f(q,r) >= q
            p = tab[q][r]
            if p >= q and p <= n:
                cnt[p] += 1
    tot, got = 0, {}
    for p in range(n + 1):
        tot += cnt[p]
        got[p] = tot
    return _cmp("A029899", got)


def test_A029901_A029902_stale(ctx) -> str:
    """(p,p,r) P-positions: p is the stale constant, r the row that dies."""
    cen = ctx.census
    stale = sorted((c["r"], c["dconst"]) for c in cen.values() if c["cls"] == "stale")
    # both b-files are 0-indexed (A029901's stated offset is 1, but the
    # synthesised b-file starts at n=0; `oeis()` reads the file, not the header)
    a901 = {i: p for i, (_, p) in enumerate(stale)}
    a902 = {i: r for i, (r, _) in enumerate(stale)}
    return (_cmp("A029901", a901) + "; " + _cmp("A029902", a902))


def test_A029903_A029904_A029905_period1(ctx) -> str:
    """The one-parameter families: f(q,r) = q + c for every q >= q0."""
    cen = ctx.census
    fam = sorted((c["r"], c["dvals"][0], c["N"])
                 for c in cen.values() if c["cls"] == "live" and c["period"] == 1)
    a905 = {i: r for i, (r, _, _) in enumerate(fam)}
    a903 = {i: c for i, (_, c, _) in enumerate(fam)}
    a904 = {i: q for i, (_, _, q) in enumerate(fam)}
    check(120 not in dict(enumerate(x[0] for x in fam)).values(),
          "r=120 must NOT be a period-1 row (Brouwer: A029905 has no term 120)")
    return "; ".join([_cmp("A029905", a905), _cmp("A029903", a903),
                      _cmp("A029904", a904)])


def test_A029900_A029901_complementary(ctx) -> str:
    """Sheiner (2026): the 3xn winning opening move is unique, equivalently
    A029900 and A029901 partition the positive integers."""
    cen, n = ctx.census, min(ctx.max_r, 20000)
    tab_n = min(n, 3000)
    tab = chomp.table(tab_n, tab_n)
    diag = {tab[q][q] for q in range(tab_n + 1)}
    stale = {c["dconst"] for c in cen.values() if c["cls"] == "stale"}
    lim = min(max(diag), max(stale))
    both = sorted((diag & stale))
    if both:
        raise Fail(f"A029900 and A029901 overlap at {both[:5]}")
    miss = [p for p in range(1, lim + 1) if p not in diag and p not in stale]
    if miss:
        raise Fail(f"neither A029900 nor A029901 contains {miss[:5]} (<= {lim})")
    return f"A029900 u A029901 = [1,{lim}] exactly, disjointly"


TESTS = [test_A029900_diagonal, test_A029899_counts, test_A029901_A029902_stale,
         test_A029903_A029904_A029905_period1, test_A029900_A029901_complementary]
