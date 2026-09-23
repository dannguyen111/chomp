"""Download the primary sources into GROUND_TRUTH/data/.

    python -m GROUND_TRUTH.fetch_sources

These are third-party papers. They are deliberately NOT committed -- this repo
is public and redistributing them is not ours to do -- so `data/` is gitignored
and this script refills it. The tests do not need any of it: everything they
check against is the derived numeric data vendored in `tests/data/`, whose
provenance is in `tests/data/SOURCES.md`.

Gotchas worth knowing before you read any of these:

  * The Zeilberger PDF that MISSION.md links is TRUNCATED at 6 pages and stops
    in the middle of the 2-rowed warm-up, before the Ultimate-Periodicity
    Theorem. Read the .tex, which is complete.
  * `math.colgate.edu/~integers/g3/g3.pdf` is NOT Byrnes. It serves
    Hegarty-Larsson, INTEGERS 6 (2006) #A03 -- a different and, as it happens,
    rather relevant paper. It is fetched here under its real name.
"""
from __future__ import annotations

import sys
from pathlib import Path

import requests

DATA = Path(__file__).resolve().parent / "data"

SOURCES = {
    "brouwer_horvath_molnarsaska_szabo_three_rowed_chomp.pdf":
        ("https://math.colgate.edu/~integers/fg7/fg7.pdf",
         "Brouwer, Horvath, Molnar-Saska, Szabo, 'On Three-Rowed Chomp', "
         "INTEGERS 5 (2005) #G07. THE SOURCE OF THE RECURRENCE this whole "
         "project is built on (section 8.1). READ IT BEFORE CLAIMING ANYTHING "
         "ABOUT f(q,r): section 8.1 already states '1 <= f(q,r) <= q+r+1', "
         "which is C0012. Its absence from this list until 2026-09-23 is why "
         "C0012 was proved, refereed and promoted before anyone noticed it "
         "was prior art."),
    "byrnes_poset_game_periodicity.pdf":
        ("http://e.math.hr/dvijeigre/byrnes/main.pdf",
         "Byrnes, Poset-Game Periodicity (Intel STS version, 20pp). "
         "Published as INTEGERS 3 (2003) #G03. The proof audited in "
         "byrnes_audit.md; Lemma 4 p.8, Lemma 5 p.8, Lemma 9 p.14."),
    "byrnes_siemens.pdf":
        ("http://e.math.hr/dvijeigre/byrnes/siemens.pdf",
         "Byrnes, same proof, Siemens-Westinghouse version (22pp)."),
    "zeilberger_chomp_recurrences_chaos.tex":
        ("http://sites.math.rutgers.edu/~zeilberg/mamarim/mamarimTeX/byrnes.tex",
         "Zeilberger, Chomp, Recurrences and Chaos(?) -- COMPLETE source. "
         "The Ultimate-Periodicity Theorem and the 3-row reduction."),
    "zeilberger_TRUNCATED.pdf":
        ("https://sites.math.rutgers.edu/~zeilberg/mamarim/mamarimPDF/byrnes.pdf",
         "The same paper as hosted PDF -- TRUNCATED at 6pp. Kept only so nobody "
         "re-downloads it and concludes the exposition is unfinished."),
    "hegarty_larsson_difference_multisets.pdf":
        ("https://math.colgate.edu/~integers/g3/g3.pdf",
         "Hegarty & Larsson, INTEGERS 6 (2006) #A03. Greedy mex-like "
         "permutations constrained by pi(n)-n, Beatty sequences, Stolarsky "
         "arrays. Relevant to island 02; novelty-check before building on it."),
    "brouwer_chomp.html":
        ("https://aeb.win.tue.nl/games/chomp.html",
         "Brouwer's Chomp page: the small table, the r=120 anomaly, Nivasch's "
         "period census, and the A029900/A029901/A029902 strip bounds."),
}


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    rc = 0
    for name, (url, what) in SOURCES.items():
        dest = DATA / name
        if dest.exists():
            print(f"  have  {name} ({dest.stat().st_size:,} B)")
            continue
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
        except Exception as e:                       # noqa: BLE001
            print(f"  FAIL  {name}: {e}")
            rc = 1
            continue
        dest.write_bytes(r.content)
        print(f"  got   {name} ({len(r.content):,} B)  {url}")
        print(f"        {what}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
