"""Offline tests. No network: the session loop runs against a fake model."""
import json
from pathlib import Path

from harness import prompt, tools
from harness.ledger import Ledger, Claim
from harness.orclient import Budget, BudgetExhausted

ROOT = Path(__file__).parent


def test_ledger_append_only_and_last_write_wins():
    led = Ledger(ROOT / "LEDGER")
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
    led = Ledger(ROOT / "LEDGER")
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
    p = ROOT / "LEDGER" / "claims.jsonl"
    p.open("a").write("{ this is not json\n")
    led = Ledger(ROOT / "LEDGER")
    assert len(led.resolved()) >= 2
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
    msgs = prompt.build(ROOT, "01-recurrence", "S999")
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

    fp1 = prompt.prefix_fingerprint(ROOT, "01-recurrence")
    Ledger(ROOT / "LEDGER").add("a new claim churns the ledger", session="S999")
    fp2 = prompt.prefix_fingerprint(ROOT, "01-recurrence")
    assert fp1 == fp2, "ledger churn must NOT invalidate the cached prefix"
    fp3 = prompt.prefix_fingerprint(ROOT, "02-renorm")
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
        summary = S.run(ROOT, "01-recurrence", max_output_tokens=20_000,
                        max_minutes=1, session_spend_cap=0.15)
    finally:
        S.OpenRouter.chat = orig

    assert summary["handoff_written"], "session must end with a handoff"
    assert summary["cost"] > 0
    print(f"  session: {summary['turns']} turns, ${summary['cost']:.2f}, "
          f"handoff written, budget respected")


if __name__ == "__main__":
    for fn in [
        test_ledger_append_only_and_last_write_wins,
        test_dependency_validation_and_ids,
        test_malformed_line_survivable,
        test_tools_protect_ground_truth,
        test_sandbox_allows_scratch_but_not_escape,
        test_tools_clip_runaway_output,
        test_prompt_ordering_and_fingerprint,
        test_budget_hard_cap,
        test_session_loop_with_fake_model,
    ]:
        print(f"\n{fn.__name__}")
        fn()
    print("\nAll harness tests passed.")
