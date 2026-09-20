"""Shared fixtures for the ground-truth tests.

Every reference file under tests/data/ is vendored so the suite runs offline and
byte-identically in CI.  Provenance is in tests/data/SOURCES.md; `refresh.py`
re-downloads them.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"


class Fail(AssertionError):
    """A ground-truth disagreement.  Message must name the exact cell."""


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise Fail(msg)


# ------------------------------------------------------------ OEIS b-files --
@lru_cache(maxsize=None)
def oeis(name: str) -> dict[int, int]:
    """{index: term} from a vendored b-file."""
    out = {}
    for line in (DATA / "oeis" / f"{name}.txt").read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        n, v = line.split()[:2]
        out[int(n)] = int(v)
    return out


# ------------------------------------------------------- Brouwer's page -----
@lru_cache(maxsize=None)
def brouwer_table() -> dict[tuple[int, int], int]:
    """{(q,r): f(q,r)} for r <= q <= 24, from aeb.win.tue.nl/games/chomp.html."""
    out = {}
    for line in (DATA / "brouwer_table_24.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        vals = [int(x) for x in line.split()]
        r, vals = vals[0], vals[1:]
        for i, v in enumerate(vals):
            out[(r + i, r)] = v
    return out


@lru_cache(maxsize=None)
def r120_pvalues() -> dict[int, int]:
    """{q: f(q,120)} for q = 120.. as printed by Brouwer."""
    out = {}
    for line in (DATA / "r120_pvalues.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        q, p = line.split()
        out[int(q)] = int(p)
    return out


@lru_cache(maxsize=None)
def nivasch_periods() -> dict[int, list[int]]:
    """{period: [r, ...]} -- Nivasch's census to r = 10000."""
    return {int(k): v for k, v in
            json.loads((DATA / "nivasch_periods.json").read_text()).items()}


@lru_cache(maxsize=None)
def brouwer_patterns() -> list[tuple[int, int, int, list[int]]]:
    """[(r, start, period, pattern), ...] -- Brouwer's worked table."""
    return [tuple(x) for x in                       # type: ignore[misc]
            json.loads((DATA / "brouwer_patterns.json").read_text())]
