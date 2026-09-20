"""Re-download every vendored reference file in tests/data/.

    python -m GROUND_TRUTH.tests.refresh

Needs network. Run it, then `git diff` -- an empty diff means the literature has
not moved under us; a non-empty one is the news. See data/SOURCES.md.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

import requests

DATA = Path(__file__).resolve().parent / "data"
RAW = Path(__file__).resolve().parent.parent / "data"
CHOMP = "https://aeb.win.tue.nl/games/chomp.html"
SEQS = ["A029899", "A029900", "A029901", "A029902", "A029903", "A029904",
        "A029905", "A069001"]


def get(url: str) -> str:
    r = requests.get(url, timeout=90)
    r.raise_for_status()
    r.encoding = r.encoding or "utf-8"
    return r.text


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "oeis").mkdir(exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)

    for s in SEQS:
        txt = get(f"https://oeis.org/{s}/b{s[1:]}.txt")
        (DATA / "oeis" / f"{s}.txt").write_text(txt, encoding="utf-8")
        print(f"  {s}: {len(txt.splitlines())} lines")

    raw = get(CHOMP)
    (RAW / "brouwer_chomp.html").write_text(raw, encoding="utf-8")
    t = re.sub(r"<[^>]+>", " ", raw)
    t = re.sub(r"[ \t]+", " ", html.unescape(t))

    tab = {}
    for m in re.finditer(r"^\s*(\d{1,2})\|\s*([\d ]+)$", t, re.M):
        r, vals = int(m.group(1)), [int(x) for x in m.group(2).split()]
        if r <= 24 and len(vals) == 25 - r:
            tab[r] = vals
    assert set(tab) == set(range(25)), sorted(set(range(25)) - set(tab))
    with (DATA / "brouwer_table_24.txt").open("w") as f:
        f.write("# Brouwer, https://aeb.win.tue.nl/games/chomp.html -- f(q,r), r<=q<=24\n")
        f.write("# one line per r: `r  f(r,r) f(r+1,r) ... f(24,r)`\n")
        for r in range(25):
            f.write("%d %s\n" % (r, " ".join(map(str, tab[r]))))
    print(f"  brouwer_table_24: {sum(len(v) for v in tab.values())} cells")

    m = re.search(r"a function of q for q at least 120 are:\s*([\d\s]+?)\.\.\.", t)
    seq = [int(x) for x in m.group(1).split()]
    (DATA / "r120_pvalues.txt").write_text(
        "# Brouwer: f(q,120) for q = 120, 121, ...\n"
        + "\n".join("%d %d" % (120 + i, v) for i, v in enumerate(seq)) + "\n")
    print(f"  r120_pvalues: {len(seq)} values")

    cens = {}
    for p in (2, 3, 4, 9):
        mm = re.search(r"Period %d for r = ([\d,\s]+?)\." % p, t)
        cens[p] = sorted(int(x) for x in mm.group(1).replace(",", " ").split())
    (DATA / "nivasch_periods.json").write_text(json.dumps(cens, indent=1))
    print("  nivasch_periods:", {k: len(v) for k, v in cens.items()})

    rows = re.findall(r"^\s*(\d+) (\d+) (\d+) ((?:-?\d+ ?)+)$", t, re.M)
    pat = [(int(a), int(b), int(c), [int(x) for x in d.split()])
           for a, b, c, d in rows]
    pat = [p for p in pat if p[2] in (2, 3, 4, 9) and len(p[3]) == p[2]]
    (DATA / "brouwer_patterns.json").write_text(json.dumps(pat, indent=1))
    print(f"  brouwer_patterns: {len(pat)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
