"""Run every ground-truth test.

    python -m GROUND_TRUTH.tests.run_all --max-r 10000

--max-r sets how far the census-backed tests reach.  10000 is the full
published range (Nivasch's census); smaller values skip the tests that need it
and run in seconds.  Exit code is 0 only if every test passes.
"""
from __future__ import annotations

import argparse
import sys
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path

from .. import chomp
from . import (test_brouwer_table, test_grundy, test_nivasch, test_oeis,
               test_r120, test_trivial)
from .common import Fail

# order matters only for readability: cheap and structural first, then the
# census-backed ones, then the slow brute-force game tree.
MODULES = [test_brouwer_table, test_trivial, test_r120, test_oeis,
           test_nivasch, test_grundy]


@dataclass
class Ctx:
    max_r: int
    grundy_n: int
    alpha: float
    margin: int
    cache: Path | None
    _census: dict = field(default_factory=dict, repr=False)

    @property
    def census(self) -> dict[int, dict]:
        if not self._census:
            t = time.time()
            print(f"    [census to r={self.max_r} ...]", end="", flush=True)
            self._census = chomp.census(self.max_r, alpha=self.alpha,
                                        margin=self.margin, cache=self.cache)
            print(f" {time.time() - t:.1f}s")
        return self._census


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="GROUND_TRUTH.tests.run_all")
    ap.add_argument("--max-r", type=int, default=10000,
                    help="how far the census-backed tests reach (default 10000)")
    ap.add_argument("--grundy-n", type=int, default=40,
                    help="board size for the brute-force game tree (default 40)")
    ap.add_argument("--alpha", type=float, default=1.8)
    ap.add_argument("--margin", type=int, default=600)
    ap.add_argument("--cache", type=Path, default=None,
                    help="reuse/write a census TSV instead of recomputing")
    ap.add_argument("-k", default=None, help="only tests whose name contains this")
    a = ap.parse_args(argv)

    ctx = Ctx(a.max_r, a.grundy_n, a.alpha, a.margin, a.cache)
    print(f"ground truth: solver={chomp.build()}  max_r={a.max_r}  "
          f"grundy_n={a.grundy_n}\n")

    npass = nfail = nskip = 0
    t0 = time.time()
    for mod in MODULES:
        name = mod.__name__.rsplit(".", 1)[-1]
        print(f"{name}")
        for fn in mod.TESTS:
            if a.k and a.k not in fn.__name__:
                continue
            t = time.time()
            try:
                detail = fn(ctx)
            except Fail as e:
                nfail += 1
                print(f"  FAIL {fn.__name__}\n       {e}")
                continue
            except Exception:
                nfail += 1
                print(f"  ERROR {fn.__name__}")
                traceback.print_exc()
                continue
            dt = time.time() - t
            if isinstance(detail, str) and detail.startswith("SKIP"):
                nskip += 1
                print(f"  skip {fn.__name__}: {detail[5:]}")
            else:
                npass += 1
                print(f"  ok   {fn.__name__}  ({dt:.1f}s)\n       {detail}")
        print()

    print(f"{npass} passed, {nfail} failed, {nskip} skipped "
          f"in {time.time() - t0:.1f}s")
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
