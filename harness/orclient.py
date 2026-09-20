"""OpenRouter client with a hard, persistent spend cap.

Two things matter here and nothing else does:

1. The budget cap is enforced on disk, before every call, in a file that
   survives crashes. $30 total means $30 total.
2. Cost comes from OpenRouter's own accounting (usage.include), not from
   multiplying token counts by prices I hardcoded. Prices change; the
   `deepseek/deepseek-v4-pro` slug floats between versions. Never guess.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

import requests

API = "https://openrouter.ai/api/v1/chat/completions"

# Pin the version. The bare slug floats to whatever is current.
EXPLORER_MODEL = "deepseek/deepseek-v4-pro-0813"
REFEREE_MODEL = "deepseek/deepseek-v4-pro-0813"
LIBRARIAN_MODEL = "deepseek/deepseek-v4-flash"


class BudgetExhausted(RuntimeError):
    pass


@dataclass
class Reply:
    text: str
    tool_calls: list[dict]
    cost: float
    prompt_tokens: int
    completion_tokens: int
    cached_tokens: int
    finish_reason: str


class Budget:
    """Persistent spend ledger. Survives crashes; refuses to be talked into
    going over."""

    def __init__(self, path: str | os.PathLike = "BUDGET.json", cap: float = 30.0):
        self.path = Path(path)
        self.cap = cap
        if not self.path.exists():
            self._write({"cap": cap, "spent": 0.0, "calls": 0, "log": []})

    def _read(self) -> dict:
        return json.loads(self.path.read_text())

    def _write(self, d: dict) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(d, indent=2))
        tmp.replace(self.path)  # atomic

    @property
    def spent(self) -> float:
        return self._read()["spent"]

    @property
    def remaining(self) -> float:
        d = self._read()
        return d["cap"] - d["spent"]

    def check(self, headroom: float = 0.25) -> None:
        if self.remaining < headroom:
            raise BudgetExhausted(
                f"${self.spent:.2f} of ${self.cap:.2f} spent, "
                f"${self.remaining:.2f} left (need ${headroom:.2f})"
            )

    def charge(self, cost: float, tag: str) -> None:
        d = self._read()
        d["spent"] = round(d["spent"] + cost, 6)
        d["calls"] += 1
        d["log"].append({"t": time.time(), "tag": tag, "cost": cost})
        self._write(d)


class OpenRouter:
    def __init__(self, budget: Budget, api_key: str | None = None):
        self.budget = budget
        self.key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.key:
            raise RuntimeError("set OPENROUTER_API_KEY")
        self.session = requests.Session()

    def chat(
        self,
        messages: list[dict],
        *,
        model: str = EXPLORER_MODEL,
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        reasoning_effort: str | None = "xhigh",
        max_tokens: int = 32_000,
        response_format: dict | None = None,
        tag: str = "",
        max_retries: int = 5,
    ) -> Reply:
        self.budget.check()

        body: dict = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            # Ask OpenRouter to report what it actually charged us.
            "usage": {"include": True},
        }
        if reasoning_effort:
            body["reasoning"] = {"effort": reasoning_effort}
        if tools:
            body["tools"] = tools
            body["tool_choice"] = "auto"
        if response_format:
            body["response_format"] = response_format

        delay = 2.0
        for attempt in range(max_retries):
            try:
                r = self.session.post(
                    API,
                    headers={
                        "Authorization": f"Bearer {self.key}",
                        "Content-Type": "application/json",
                    },
                    json=body,
                    timeout=1800,  # xhigh reasoning on hard maths is slow
                )
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                print(f"[or] network error ({e}); retry in {delay:.0f}s")
                time.sleep(delay)
                delay *= 2
                continue

            if r.status_code in (429, 500, 502, 503, 520, 524):
                if attempt == max_retries - 1:
                    r.raise_for_status()
                print(f"[or] http {r.status_code}; retry in {delay:.0f}s")
                time.sleep(delay)
                delay *= 2
                continue
            r.raise_for_status()
            break

        data = r.json()
        if "error" in data:
            raise RuntimeError(f"openrouter error: {data['error']}")

        usage = data.get("usage") or {}
        cost = float(usage.get("cost", 0.0))
        self.budget.charge(cost, tag or model)

        choice = data["choices"][0]
        msg = choice.get("message") or {}
        details = usage.get("prompt_tokens_details") or {}

        return Reply(
            text=msg.get("content") or "",
            tool_calls=msg.get("tool_calls") or [],
            cost=cost,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            cached_tokens=details.get("cached_tokens", 0),
            finish_reason=choice.get("finish_reason", ""),
        )
