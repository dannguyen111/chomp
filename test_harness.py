"""Offline tests. No network: the session loop runs against a fake model."""
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from harness import prompt, tools
from harness.ledger import Ledger, Claim
from harness.orclient import Budget, BudgetExhausted

ROOT = Path(__file__).parent


# No test may write to the real LEDGER/ or BUDGET.json. Four did: the first
# appended "N(r) <= 2r ..." as a live claim, the third a deliberately corrupt
# line, the prompt test a claim of its own, and the session test charged its
# fake spend to the real budget and wrote the real HANDOFF.md. Ledger tests get
# an empty ledger; anything that needs the real prompts and mission runs on a
# throwaway copy of the tracked repo.

def _empty_ledger() -> Ledger:
    return Ledger(Path(tempfile.mkdtemp(prefix="chomp-test-ledger-")))


def _sandbox_root() -> Path:
    """A copy of every tracked file except runs/, in a temp directory."""
    tmp = Path(tempfile.mkdtemp(prefix="chomp-test-root-"))
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                           text=True, check=True).stdout.splitlines()
    for f in files:
        if f.startswith("runs/") or not (ROOT / f).is_file():
            continue
        (tmp / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / f, tmp / f)
    (tmp / "runs").mkdir(exist_ok=True)
    return tmp


def _real_state() -> str:
    h = hashlib.sha256()
    for f in sorted((ROOT / "LEDGER").rglob("*")) + [ROOT / "BUDGET.json",
                                                    ROOT / "BUDGET.log.jsonl"]:
        if f.is_file():
            h.update(str(f.relative_to(ROOT)).encode() + f.read_bytes())
    return h.hexdigest()


def test_ledger_append_only_and_last_write_wins():
    led = _empty_ledger()
    c = led.add("N(r) <= 2r for all rows of period 2", type="conjecture",
                evidence="checked r<=10000", verified_range="r<=10000",
                session="S001")
    assert c.id == "C0001"
    led.set_status(c.id, "evidence", "S002", verified_range="r<=20000")
    led.set_status(c.id, "refuted", "S003", evidence="fails at r=6541")

    assert len(led.raw()) == 3, "history preserved"
    assert led.resolved()[c.id].status == "refuted"
    assert c.id not in {x.id for x in led.active()}, "refuted hidden from prompt"
    print("  ledger: 3 lines on disk, resolves to refuted, hidden from active")


def test_dependency_validation_and_ids():
    led = _empty_ledger()
    led.add("first claim", session="S001")
    b = led.add("mex structure forces f(q,r) >= q", session="S001")
    assert b.id == "C0002"
    led.add("bound follows", depends_on=[b.id], session="S001")
    try:
        led.add("bad", depends_on=["C9999"])
    except ValueError as e:
        print(f"  ledger: rejected unknown dependency ({e})")
    else:
        raise AssertionError("should have rejected unknown dep")


def test_malformed_line_survivable():
    led = _empty_ledger()
    led.add("one", session="S001")
    led.add("two", session="S001")
    with led.path.open("a", encoding="utf-8") as f:
        f.write("{ this is not json\n")
    led = Ledger(led.root)
    assert len(led.resolved()) == 2
    print("  ledger: corrupt line skipped, session survives")


def test_tools_protect_ground_truth():
    r = tools.dispatch("write_file",
                       {"path": "GROUND_TRUTH/solver.cpp", "content": "x"}, ROOT)
    assert r.startswith("REFUSED"), r
    r2 = tools.dispatch("write_file",
                        {"path": "../escape.txt", "content": "x"}, ROOT)
    assert "escapes" in r2 or "REFUSED" in r2, r2
    r3 = tools.dispatch("write_file",
                        {"path": "islands/01-recurrence/scratch/ok.py",
                         "content": "print(1)\n"}, ROOT)
    assert r3.startswith("wrote"), r3
    out = tools.dispatch("bash", {"command": "python islands/01-recurrence/scratch/ok.py"}, ROOT)
    assert out.strip() == "1", out
    print("  tools: GROUND_TRUTH protected, traversal blocked, scratch writable")


def test_sandbox_allows_scratch_but_not_escape():
    """The referee must be able to write and run a verification script.

    Run 7 (C0021, 2026-09-23) was blocked on
    `mkdir -p /tmp/gtest && cat > /tmp/gtest/grundy.py`, never retried inside
    the box, and then rejected a correct claim at high confidence on reasoning
    it had not checked.  /tmp holds nothing about this project; the controls
    that protect provenance are the network block, the sweep block, and the
    refusal of rooted paths into the real checkout.  This test pins both sides:
    scratch is writable, escapes still are not.
    """
    from pathlib import Path
    box = Path("/home/runner/work/chomp/chomp/refbox")
    allow = [
        "mkdir -p /tmp/gtest && cat > /tmp/gtest/grundy.py <<'EOF'",
        "python3 /tmp/gtest/grundy.py",
        "cd /tmp && python3 -c 'print(1)'",
        "ls /tmp/gtest",
        "python3 -c 'print(7 / 2)'",          # division must survive; it did not once
        "grep -n foo claim.md 2>/dev/null",
        "cat submission.md",
    ]
    deny = [
        "curl https://example.com",           # network: novelty is not its call
        "git log --oneline",
        "pip install sympy",
        "ls -la / && find / -maxdepth 3 -iname '*chomp*'",   # run 1 tried this
        "cat /home/runner/work/chomp/chomp/LEDGER/claims.jsonl",
        "cat ../../MISSION.md",
        "cat ~/.config/gh/hosts.yml",
        "cat /etc/passwd",
        "cat /tmpfoo/secrets",                # the /tmp rule must not match a prefix
    ]
    for c in allow:
        assert tools._escapes(c, box) is None, f"should allow: {c!r}"
    for c in deny:
        assert tools._escapes(c, box) is not None, f"should deny: {c!r}"
    print(f"  sandbox: {len(allow)} scratch/analysis commands allowed, "
          f"{len(deny)} escapes refused")


def test_tools_clip_runaway_output():
    out = tools.dispatch("bash", {"command": "python -c \"print('x'*200000)\""}, ROOT)
    assert len(out) < tools.MAX_OUTPUT + 500 and "elided" in out
    print(f"  tools: 200k-char output clipped to {len(out)}")


def test_prompt_ordering_and_fingerprint():
    root = _sandbox_root()
    # The marker used to arrive in the real ledger courtesy of the test above.
    Ledger(root / "LEDGER").add("mex structure forces f(q,r) >= q",
                                session="S999")
    msgs = prompt.build(root, "01-recurrence", "S999")
    system = msgs[0]["content"]
    user = msgs[1]["content"]
    assert "MISSION: Effective Byrnes" in system
    assert "{{ISLAND_THESIS}}" not in system, "thesis placeholder unfilled"
    assert "LEDGER" in user and "HANDOFF" in user
    # The real cache test: volatile claim text must live in the user message,
    # never in the cached system prefix.
    marker = "mex structure forces"
    assert marker in user, "ledger content missing from volatile suffix"
    assert marker not in system, "ledger content leaked into cached prefix"

    fp1 = prompt.prefix_fingerprint(root, "01-recurrence")
    Ledger(root / "LEDGER").add("a new claim churns the ledger", session="S999")
    fp2 = prompt.prefix_fingerprint(root, "01-recurrence")
    assert fp1 == fp2, "ledger churn must NOT invalidate the cached prefix"
    fp3 = prompt.prefix_fingerprint(root, "02-renorm")
    assert fp3 != fp1, "islands must have distinct prefixes"
    print(f"  prompt: prefix {fp1} stable across ledger writes; islands differ")


def test_budget_hard_cap():
    p = ROOT / "runs" / "_test_budget.json"
    p.unlink(missing_ok=True)
    b = Budget(p, cap=1.00)
    b.charge(0.40, "explorer")
    b.charge(0.40, "explorer")
    assert abs(b.remaining - 0.20) < 1e-9
    b.check(headroom=0.10)
    try:
        b.check(headroom=0.25)
    except BudgetExhausted as e:
        print(f"  budget: refused call with insufficient headroom ({e})")
    else:
        raise AssertionError("cap not enforced")
    p.unlink()
    b.log_path.unlink()


def test_budget_log_is_separate_and_migrates():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "BUDGET.json"
        old = [{"t": 1.0, "tag": "explorer", "cost": 0.25},
               {"t": 2.0, "tag": "referee", "cost": 0.5}]
        p.write_text(json.dumps({"cap": 1.0, "spent": 0.75, "calls": 2,
                                 "log": old}), encoding="utf-8")
        b = Budget(p, cap=1.0)
        assert "log" not in json.loads(p.read_text(encoding="utf-8"))
        b.charge(0.125, "referee/C0001", "some/model")
        summary = json.loads(p.read_text(encoding="utf-8"))
        assert summary == {"cap": 1.0, "spent": 0.875, "calls": 3}, summary
        lines = [json.loads(l) for l in
                 (Path(d) / "BUDGET.log.jsonl").read_text(encoding="utf-8").splitlines()]
        assert lines[:2] == old and lines[2]["model"] == "some/model"
        assert abs(sum(e["cost"] for e in lines) - summary["spent"]) < 1e-9
        Budget(p, cap=1.0)          # a second open must not duplicate the log
        assert len((Path(d) / "BUDGET.log.jsonl").read_text().splitlines()) == 3
    print("  budget: per-call log split out, legacy log migrated once")


def test_session_loop_with_fake_model():
    """Drive the real session loop against a scripted fake model."""
    import harness.session as S
    from harness.orclient import Reply

    script = [
        Reply("Plan: test the sqrt(2) ratio on period-3 rows.",
              [{"id": "1", "function": {"name": "bash",
                "arguments": json.dumps({"command": "echo 1.4142"})}}],
              0.05, 12000, 11000, 3000, "tool_calls"),
        Reply("Ratio holds. Logging.",
              [{"id": "2", "function": {"name": "write_file", "arguments":
                json.dumps({"path": "islands/01-recurrence/HANDOFF.md",
                            "content": "## State\nRatio holds on period-3.\n"})}}],
              0.05, 13000, 12000, 3000, "tool_calls"),
        Reply("Handoff written.", [], 0.02, 14000, 13000, 200, "stop"),
    ]
    calls = {"n": 0}

    def fake_chat(self, messages, **kw):
        i = min(calls["n"], len(script) - 1)
        calls["n"] += 1
        self.budget.charge(script[i].cost, kw.get("tag", ""))
        return script[i]

    orig = S.OpenRouter.chat
    S.OpenRouter.chat = fake_chat
    import os
    os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
    try:
        summary = S.run(_sandbox_root(), "01-recurrence",
                        max_output_tokens=20_000,
                        max_minutes=1, session_spend_cap=0.15)
    finally:
        S.OpenRouter.chat = orig

    assert summary["handoff_written"], "session must end with a handoff"
    assert summary["cost"] > 0
    print(f"  session: {summary['turns']} turns, ${summary['cost']:.2f}, "
          f"handoff written, budget respected")


def test_referee_parse_survives_braces_in_prose():
    """A set written before the verdict must not hide the verdict."""
    from harness.referee import _parse
    text = ('Checked R_n = {f(n,b): b<n} against the census.\n```json\n'
            '{"disposition": "accept", "novelty": {"result": "novel"}}\n```')
    v = _parse(text)
    assert v and v["disposition"] == "accept", v
    assert _parse("The set {1,2,3} is all I have.") is None
    print("  parse: verdict found past a brace in prose")


def test_referee_parse_repairs_unescaped_quotes():
    """Run 17, C0028 t=0.3: a whole verdict lost to quotes inside a string."""
    from harness.referee import _parse
    text = ('He wrote "so it holds, then stopped.\n```json\n{\n'
            '  "disposition": "accept_with_gaps",\n'
            '  "effectivity_check": "Closed form in Section 2-3: "g(1)=1, '
            'g(r+1)=g(r)(r+2)^(r+1)" and "h(1)=12", fully computable.",\n'
            '  "novelty": {"result": "inconclusive"},\n'
            '  "confidence": "medium"\n}\n```')
    v = _parse(text)
    assert v and v["disposition"] == "accept_with_gaps", v
    assert v["_repaired"] is True
    assert '"g(1)=1, ' in v["effectivity_check"]
    assert v["confidence"] == "medium"
    clean = _parse('{"disposition": "reject", "confidence": "high"}')
    assert "_repaired" not in clean
    print("  parse: unescaped inner quotes repaired and flagged")


def _referee_root(tmp: Path) -> Path:
    import shutil
    shutil.copy2(ROOT / "MISSION.md", tmp / "MISSION.md")
    (tmp / "prompts").mkdir()
    shutil.copy2(ROOT / "prompts" / "referee.md", tmp / "prompts" / "referee.md")
    (tmp / "isl" / "proofs").mkdir(parents=True)
    (tmp / "isl" / "proofs" / "p.md").write_text("Proof. Trivial.\n", encoding="utf-8")
    led = Ledger(tmp / "LEDGER")
    ref = "isl/proofs/p.md"
    led.append(Claim(id="C0001", statement="Lemma.", type="lemma", proof_ref=ref))
    led.append(Claim(id="C0002", statement="Targets.", type="observation",
                     proof_ref=ref))
    led.append(Claim(id="C0003", statement="Other.", type="lemma",
                     proof_ref=ref + " (section 2)"))
    return tmp


def test_referee_queue_and_dedup():
    """One referee pass per proof file; claims that keep failing go last."""
    import tempfile
    from harness import referee as R
    with tempfile.TemporaryDirectory() as d:
        root = _referee_root(Path(d))
        resolved = Ledger(root / "LEDGER").resolved()
        ok, why = R.refereeable(root, resolved["C0002"], resolved)
        assert not ok and "C0001" in why, why
        assert R.refereeable(root, resolved["C0002"])[0]   # no ledger, no dedup
        assert R.refereeable(root, resolved["C0003"], resolved)[0]
        R._attempts_path(root).parent.mkdir(parents=True)
        R._attempts_path(root).write_text('{"C0001": 2}', encoding="utf-8")
        assert R.attempts(root) == {"C0001": 2}
        (root / "LEDGER" / "referee" / "hold.json").write_text(
            '{"C0003": "prior art"}', encoding="utf-8")
        ok, why = R.refereeable(root, resolved["C0003"], resolved)
        assert not ok and "prior art" in why, why
    print("  queue: observation deduped onto its lemma, attempts read back")


def test_referee_asks_again_when_reply_does_not_parse():
    """Runs 14-15: the model stopped with prose. One forced retry, no tools."""
    import os
    import tempfile
    from harness import make_refbox
    from harness import referee as R
    from harness.orclient import Reply

    seen = []

    def fake_chat(self, messages, **kw):
        seen.append(kw.get("tools"))
        forced = messages[-1]["content"] == R.FORCE_VERDICT
        text = ('{"disposition": "accept", "confidence": "high"}' if forced
                else "I believe the set {a: a<n} works, so I am done.")
        self.budget.charge(0.01, kw.get("tag", ""))
        return Reply(text, [], 0.01, 10, 10, 0, "stop")

    orig_chat, orig_box = R.OpenRouter.chat, make_refbox.build_box
    R.OpenRouter.chat = fake_chat
    make_refbox.build_box = lambda root, claim, box, **kw: (box, [])
    os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
    try:
        with tempfile.TemporaryDirectory() as d:
            root = _referee_root(Path(d))
            report = R.referee(root, "C0001", max_spend=0.50)
            assert report["final"] == "accept", report
            assert (root / "LEDGER" / "referee" / "C0001.json").exists()
            assert Ledger(root / "LEDGER").resolved()["C0001"].status == "proven"
            assert not R._attempts_path(root).exists()
    finally:
        R.OpenRouter.chat, make_refbox.build_box = orig_chat, orig_box
    # Per pass: one call with tools, then the retry without them.
    assert seen == [R.tools.SCHEMA, None, R.tools.SCHEMA, None], seen
    print("  referee: unparseable reply -> one tool-less retry -> verdict")


def test_referee_keeps_every_failed_attempt():
    """Run 17 overwrote run 16's C0028 record. Each attempt gets its own file."""
    import os
    import tempfile
    from harness import make_refbox
    from harness import referee as R
    from harness.orclient import Reply

    def fake_chat(self, messages, **kw):
        # The two passes disagree, so every run is `unresolved`.
        d = "accept" if kw.get("temperature") == 0.3 else "accept_with_gaps"
        self.budget.charge(0.01, kw.get("tag", ""))
        return Reply('{"disposition": "%s"}' % d, [], 0.01, 10, 10, 0, "stop")

    orig_chat, orig_box = R.OpenRouter.chat, make_refbox.build_box
    R.OpenRouter.chat = fake_chat
    make_refbox.build_box = lambda root, claim, box, **kw: (box, [])
    os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
    try:
        with tempfile.TemporaryDirectory() as d:
            root = _referee_root(Path(d))
            for _ in range(2):
                assert R.referee(root, "C0001")["final"] == "unresolved"
            inv = root / "LEDGER" / "referee" / "invalid"
            assert sorted(p.name for p in inv.iterdir()) == [
                "C0001.unresolved.1.json", "C0001.unresolved.2.json"]
            assert R.attempts(root) == {"C0001": 2}
    finally:
        R.OpenRouter.chat, make_refbox.build_box = orig_chat, orig_box
    print("  referee: two failed attempts, two files, attempts=2")


def test_referee_resumes_a_dead_run():
    """Run 21 died mid-claim and lost everything. A finished pass survives in
    the progress file, the transcript is written turn by turn, and the next
    run of the same submission reuses the pass instead of paying again."""
    import os
    import tempfile
    from harness import make_refbox
    from harness import referee as R
    from harness.orclient import Reply

    calls = []

    def dying_chat(self, messages, **kw):
        calls.append(kw.get("temperature"))
        if kw.get("temperature") == 0.8:
            raise KeyboardInterrupt("runner lost")       # not an Exception
        self.budget.charge(0.01, kw.get("tag", ""))
        return Reply('{"disposition": "accept"}', [], 0.01, 10, 10, 0, "stop")

    def fine_chat(self, messages, **kw):
        calls.append(kw.get("temperature"))
        self.budget.charge(0.01, kw.get("tag", ""))
        return Reply('{"disposition": "accept"}', [], 0.01, 10, 10, 0, "stop")

    orig_chat, orig_box = R.OpenRouter.chat, make_refbox.build_box
    make_refbox.build_box = lambda root, claim, box, **kw: (box, [])
    os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
    try:
        with tempfile.TemporaryDirectory() as d:
            root = _referee_root(Path(d))
            prog = R._progress_path(root, "C0001")
            R.OpenRouter.chat = dying_chat
            try:
                R.referee(root, "C0001")
                assert False, "the fake runner should have died"
            except KeyboardInterrupt:
                pass
            saved = json.loads(prog.read_text(encoding="utf-8"))
            assert [v["disposition"] for v in saved["verdicts"]] == ["accept"]
            logs = sorted((root / "runs" / "referee").rglob("*.jsonl"))
            assert [p.name for p in logs] == ["C0001.t0.3.jsonl", "C0001.t0.8.jsonl"]
            assert 'disposition' in logs[0].read_text(encoding="utf-8")

            calls.clear()
            R.OpenRouter.chat = fine_chat
            report = R.referee(root, "C0001")
            assert calls == [0.8], calls                 # t=0.3 was reused
            assert report["final"] == "accept", report
            assert "_resumed_from_run" in report["verdicts"][0]
            assert report["spend"] == 0.02, report["spend"]
            assert not prog.exists()

            # A changed submission must not reuse an old pass.
            R._write_json(prog, saved)
            Ledger(root / "LEDGER").set_status("C0001", "open", "test")
            (root / "LEDGER" / "referee" / "C0001.json").unlink()
            ref = R._ref(Ledger(root / "LEDGER").resolved()["C0001"])
            (root / ref).write_text("a different proof", encoding="utf-8")
            calls.clear()
            R.referee(root, "C0001")
            assert calls == [0.3, 0.8], calls
    finally:
        R.OpenRouter.chat, make_refbox.build_box = orig_chat, orig_box
    print("  referee: dead pass saved, transcript on disk, resumed once")


def test_referee_fingerprint_and_unrun_searches():
    """A saved pass is not reused once the solver changes, and a verdict
    never records a search the sandbox refused."""
    from harness import referee as R
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "GROUND_TRUTH").mkdir()
        src = root / "GROUND_TRUTH" / "solver.cpp"
        src.write_text("int main(){}", encoding="utf-8")
        msgs = [{"role": "user", "content": "x"}]
        a = R._fingerprint(msgs, root)
        assert a == R._fingerprint(msgs, root)
        src.write_text("int main(){return 1;}", encoding="utf-8")
        assert a != R._fingerprint(msgs, root), "solver change kept the pass"
    v = {"novelty": {"searched": ["arXiv API: chomp"], "result": "inconclusive"}}
    R._strip_unrun_searches(v)
    assert v["novelty"]["searched"] == []
    assert v["novelty"]["_claimed_not_run"] == ["arXiv API: chomp"]
    print("  referee: fingerprint covers the solver; unrun searches not recorded")


def test_sandbox_memory_cap_and_reap():
    """A runaway allocation fails inside the command, not on the runner, and
    background jobs do not outlive reap()."""
    import os
    import time
    if os.name != "posix":
        return
    box = Path(tempfile.mkdtemp(prefix="chomp-test-box-"))
    out = tools.dispatch("bash", {"command": "python3 -c 'bytearray(%d)'"
                                  % int((tools.SANDBOX_MEM_GB + 1) * 2**30)},
                         box, sandbox=True)
    assert "MemoryError" in out, out
    tools.dispatch("bash", {"command": "nohup sleep 97 >/dev/null 2>&1 &"},
                   box, sandbox=True)
    tools.reap()
    time.sleep(0.2)
    ps = subprocess.run(["ps", "-eo", "args"], capture_output=True,
                        text=True).stdout
    assert "sleep 97" not in ps, "a background job survived reap()"
    print("  sandbox: memory cap bites, reap() kills background jobs")


if __name__ == "__main__":
    before = _real_state()
    for fn in [
        test_ledger_append_only_and_last_write_wins,
        test_dependency_validation_and_ids,
        test_malformed_line_survivable,
        test_tools_protect_ground_truth,
        test_sandbox_allows_scratch_but_not_escape,
        test_tools_clip_runaway_output,
        test_prompt_ordering_and_fingerprint,
        test_budget_hard_cap,
        test_budget_log_is_separate_and_migrates,
        test_session_loop_with_fake_model,
        test_referee_parse_survives_braces_in_prose,
        test_referee_parse_repairs_unescaped_quotes,
        test_referee_queue_and_dedup,
        test_referee_keeps_every_failed_attempt,
        test_referee_asks_again_when_reply_does_not_parse,
        test_referee_resumes_a_dead_run,
        test_referee_fingerprint_and_unrun_searches,
        test_sandbox_memory_cap_and_reap,
    ]:
        print(f"\n{fn.__name__}")
        fn()
    assert _real_state() == before, "a test wrote to the real LEDGER/ or BUDGET"
    print("\nAll harness tests passed.")
