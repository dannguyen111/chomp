"""Thin Python wrapper around GROUND_TRUTH/solver.cpp.

Builds the binary on demand (g++, clang++ or MSVC) and parses its four output
modes.  Nothing here reimplements the recurrence: the C++ file is the single
source of truth, and this module only moves bytes.
"""
from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "solver.cpp"
EXE = HERE / ("solver.exe" if os.name == "nt" else "solver")


# --------------------------------------------------------------------- build
def _msvc_env() -> dict | None:
    """Locate a 64-bit MSVC toolchain via vswhere and return its environment."""
    vswhere = Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) \
        / "Microsoft Visual Studio/Installer/vswhere.exe"
    if not vswhere.exists():
        return None
    try:
        root = subprocess.run(
            [str(vswhere), "-products", "*", "-latest", "-property", "installationPath"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            check=True).stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        return None
    vcvars = Path(root) / "VC/Auxiliary/Build/vcvars64.bat"
    if not root or not vcvars.exists():
        return None
    out = subprocess.run(["cmd", "/c", f'"{vcvars}" >nul 2>&1 && set'],
                         capture_output=True, text=True)
    env = dict(os.environ)
    for line in out.stdout.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            env[k] = v
    return env


def build(force: bool = False) -> Path:
    """Compile solver.cpp if the binary is missing or stale.

    On Windows MSVC comes first: the g++ that ships with Git-for-Windows /
    MinGW here is a 32-bit GCC 6, which caps the address space well below what
    a census past r ~ 20000 needs.  Everywhere else g++ is fine and is what CI
    uses.
    """
    if EXE.exists() and not force and EXE.stat().st_mtime >= SRC.stat().st_mtime:
        return EXE
    errs = []

    def try_msvc():
        env = _msvc_env()
        if not env:
            errs.append("msvc: no vswhere/vcvars64")
            return False
        # CreateProcess resolves the program name against the *parent's* PATH,
        # not the env= we pass, so find cl.exe ourselves.
        cl = shutil.which("cl", path=env.get("PATH", ""))
        if not cl:
            errs.append("msvc: cl.exe not on the vcvars PATH")
            return False
        r = subprocess.run(
            [cl, "/nologo", "/O2", "/std:c++17", "/EHsc",
             f"/Fe:{EXE}", f"/Fo:{HERE / 'solver.obj'}", str(SRC)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=env, cwd=str(HERE))
        if r.returncode == 0 and EXE.exists():
            return True
        errs.append("cl: " + (r.stdout + r.stderr).strip()[:800])
        return False

    def try_gcc():
        for cxx in ("g++", "clang++"):
            if not shutil.which(cxx):
                continue
            for std in ("-std=c++17", "-std=c++1z"):
                r = subprocess.run([cxx, "-O2", std, "-o", str(EXE), str(SRC)],
                                   capture_output=True, text=True,
                                   encoding="utf-8", errors="replace")
                if r.returncode == 0 and EXE.exists():
                    return True
                errs.append(f"{cxx} {std}: {r.stderr.strip()[:500]}")
        errs.append("no working g++/clang++ on PATH")
        return False

    order = (try_msvc, try_gcc) if platform.system() == "Windows" else (try_gcc, try_msvc)
    for attempt in order:
        if attempt():
            return EXE
    raise RuntimeError("cannot build %s:\n%s" % (SRC, "\n".join(errs)))


def run(*args: object, stderr: bool = False) -> str:
    exe = build()
    p = subprocess.run([str(exe)] + [str(a) for a in args],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError(f"solver {args} failed ({p.returncode}):\n{p.stderr}")
    return p.stderr if stderr else p.stdout


# ---------------------------------------------------------------- the modes
def table(rmax: int, qmax: int | None = None) -> list[list[int]]:
    """f[q][r] for 0<=q<=qmax, 0<=r<=rmax.  Entries with r>q are f(q,q)."""
    if qmax is None:
        qmax = rmax
    txt = run("table", "--rmax", rmax, "--qmax", qmax)
    return [[int(x) for x in line.split()] for line in txt.splitlines() if line.strip()]


def row(r: int, qmax: int | None = None) -> list[tuple[int, int, int]]:
    """[(q, f(q,r), f(q,r)-q), ...] for one column r."""
    args = ["row", "--r", r] + (["--qmax", qmax] if qmax is not None else [])
    return [tuple(int(x) for x in line.split())          # type: ignore[misc]
            for line in run(*args).splitlines() if line.strip()]


_FIELDS = ("r", "cls", "period", "N", "dvals", "deathq", "dconst", "qend")


def _parse_census(txt: str) -> dict[int, dict]:
    out: dict[int, dict] = {}
    for line in txt.splitlines():
        if not line.strip() or line.startswith(("r\t", "#")):
            continue
        f = line.split("\t")
        rec = dict(zip(_FIELDS, f))
        d = {
            "r": int(rec["r"]),
            "cls": rec["cls"],
            "period": int(rec["period"]),
            "N": int(rec["N"]),
            "dvals": [int(x) for x in rec["dvals"].split(",")] if rec["dvals"] != "-" else [],
            "deathq": None if rec["deathq"] == "-" else int(rec["deathq"]),
            "dconst": None if rec["dconst"] == "-" else int(rec["dconst"]),
            "qend": None if rec["qend"] == "-" else int(rec["qend"]),
        }
        out[d["r"]] = d
    return out


class CorruptCensus(RuntimeError):
    """A census file is not a complete run. Never silently reuse one."""


_TRAILER = re.compile(r"^# complete rmax=(\d+) rows=(\d+)\s*$", re.M)


def _validate(txt: str, cen: dict[int, dict], where: str,
              rmax: int | None = None) -> dict[int, dict]:
    """A census must be complete: it must carry the solver's trailer, cover
    0..rmax with no gaps, and have the row count the trailer claims.

    Without the trailer check a file truncated to its first row still parses as
    a valid (tiny) census, and every number computed from it downstream would be
    quietly wrong. That is the exact shape of failure MISSION.md section 6 is
    written to prevent, so this raises rather than warns.
    """
    m = _TRAILER.search(txt)
    if not m:
        raise CorruptCensus(
            f"{where}: no completion trailer -- the file is truncated, or was "
            f"written by a solver predating the trailer. Delete and recompute.")
    claimed_r, claimed_n = int(m.group(1)), int(m.group(2))
    if not cen:
        raise CorruptCensus(f"{where}: no census rows")
    if len(cen) != claimed_n:
        raise CorruptCensus(
            f"{where}: trailer claims {claimed_n} rows, parsed {len(cen)}")
    if max(cen) != claimed_r:
        raise CorruptCensus(
            f"{where}: trailer claims rmax={claimed_r}, parsed {max(cen)}")
    top = max(cen)
    missing = [r for r in range(top + 1) if r not in cen]
    if missing:
        raise CorruptCensus(
            f"{where}: {len(missing)} gaps in 0..{top}, first at r={missing[0]}")
    if rmax is not None and top < rmax:
        raise CorruptCensus(
            f"{where}: covers r<={top} but r<={rmax} was asked for "
            f"(truncated file? delete it and recompute)")
    return cen


def census(rmax: int, alpha: float | None = None, margin: int | None = None,
           confirm: int | None = None, cache: Path | None = None) -> dict[int, dict]:
    """One descriptor per r in 0..rmax.  `cache` reuses/writes a TSV.

    Pass rmax=0 to mean "whatever is in the cache file".
    """
    if cache is not None and Path(cache).exists():
        raw = Path(cache).read_text()
        return _validate(raw, _parse_census(raw), str(cache), rmax or None)
    args: list[object] = ["census", "--rmax", rmax]
    if alpha is not None:
        args += ["--alpha", alpha]
    if margin is not None:
        args += ["--margin", margin]
    if confirm is not None:
        args += ["--confirm", confirm]
    txt = run(*args)
    cen = _validate(txt, _parse_census(txt), "solver output", rmax or None)
    if cache is not None:
        # Write through a temp file in the same directory and rename, so an
        # interrupted run leaves no half-written census behind to be reused.
        dest = Path(cache)
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".part")
        tmp.write_text(txt)
        tmp.replace(dest)
    return cen


def f_at(cen: dict[int, dict], q: int, r: int) -> int | None:
    """f(q,r) from a census descriptor, for q past the column's preperiod."""
    c = cen[r]
    if c["cls"] == "stale":
        return c["dconst"] if q >= c["deathq"] else None
    if q < c["N"]:
        return None
    return q + c["dvals"][(q - c["N"]) % c["period"]]


if __name__ == "__main__":
    print(build())
