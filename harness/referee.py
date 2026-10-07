"""Referee gate.

Two rules carry all the weight:

1. Provenance is stripped. The referee sees the claim and the proof and nothing
   about where they came from -- not the island, not the session log, not the
   seed conjecture in MISSION.md s5, not the explorer's stated confidence. A
   referee who knows the expected answer will find reasons to accept it.

2. It runs twice, at different temperatures, and both must agree. One
   sycophantic pass is the single most likely way a false lemma gets promoted
   to `proven`, and at roughly $0.30 a run the second opinion is cheap.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import time
from dataclasses import replace
from pathlib import Path

from . import tools
from .ledger import Ledger
from .orclient import REFEREE_MODEL, Budget, OpenRouter

# Mission sections the referee may see. Section 5 (the sqrt(2) seed conjecture),
# 7, 8 and 9 are withheld: they telegraph the expected answer and the budget.
ALLOWED_SECTIONS = ("## 1.", "## 2.", "## 3.", "## 4.", "## 6.")


def redacted_mission(root: Path) -> str:
    text = (root / "MISSION.md").read_text(encoding="utf-8")
    blocks = re.split(r"\n(?=## \d+\.)", text)
    keep = [b for b in blocks if b.lstrip().startswith(ALLOWED_SECTIONS)]
    return "\n\n".join(keep)


def build_messages(root: Path, claim, proof: str, deps: dict) -> list[dict]:
    # A dependency reaches the referee verbatim, so it gets the same
    # provenance-free restatement as the claim itself when one is on file.
    # C0032's referee was shown C0029's ledger text, which names
    # byrnes_audit.md and the papers the island worked from.
    dep_text = (
        "\n".join(f"- [{d.id}] {_restatement(root, d.id) or d.statement}"
                  for d in deps.values())
        or "(none cited)"
    )
    return [
        {"role": "system", "content": (root / "prompts" / "referee.md").read_text(encoding="utf-8")},
        {
            "role": "user",
            "content": (
                f"{redacted_mission(root)}\n\n{'=' * 70}\n\n"
                f"## SUBMISSION\n\n**Claim.** {claim.statement}\n\n"
                f"**Results cited as already established:**\n{dep_text}\n\n"
                f"**Proof.**\n\n{proof}\n\n{'=' * 70}\n\n"
                "Referee this submission. Run all three passes. Emit only the JSON."
            ),
        },
    ]


def _parse(text: str) -> dict | None:
    """The last JSON object in the reply that carries a `disposition`.

    This used to be one greedy `\\{.*\\}`, which spans from the FIRST brace in
    the reply to the last. A referee that writes a set -- `{f(a,n): a<n}` --
    anywhere before its verdict put a brace in front of the JSON and made the
    whole reply unparseable, i.e. `inconclusive`. In a paper about sets of
    P-positions that is most replies.
    """
    found = _scan(text)
    if found is None:
        # Referee run 17 (C0028, t=0.3) wrote a complete verdict and lost it:
        # the model quoted the proof inside a string without escaping the
        # quotes -- "...in closed form: "g(1)=1, ..."" -- so no brace decoded.
        # Retry once on a copy with stray inner quotes escaped, and flag the
        # result so an audit can tell a repaired verdict from a clean one.
        found = _scan(text, repair=True)
        if found is not None:
            found["_repaired"] = True
    return found


def _scan(text: str, repair: bool = False) -> dict | None:
    dec = json.JSONDecoder()
    found = None
    # Repair starts fresh at each candidate object, so a quote in the prose
    # before the verdict cannot throw the in-string tracking out of phase.
    for m in re.finditer(r'\{\s*"' if repair else r"\{", text):
        try:
            if repair:
                obj, _ = dec.raw_decode(_escape_stray_quotes(text[m.start():]))
            else:
                obj, _ = dec.raw_decode(text, m.start())
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and "disposition" in obj:
            found = obj
    return found


def _escape_stray_quotes(text: str) -> str:
    """Escape every `"` inside a JSON string that cannot be its closing quote.

    A closing quote is followed, after whitespace, by `:` `}` `]` or a
    newline, or by a `,` that leads to the next key or element (`"` `{` `[`).
    Anything else -- a letter, a digit, `(`, `, fully` -- means the model
    meant a literal quote. Heuristic, so only ever used after the strict
    parse has failed.
    """
    out, in_str, i = [], False, 0
    while i < len(text):
        ch = text[i]
        if in_str and ch == "\\":
            out.append(text[i:i + 2])
            i += 2
            continue
        if ch == '"':
            if not in_str:
                in_str = True
            else:
                rest = text[i + 1:].lstrip(" \t")
                closes = rest[:1] in ("", ":", "}", "]", "\n", "\r") or (
                    rest[:1] == "," and rest[1:].lstrip()[:1] in ('"', "{", "["))
                if closes:
                    in_str = False
                else:
                    out.append('\\"')
                    i += 1
                    continue
        out.append(ch)
        i += 1
    return "".join(out)


FORCE_VERDICT = ("[HARNESS] Stop. Emit your JSON verdict now, this turn, and "
                 "nothing else. If you did not finish, say so in "
                 "gap_description and set confidence low -- do not reject a "
                 "claim you did not manage to check.")


def _attempts_path(root: Path) -> Path:
    return root / "LEDGER" / "referee" / "attempts.json"


def attempts(root: Path) -> dict[str, int]:
    """Runs per claim that ended without a verdict (inconclusive or split).

    The auto queue is ordered by this, fewest first. Before it existed the
    queue was ordered by id alone, and a claim that never got a verdict stayed
    at the head forever: C0024 took referee runs 13, 14 and 15 while seventeen
    other claims waited behind it.
    """
    p = _attempts_path(root)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("[referee] attempts.json is not valid JSON; treating as empty")
        return {}


def _restatement(root: Path, claim_id: str) -> str | None:
    """A provenance-free restatement of the claim, if one is on file.

    See LEDGER/restatements.json. The substitution is recorded in the verdict
    so it can be audited against the ledger statement afterwards.
    """
    p = root / "LEDGER" / "restatements.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8")).get(claim_id)
    except json.JSONDecodeError:
        print(f"[referee] restatements.json is not valid JSON; ignoring it")
        return None


def _ref(claim) -> str:
    return claim.proof_ref.split(" (")[0].strip()      # tolerate "path (NOTE)"


class NotRefereeable(Exception):
    """The claim cannot be judged yet. Not an error -- a skip."""


def refereeable(root: Path, claim, resolved: dict | None = None) -> tuple[bool, str]:
    """Can this claim be put in front of the referee right now?

    A claim is judged on a PROOF. Several claims carry a `proof_ref` that points
    at supporting evidence instead -- a census write-up, a literature audit, the
    test runner. Handing those to the referee would ask it whether a document
    that never claimed to be a proof is a valid proof; it would say no, and the
    claim would be marked `refuted` and hidden from every future explorer. So
    the bar is: a `lemma`, or a file written deliberately as a proof (under a
    `proofs/` directory). Observations are validated by the solver and their
    `verified_range`, not by an adversarial reader.

    Given the ledger (`resolved`), an observation whose proof file is also the
    proof of a lemma is skipped: the lemma is what that file sets out to prove,
    so it is refereed once, as the lemma. Ten observations point at
    C0045_reduction.md, and one of them (C0066) is a list of proof targets --
    not a statement a proof could establish, so a referee would reject it and
    it would be marked `refuted`.
    """
    if not claim.proof_ref:
        return False, "no proof_ref"
    ref = _ref(claim)
    if claim.type != "lemma" and "/proofs/" not in ref.replace("\\", "/"):
        return False, f"{claim.type} backed by evidence, not a proof: {ref}"
    if claim.type != "lemma" and resolved:
        owner = next((c.id for c in sorted(resolved.values(), key=lambda c: c.id)
                      if c.type == "lemma" and c.proof_ref and _ref(c) == ref),
                     None)
        if owner:
            return False, f"{ref} is refereed as the proof of lemma {owner}"
    if not (root / ref).exists():
        return False, f"proof file missing: {ref}"
    if claim.status in ("proven", "refuted", "superseded"):
        return False, f"already {claim.status}"
    if (root / "LEDGER" / "referee" / f"{claim.id}.json").exists():
        return False, "already refereed"
    held = _held(root).get(claim.id)
    if held:
        return False, f"held: {held}"
    return True, ref


def _held(root: Path) -> dict[str, str]:
    """Claims the operator has taken out of the queue, with the reason.

    For a lemma already in print (the C0012 lesson): refereeing it spends the
    budget confirming someone else's theorem. Edit LEDGER/referee/hold.json to
    release one.
    """
    p = root / "LEDGER" / "referee" / "hold.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("[referee] hold.json is not valid JSON; holding nothing")
        return {}


# ---- progress: what survives a dead runner ------------------------------
#
# Referee run 21 refereed C0032, then worked on its next claim for two and a
# half hours and died with the step still running: no verdict, no log, and no
# record of what it had spent. A verdict was only written once both passes had
# finished. Now every pass is written the moment it ends, and every turn is
# appended to a transcript, and the workflow pushes both to a side branch every
# few minutes (see referee.yml and ops/recover_referee.py). A rerun reuses a
# finished pass of the identical submission instead of paying for it again.

def _run_id() -> str:
    return os.environ.get("GITHUB_RUN_NUMBER") or "local"


def _progress_path(root: Path, claim_id: str) -> Path:
    return root / "LEDGER" / "referee" / "progress" / f"{claim_id}.json"


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    tmp.replace(path)      # atomic: a snapshot never sees half a file


def _fingerprint(messages: list[dict]) -> str:
    """What the referee was shown. A pass is reusable only for the same text."""
    return hashlib.sha256(json.dumps(messages, sort_keys=True)
                          .encode("utf-8")).hexdigest()[:16]


class _Transcript:
    """One JSON line per message, appended as the pass runs."""

    def __init__(self, root: Path, claim_id: str, temp: float):
        self.path = (root / "runs" / "referee" / f"run-{_run_id()}"
                     / f"{claim_id}.t{temp}.jsonl")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, msg: dict, **extra) -> None:
        line = {"t": round(time.time(), 1), **extra, **msg}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")


def referee(root: Path, claim_id: str, session: str = "referee",
            max_spend: float = 1.00) -> dict:
    led = Ledger(root / "LEDGER")
    resolved = led.resolved()
    claim = resolved.get(claim_id)
    if claim is None:
        raise SystemExit(f"no such claim {claim_id}")
    ok, why = refereeable(root, claim, resolved)
    if not ok:
        raise NotRefereeable(f"{claim_id}: {why}")

    proof = (root / why).read_text(encoding="utf-8")
    deps = {d: resolved[d] for d in claim.depends_on if d in resolved}

    budget = Budget(root / "BUDGET.json")
    start_spend = budget.spent
    client = OpenRouter(budget)
    verdicts = []

    # The referee works inside an isolated box, NOT the project root. Its tools
    # used to be scoped to the repo, and `bash` runs with shell=True, so one
    # `cat islands/<id>/HANDOFF.md` handed it the expected answer and the
    # explorer's confidence -- which is exactly what this gate is supposed not
    # to know. See harness/make_refbox.py.
    from . import make_refbox
    restated = _restatement(root, claim_id)
    box = Path(tempfile.mkdtemp(prefix=f"refbox-{claim_id}-"))
    # Hand over the precomputed censuses. Run 2 spent most of its 40 turns
    # recomputing a 50000-row census the repo already had, and never reached a
    # verdict. The referee should spend its turns on the proof, not on the
    # solver.
    cached = sorted((root / "GROUND_TRUTH" / "cache").glob("census_*.tsv"))
    box, leaks = make_refbox.build_box(root, claim, box, census=cached,
                                       statement=restated, deps=deps)
    if restated:
        print(f"[referee] using the provenance-free restatement of {claim_id} "
              f"from LEDGER/restatements.json")
    if leaks:
        print(f"[referee] WARNING: the submission for {claim_id} names "
              f"{leaks}. The claim statement reaches the referee verbatim, so "
              f"this tells it what answer is wanted. Recorded in the verdict; "
              f"use `make_refbox --statement` for a clean run.")
    refusals = 0
    # What the model is actually shown. build_box() applies the restatement to
    # its own copy for the box file; the wired path builds its own messages, so
    # it has to be applied here too or only the box would be clean.
    submitted = replace(claim, statement=restated) if restated else claim

    fingerprint = _fingerprint(build_messages(root, submitted, proof, deps))
    prog_path = _progress_path(root, claim_id)
    reusable: dict[float, dict] = {}
    if prog_path.exists():
        try:
            prev = json.loads(prog_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            prev = {}
        if prev.get("fingerprint") == fingerprint:
            reusable = {v["_temperature"]: v for v in prev.get("verdicts", [])
                        if v.get("disposition") not in (None, "inconclusive")}
            if reusable:
                print(f"[referee] resuming {claim_id}: reusing the finished "
                      f"pass(es) {sorted(reusable)} from run {prev.get('run')}")
        else:
            print(f"[referee] {prog_path.name} is for a different submission; "
                  f"starting {claim_id} from scratch")
    progress = {"claim": claim_id, "run": _run_id(), "fingerprint": fingerprint,
                "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "verdicts": []}

    def save_progress(state: str) -> None:
        progress.update(state=state, verdicts=verdicts,
                        updated=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        _write_json(prog_path, progress)

    save_progress("started")

    TURNS = 40
    forcing = False
    for temp in (0.3, 0.8):
        if temp in reusable:
            v = dict(reusable[temp])
            v.setdefault("_resumed_from_run", prev.get("run"))
            verdicts.append(v)
            print(f"[referee t={temp}] {v.get('disposition')} (reused)")
            continue
        pass_start = budget.spent
        log = _Transcript(root, claim_id, temp)
        messages = build_messages(root, submitted, proof, deps)
        for m in messages:
            log.add(m)
        save_progress(f"pass t={temp}")
        # The referee gets tools so it can actually hunt counterexamples.
        for turn in range(TURNS):
            left = TURNS - turn
            # Both passes of the first two runs simply ran out of turns -- the
            # spend cap never bit (they used $0.16 of $0.60) and nothing told
            # them the end was coming, so the loop exited on a tool call and
            # there was no verdict to parse. Warn, then force.
            forcing = budget.spent - start_spend >= max_spend or left <= 2
            if forcing:
                print(f"[referee] forcing a verdict "
                      f"({'spend cap' if left > 2 else 'out of turns'}).")
                messages.append({"role": "user", "content": FORCE_VERDICT})
            elif left <= 6:
                messages.append({"role": "user", "content":
                                 f"[HARNESS] {left} turns left. Stop starting "
                                 f"new computations and converge on a verdict."})
            reply = client.chat(
                messages,
                model=REFEREE_MODEL,
                # On the forced turn the tools are withdrawn. Asking for a
                # verdict is not enough: run 3's t=0.8 pass was asked, made a
                # tool call anyway, and the loop ended with no text to parse.
                # With no tools offered, a reply can only be the verdict.
                tools=None if forcing else tools.SCHEMA,
                temperature=temp,
                reasoning_effort="xhigh",
                tag=f"referee/{claim_id}/t{temp}",
            )
            messages.append({
                "role": "assistant",
                "content": reply.text,
                **({"tool_calls": reply.tool_calls} if reply.tool_calls else {}),
            })
            log.add(messages[-1], turn=turn,
                    spend=round(budget.spent - pass_start, 4))
            if not reply.tool_calls:
                break
            for call in reply.tool_calls:
                fn = call["function"]
                # Referee run 13 (MiMo) sent arguments cut off mid-string and
                # the bare json.loads killed the job with no verdict. Hand the
                # error back as the tool result, as session.py does.
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                except json.JSONDecodeError as e:
                    args = {}
                    result = (f"TOOL ERROR: unparseable arguments ({e}). "
                              f"Resend the call with valid JSON.")
                else:
                    result = tools.dispatch(fn["name"], args, box, sandbox=True)
                if result.startswith("REFUSED:") and "outside" in result:
                    refusals += 1
                    print(f"[referee t={temp}] blocked an escape: "
                          f"{str(args.get('command'))[:90]}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": result,
                })
                log.add(messages[-1], turn=turn)

        v = _parse(reply.text)
        if v is None and not forcing:
            # The loop above forces a verdict only when turns or spend run
            # out. Referee runs 14 and 15 (MiMo, C0024) ended neither way: the
            # model stopped calling tools and replied with something that did
            # not parse, and that was taken as the end of the pass. Ask once,
            # with the tools withdrawn, before calling it inconclusive.
            print(f"[referee t={temp}] no parseable verdict "
                  f"(finish_reason={reply.finish_reason!r}); asking once more.")
            messages.append({"role": "user", "content": FORCE_VERDICT})
            reply = client.chat(messages, model=REFEREE_MODEL, tools=None,
                                temperature=temp, reasoning_effort="xhigh",
                                tag=f"referee/{claim_id}/t{temp}")
            messages.append({"role": "assistant", "content": reply.text})
            log.add(messages[-1], turn="forced")
            v = _parse(reply.text)
        if v is None:
            # NOT a reject. A referee that never produced a verdict has said
            # nothing about the mathematics, and mapping that to `reject` --
            # which `refuted` follows from -- silently destroys correct claims.
            # The first run of this gate did exactly that to both claims it saw.
            v = {"disposition": "inconclusive", "gap_description":
                 "no parseable verdict: the referee did not finish. This is a "
                 "harness failure and says nothing about the claim.",
                 "confidence": "none",
                 # What the model actually sent, so the next failure can be
                 # diagnosed from the verdict file instead of guessed at.
                 "_finish_reason": reply.finish_reason,
                 "_raw_tail": reply.text[-2000:]}
        v["_temperature"] = temp
        v["_spend"] = round(budget.spent - pass_start, 4)
        v["_run"] = _run_id()
        verdicts.append(v)
        # Background jobs from this pass must not outlive it: they hold memory
        # the next pass needs, and they write files the next pass would read.
        tools.reap()
        save_progress(f"pass t={temp} done")
        print(f"[referee t={temp}] {v.get('disposition')} -- "
              f"{(v.get('gap_description') or '')[:110]}")

    d0, d1 = (v.get("disposition") for v in verdicts)
    agreed = d0 == d1
    # Only two outcomes may move a claim: both passes accepting promotes it,
    # both passes rejecting refutes it. Everything else means the gate did not
    # resolve, and the claim is left exactly as it was.
    #
    # The earlier rule -- "disagreement falls to the weaker verdict", i.e. to
    # reject -- refuted C0012 on a run where NEITHER pass rejected it: one said
    # `accept`, the other `accept_with_gaps`, both at high confidence and both
    # explicitly finding the proof correct. A disagreement about whether to
    # flag a caveat is not evidence of falsity, and neither is a genuine
    # accept/reject split: that is an unresolved question, not a refutation.
    if agreed and d0 in ("accept", "reject"):
        final = d0
    elif "inconclusive" in (d0, d1):
        final = "inconclusive"
    else:
        final = "unresolved"

    out_dir = root / "LEDGER" / "referee"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "claim": claim_id, "agreed": agreed, "final": final,
        "sandboxed": True,
        "restated": restated,          # null = judged on the ledger statement
        "ledger_statement": claim.statement if restated else None,
        "submission_leaks": leaks,
        "escape_attempts_blocked": refusals,
        "spend": round(sum(v.get("_spend", 0) for v in verdicts), 4),
        "run": _run_id(),
        "transcripts": f"runs/referee/run-{_run_id()}/",
        "verdicts": verdicts,
    }
    # An inconclusive run is a harness bug report, not a verdict. Keep it out of
    # the verdict directory, or `refereeable()` will treat the claim as judged
    # and never look at it again. Each failed attempt gets its own file:
    # one name per claim meant run 17 overwrote run 16's record of C0028.
    tries = attempts(root)
    n = tries.get(claim_id, 0) + 1
    name = (f"{claim_id}.json" if final in ("accept", "reject")
            else f"invalid/{claim_id}.{final}.{n}.json")
    (out_dir / name).parent.mkdir(parents=True, exist_ok=True)
    (out_dir / name).write_text(json.dumps(report, indent=2), encoding="utf-8")
    if final not in ("accept", "reject"):
        tries[claim_id] = n
        _attempts_path(root).write_text(json.dumps(tries, indent=2,
                                                   sort_keys=True) + "\n", encoding="utf-8")
    # The verdict file now carries both passes; the progress file has done its job.
    prog_path.unlink(missing_ok=True)

    results = [(v.get("novelty") or {}).get("result") for v in verdicts]
    known = any(r == "already known" for r in results)
    # Network is blocked in the sandbox, so the referee cannot actually search.
    # Recording novelty_checked=True on the strength of "it did not say the
    # result was known" would be a lie in the ledger; novelty is the operator's
    # job (OPERATOR_NOTES.md).
    novelty_checked = all(r == "novel" for r in results)

    if final == "accept" and not known:
        led.set_status(claim_id, "proven", session,
                       novelty_checked=novelty_checked)
        print(f"\n{claim_id} PROMOTED to proven"
              + ("." if novelty_checked
                 else " (novelty NOT checked -- the sandbox blocks search)."))
    elif final == "reject":
        led.set_status(
            claim_id, "refuted", session,
            evidence=verdicts[0].get("gap_description", "")[:400],
        )
        print(f"\n{claim_id} REFUTED by both passes. Record the lesson in "
              f"dead_ends.md.")
    elif final == "inconclusive":
        print(f"\n{claim_id} INCONCLUSIVE -- a pass did not finish. The claim "
              f"is untouched and remains refereeable. A harness problem to "
              f"fix, not a result.")
    elif agreed:
        # Run 16: C0029, C0032, C0033 -- both passes said accept_with_gaps.
        print(f"\n{claim_id} UNRESOLVED -- both passes said {d0}. The proof "
              f"needs its gaps filled before a rerun can accept it; they are "
              f"in LEDGER/referee/{name}.")
    else:
        print(f"\n{claim_id} UNRESOLVED -- the passes disagreed ({d0} vs {d1}). "
              f"Not promoted, and NOT refuted: a split is an open question, not "
              f"a refutation. The claim is untouched and remains refereeable; "
              f"read both verdicts in "
              f"LEDGER/referee/{name}.")

    return report


def main() -> None:
    ap = argparse.ArgumentParser(prog="harness.referee")
    ap.add_argument("claim_id", nargs="?", default="auto",
                    help="a claim id, or 'auto' for every refereeable claim")
    ap.add_argument("--root", default=".")
    ap.add_argument("--max-spend", type=float, default=1.00,
                    help="USD cap per claim (default 1.00)")
    ap.add_argument("--max-claims", type=int, default=3,
                    help="in auto mode, referee at most this many (default 3)")
    ap.add_argument("--list", action="store_true",
                    help="show what is refereeable and exit; spends nothing")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    led = Ledger(root / "LEDGER")

    if a.list or a.claim_id == "auto":
        ready, skipped = [], []
        resolved = led.resolved()
        tries = attempts(root)
        for c in sorted(resolved.values(), key=lambda c: c.id):
            ok, why = refereeable(root, c, resolved)
            (ready if ok else skipped).append((c.id, c.status, c.type, why))
        # Fewest failed attempts first, then id: a claim the referee cannot
        # finish goes to the back of the line instead of holding the front.
        ready.sort(key=lambda r: (tries.get(r[0], 0), r[0]))
        print(f"refereeable now ({len(ready)}), in queue order:")
        for cid, st, ty, ref in ready:
            n = tries.get(cid, 0)
            print(f"  {cid}  {st}/{ty}  {ref}"
                  + (f"  ({n} run{'s' * (n != 1)} without a verdict)" if n else ""))
        if a.list:
            print(f"\nnot yet ({len(skipped)}):")
            for cid, st, ty, why in skipped:
                print(f"  {cid}  {st}/{ty}  -- {why}")
            return
        if not ready:
            print("nothing to referee.")
            return
        for cid, *_ in ready[:a.max_claims]:
            print(f"\n=== refereeing {cid} ===")
            try:
                referee(root, cid, max_spend=a.max_spend)
            except NotRefereeable as e:
                print(f"skipped: {e}")
        return

    try:
        referee(root, a.claim_id, max_spend=a.max_spend)
    except NotRefereeable as e:
        print(f"skipped: {e}")


if __name__ == "__main__":
    main()
