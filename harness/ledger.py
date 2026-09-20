"""Append-only claim ledger.

Every mutation is an append. Status changes are new lines with the same id;
the last line for an id wins. Nothing is ever edited or deleted, so a bad
librarian pass or a crashed session can never destroy a result.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable

VALID_STATUS = {"open", "evidence", "proven", "refuted", "superseded"}
VALID_TYPE = {"lemma", "conjecture", "observation", "solver_bug"}
_ID_RE = re.compile(r"^C(\d{4})$")


@dataclass
class Claim:
    id: str
    statement: str
    type: str = "conjecture"
    status: str = "open"
    proof_ref: str | None = None
    evidence: str = ""
    verified_range: str = ""
    depends_on: list[str] = field(default_factory=list)
    novelty_checked: bool = False
    session: str = ""

    def validate(self) -> None:
        if not _ID_RE.match(self.id):
            raise ValueError(f"bad claim id {self.id!r}, want C0001 form")
        if self.status not in VALID_STATUS:
            raise ValueError(f"bad status {self.status!r}")
        if self.type not in VALID_TYPE:
            raise ValueError(f"bad type {self.type!r}")
        if not self.statement.strip():
            raise ValueError("empty statement")


class Ledger:
    def __init__(self, root: str | os.PathLike = "LEDGER"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "claims.jsonl"
        self.path.touch()

    # ---- read ----------------------------------------------------------

    def raw(self) -> list[Claim]:
        """Every line, in write order. The full audit trail."""
        out = []
        for lineno, line in enumerate(self.path.read_text().splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(Claim(**json.loads(line)))
            except (json.JSONDecodeError, TypeError) as e:
                # A corrupt line must never take down a session.
                print(f"[ledger] skipping malformed line {lineno}: {e}")
        return out

    def resolved(self) -> dict[str, Claim]:
        """Current state: last write wins per id."""
        state: dict[str, Claim] = {}
        for c in self.raw():
            state[c.id] = c
        return state

    def active(self) -> list[Claim]:
        """What the explorer sees. Refuted and superseded claims are hidden
        from the prompt but stay on disk -- dead_ends.md carries the lesson."""
        return [
            c for c in self.resolved().values()
            if c.status in {"open", "evidence", "proven"}
        ]

    def next_id(self) -> str:
        nums = [int(m.group(1)) for c in self.raw() if (m := _ID_RE.match(c.id))]
        return f"C{max(nums, default=0) + 1:04d}"

    # ---- write ---------------------------------------------------------

    def append(self, claim: Claim) -> Claim:
        claim.validate()
        for dep in claim.depends_on:
            if dep not in self.resolved():
                raise ValueError(f"{claim.id} depends on unknown claim {dep}")
        with self.path.open("a") as f:
            f.write(json.dumps(asdict(claim), sort_keys=True) + "\n")
        return claim

    def add(self, statement: str, **kw) -> Claim:
        return self.append(Claim(id=self.next_id(), statement=statement, **kw))

    def set_status(self, cid: str, status: str, session: str, **kw) -> Claim:
        cur = self.resolved().get(cid)
        if cur is None:
            raise KeyError(f"no such claim {cid}")
        d = asdict(cur) | {"status": status, "session": session} | kw
        return self.append(Claim(**d))

    # ---- prompt rendering ----------------------------------------------

    def render(self, claims: Iterable[Claim] | None = None) -> str:
        claims = list(claims if claims is not None else self.active())
        if not claims:
            return "(ledger empty -- this is session 1)"
        order = {"proven": 0, "evidence": 1, "open": 2}
        claims.sort(key=lambda c: (order.get(c.status, 9), c.id))
        lines = []
        for c in claims:
            head = f"[{c.id}] ({c.status}/{c.type}) {c.statement}"
            bits = []
            if c.verified_range:
                bits.append(f"verified: {c.verified_range}")
            if c.evidence:
                bits.append(c.evidence)
            if c.depends_on:
                bits.append("depends on " + ", ".join(c.depends_on))
            if c.proof_ref:
                bits.append(f"proof: {c.proof_ref}")
            if not c.novelty_checked and c.status in {"evidence", "proven"}:
                bits.append("NOVELTY NOT CHECKED")
            lines.append(head + ("\n    " + "; ".join(bits) if bits else ""))
        return "\n".join(lines)


def dead_ends(root: str | os.PathLike = "LEDGER") -> str:
    p = Path(root) / "dead_ends.md"
    if not p.exists() or not p.read_text().strip():
        return "(no dead ends recorded yet)"
    return p.read_text()
