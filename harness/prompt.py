"""Prompt assembly.

The whole point of this module is cache discipline. DeepSeek caches on exact
prefix match, so anything volatile placed early invalidates everything after
it. Order is: system prompt, mission, island thesis (stable for the island),
then ledger, dead ends, notes, handoff (volatile, last).

Cache reads are roughly a tenth of fresh input. On a 12-session budget that
ordering is worth several extra sessions, so `assert_stable_prefix` fails the
run loudly rather than letting the cost drift up unnoticed.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from .ledger import Ledger, dead_ends

ISLANDS = {
    "01-recurrence": (
        "Work directly inside the Brouwer recurrence. Localize the step in the "
        "Byrnes periodicity argument that destroys effectivity, then try to make "
        "that single step quantitative. Combinatorial and inductive methods; "
        "bounds proved from the mex structure itself."
    ),
    "02-renorm": (
        "Work the Friedman-Landsberg renormalization and nonlinear-dynamics "
        "picture. P-positions for fixed r appear to lie near three lines, and the "
        "same picture rescales across r. If that self-similarity can be made "
        "rigorous even in a weak form, a preperiod bound should follow from the "
        "rate of convergence to the fixed point."
    ),
}


def _read(p: Path) -> str:
    return p.read_text() if p.exists() else ""


def stable_prefix(root: Path, island: str) -> str:
    """Never varies between sessions of the same island."""
    return "\n\n".join(
        [
            _read(root / "prompts" / "explorer.md").replace(
                "{{ISLAND_ID}}", island
            ).replace("{{ISLAND_THESIS}}", ISLANDS[island]),
            "=" * 70,
            _read(root / "MISSION.md"),
            "=" * 70,
        ]
    )


def volatile_suffix(root: Path, island: str) -> str:
    led = Ledger(root / "LEDGER")
    notes = _read(root / "islands" / island / "NOTES.md") or "(no notes yet)"
    handoff = _read(root / "islands" / island / "HANDOFF.md") or (
        "(no previous session -- you are first on this island)"
    )
    return "\n\n".join(
        [
            "## LEDGER — current claims\n\n" + led.render(),
            "## DEAD ENDS — do not repeat these\n\n" + dead_ends(root / "LEDGER"),
            f"## ISLAND NOTES ({island})\n\n" + notes,
            "## HANDOFF FROM LAST SESSION\n\n" + handoff,
        ]
    )


def build(root: Path, island: str, session_id: str) -> list[dict]:
    prefix = stable_prefix(root, island)
    suffix = volatile_suffix(root, island)
    return [
        {"role": "system", "content": prefix},
        {
            "role": "user",
            "content": (
                f"{suffix}\n\n{'=' * 70}\n\n"
                f"Session {session_id} begins now. Start by stating, in one "
                f"paragraph, where you believe the problem stands and what you "
                f"intend to do this session. Then work."
            ),
        },
    ]


def prefix_fingerprint(root: Path, island: str) -> str:
    return hashlib.sha256(stable_prefix(root, island).encode()).hexdigest()[:16]


def assert_stable_prefix(root: Path, island: str) -> None:
    """Fail loudly if the cacheable prefix moved since last session."""
    f = root / "runs" / f".prefix-{island}"
    cur = prefix_fingerprint(root, island)
    if f.exists():
        old = f.read_text().strip()
        if old != cur:
            raise SystemExit(
                f"\nPREFIX CHANGED for {island}: {old} -> {cur}\n"
                f"Every session from here pays full input price until it "
                f"restabilises. If the edit was deliberate, delete {f} and rerun.\n"
            )
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(cur)
