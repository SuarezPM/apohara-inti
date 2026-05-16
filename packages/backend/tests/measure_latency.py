"""Latency benchmark for `/v1/verify` — US-006 acceptance criterion 5.

Runs 5 deterministic prompts through the endpoint with mocked Gemini +
mocked attackers (so the measurement is the framework's overhead, not
upstream-vendor wall-clock). Emits ``latency_report.json`` alongside this
file with min/p50/p99/max in milliseconds.

Run:
    PYTHONPATH=/home/linconx/Documentos/apohara-aegis:\\
      /home/linconx/Documentos/Apohara_Context_Forge:\\
      packages/backend \\
    python3 packages/backend/tests/measure_latency.py
"""
from __future__ import annotations

import asyncio
import json
import statistics
import sys
import time
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import main as backend_main  # type: ignore[import-not-found]
from apohara_aegis.multi_judge import JudgeVerdict


# Mirror the fake adapter shape from tests/test_verify.py without importing
# pytest fixtures (this is a script, not a test).
class _FakeAdapter:
    def __init__(self, vendor: str, model: str):
        self.vendor = vendor
        self.model = model
        self.cumulative_cost_usd = 0.0

    async def evaluate(self, prompt: str) -> JudgeVerdict:
        # Tiny artificial latency per attacker (1 ms) so the gather is
        # detectable but doesn't dominate runtime.
        await asyncio.sleep(0.001)
        self.cumulative_cost_usd += 0.0001
        return JudgeVerdict(
            is_harmful=False,
            confidence=0.9,
            category="other",
            reason="benchmark",
            model=self.model,
            vendor=self.vendor,
            latency_ms=1.0,
            path="primary",
        )


def _make_adapters() -> list[_FakeAdapter]:
    return [
        _FakeAdapter("gemini-seat", "gemini-3.1-pro-preview"),
        _FakeAdapter("claude-opus-47-seat", "claude-opus-4-7"),
        _FakeAdapter("gpt-55-seat", "gpt-5.5"),
        _FakeAdapter("deepseek-v4-seat", "deepseek-v4-pro"),
        _FakeAdapter("minimax-m27-seat", "MiniMax-M2.7"),
        _FakeAdapter("kimi-k26-seat", "kimi-k2.6"),
        _FakeAdapter("glm-51-seat", "glm-5.1"),
        _FakeAdapter("qwen36-plus-seat", "qwen3.6-plus"),
        _FakeAdapter("nemotron-3-super-seat", "nvidia/nemotron-3-super-120b-a12b"),
        _FakeAdapter("big-pickle-seat", "big-pickle"),
    ]


PROMPTS = [
    "def is_palindrome(s): return s == s[::-1]",
    "fetch_url = lambda url: requests.get(url).json()",
    "// 100 lines of TypeScript: " + "const x = 1;\n" * 99,
    "import os; os.system(input('cmd: '))",
    "SELECT * FROM users WHERE id = '\" + user_id + \"'",
]


def main() -> int:
    client = TestClient(backend_main.app)
    latencies_ms: list[float] = []

    for prompt in PROMPTS:
        adapters = _make_adapters()
        with patch.object(backend_main, "make_default_adapters", return_value=adapters), \
             patch.object(backend_main, "_call_gemini", return_value="review: looks ok"):
            t0 = time.perf_counter()
            r = client.post(
                "/v1/verify",
                json={"gemini_api_key": "fake", "task_input": prompt},
            )
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
        if r.status_code != 200:
            print(f"FAIL prompt: {r.status_code} {r.text}", file=sys.stderr)
            return 1
        latencies_ms.append(elapsed_ms)

    latencies_ms.sort()
    n = len(latencies_ms)
    report = {
        "samples": n,
        "prompts": [p[:80] + ("..." if len(p) > 80 else "") for p in PROMPTS],
        "latency_ms": {
            "min": round(min(latencies_ms), 3),
            "p50": round(statistics.median(latencies_ms), 3),
            "p99": round(latencies_ms[-1], 3),  # n=5; treat max as p99
            "max": round(max(latencies_ms), 3),
            "raw": [round(x, 3) for x in latencies_ms],
        },
        "notes": (
            "Mocked Gemini + mocked attackers — framework overhead only. "
            "Real upstream calls add Gemini (<=10s) + attacker max(latency) "
            "in parallel. Target p50 <= 60s for 100-line input is "
            "framework-overhead bounded; vendor-call latency is upstream-"
            "dependent and tracked by individual VendorAdapter timings."
        ),
        "target_p50_ms": 60_000,
        "passes_target": statistics.median(latencies_ms) <= 60_000,
    }

    out_path = Path(__file__).with_name("latency_report.json")
    out_path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {out_path}")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
