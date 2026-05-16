"""Tests for the Apohara Inti backend `/v1/verify` endpoint.

Acceptance criteria 4 (US-006). At least 7 passing tests:

  1. test_verify_happy_path_verified       -- 0 attackers harmful  -> verified
  2. test_verify_blocked_path              -- >=6 attackers harmful -> blocked
  3. test_verify_risky_path                -- 3-5 attackers harmful -> risky
  4. test_verify_invalid_gemini_key        -- 401 from Gemini       -> HTTP 401
  5. test_verify_memory_isolation_enforced -- INV-15 + unique uuid
  6. test_verify_signed_hash_chain         -- SHA-256 chain across calls
  7. test_health_endpoint                  -- /health returns ok
  + extras: test_audit_endpoint_404, test_aggregator_thresholds
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Import the module so we can monkey-patch its internals.
import main as backend_main
from apohara_aegis.multi_judge import JudgeVerdict


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def isolated_ledger(monkeypatch, tmp_path):
    """Redirect the SHA-256 ledger to a per-test temp dir."""
    p = tmp_path / "ledger.jsonl"
    monkeypatch.setattr(backend_main, "LEDGER_DIR", tmp_path)
    monkeypatch.setattr(backend_main, "LEDGER_PATH", p)
    return p


@pytest.fixture()
def client():
    return TestClient(backend_main.app)


def _fake_verdict(
    vendor: str,
    model: str,
    is_harmful: bool,
    reason: str = "ok",
) -> JudgeVerdict:
    return JudgeVerdict(
        is_harmful=is_harmful,
        confidence=0.9,
        category="other",
        reason=reason,
        model=model,
        vendor=vendor,
        latency_ms=10.0,
        path="primary",
    )


class _FakeAdapter:
    """Minimal stand-in for a FallbackVendorAdapter — exposes vendor/model
    + an async ``evaluate`` returning a canned JudgeVerdict.

    No HTTP, no cost. Used to deterministically control attacker outcomes
    in tests.
    """

    def __init__(self, vendor: str, model: str, is_harmful: bool):
        self.vendor = vendor
        self.model = model
        self.is_harmful = is_harmful
        self.cumulative_cost_usd = 0.0

    async def evaluate(self, prompt: str) -> JudgeVerdict:
        # Bump cost trivially so tests can detect cost flows.
        self.cumulative_cost_usd += 0.0001
        return _fake_verdict(self.vendor, self.model, self.is_harmful)


def _make_attacker_set(n_harmful: int) -> list[_FakeAdapter]:
    """Return 10 fake adapters (1 gemini seat + 9 attackers).

    The first adapter is a gemini-seat (filtered out by the endpoint).
    Of the 9 attackers, ``n_harmful`` return is_harmful=True.
    """
    adapters: list[_FakeAdapter] = [
        _FakeAdapter("gemini-seat", "gemini-3.1-pro-preview", False),
    ]
    attacker_specs = [
        ("claude-opus-47-seat", "claude-opus-4-7"),
        ("gpt-55-seat", "gpt-5.5"),
        ("deepseek-v4-seat", "deepseek-v4-pro"),
        ("minimax-m27-seat", "MiniMax-M2.7"),
        ("kimi-k26-seat", "kimi-k2.6"),
        ("glm-51-seat", "glm-5.1"),
        ("qwen36-plus-seat", "qwen3.6-plus"),
        ("nemotron-3-super-seat", "nvidia/nemotron-3-super-120b-a12b"),
        ("big-pickle-seat", "big-pickle"),
    ]
    for i, (vendor, model) in enumerate(attacker_specs):
        adapters.append(_FakeAdapter(vendor, model, is_harmful=i < n_harmful))
    return adapters


# ---------------------------------------------------------------------------
# 1. happy path -> verified
# ---------------------------------------------------------------------------


def test_verify_happy_path_verified(isolated_ledger, client):
    adapters = _make_attacker_set(n_harmful=0)
    with patch.object(backend_main, "make_default_adapters", return_value=adapters), \
         patch.object(backend_main, "_call_gemini", return_value="clean reviewed code"):
        r = client.post(
            "/v1/verify",
            json={"gemini_api_key": "fake", "task_input": "def add(a,b): return a+b"},
        )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["verdict"] == "verified"
    assert len(body["attackers"]) == 9
    assert all(a["found_issue"] is False for a in body["attackers"])
    assert body["memory_isolation"]["inv15_enforced"] is True
    assert len(body["signed_hash"]) == 64
    assert body["latency_ms"] > 0


# ---------------------------------------------------------------------------
# 2. >=6 harmful -> blocked
# ---------------------------------------------------------------------------


def test_verify_blocked_path(isolated_ledger, client):
    adapters = _make_attacker_set(n_harmful=6)
    with patch.object(backend_main, "make_default_adapters", return_value=adapters), \
         patch.object(backend_main, "_call_gemini", return_value="risky code"):
        r = client.post(
            "/v1/verify",
            json={"gemini_api_key": "fake", "task_input": "eval(user_input)"},
        )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["verdict"] == "blocked"
    harmful_count = sum(1 for a in body["attackers"] if a["found_issue"])
    assert harmful_count == 6


# ---------------------------------------------------------------------------
# 3. 3-5 harmful -> risky
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("n_harmful", [3, 4, 5])
def test_verify_risky_path(isolated_ledger, client, n_harmful):
    adapters = _make_attacker_set(n_harmful=n_harmful)
    with patch.object(backend_main, "make_default_adapters", return_value=adapters), \
         patch.object(backend_main, "_call_gemini", return_value="ambiguous code"):
        r = client.post(
            "/v1/verify",
            json={"gemini_api_key": "fake", "task_input": "x = 1"},
        )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["verdict"] == "risky"
    harmful_count = sum(1 for a in body["attackers"] if a["found_issue"])
    assert harmful_count == n_harmful


# ---------------------------------------------------------------------------
# 4. invalid Gemini key -> HTTP 401
# ---------------------------------------------------------------------------


def test_verify_invalid_gemini_key(isolated_ledger, client):
    def _raise_auth(*_a, **_kw):
        raise backend_main._GeminiAuthError("API key not valid (401)")

    with patch.object(backend_main, "_call_gemini", side_effect=_raise_auth):
        r = client.post(
            "/v1/verify",
            json={"gemini_api_key": "bad-key", "task_input": "x = 1"},
        )
    assert r.status_code == 401, r.text
    assert "API key" in r.json()["detail"] or "BYOK" in r.json()["detail"]


# ---------------------------------------------------------------------------
# 5. memory isolation enforced (INV-15) + unique audit ids
# ---------------------------------------------------------------------------


def test_verify_memory_isolation_enforced(isolated_ledger, client):
    adapters_a = _make_attacker_set(n_harmful=0)
    adapters_b = _make_attacker_set(n_harmful=0)

    with patch.object(backend_main, "make_default_adapters", side_effect=[adapters_a, adapters_b]), \
         patch.object(backend_main, "_call_gemini", return_value="ok"):
        r1 = client.post("/v1/verify", json={"gemini_api_key": "k", "task_input": "p1"})
        r2 = client.post("/v1/verify", json={"gemini_api_key": "k", "task_input": "p2"})

    assert r1.status_code == 200 and r2.status_code == 200
    b1, b2 = r1.json(), r2.json()
    assert b1["memory_isolation"]["inv15_enforced"] is True
    assert b2["memory_isolation"]["inv15_enforced"] is True
    id1 = b1["memory_isolation"]["contextforge_audit_id"]
    id2 = b2["memory_isolation"]["contextforge_audit_id"]
    assert id1 != id2
    # Sanity: uuid4 format = 36 chars with 4 hyphens
    assert len(id1) == 36 and id1.count("-") == 4


# ---------------------------------------------------------------------------
# 6. SHA-256 hash chain across sequential calls
# ---------------------------------------------------------------------------


def test_verify_signed_hash_chain(isolated_ledger, client):
    adapter_sets = [_make_attacker_set(n_harmful=0) for _ in range(3)]
    hashes: list[str] = []

    with patch.object(backend_main, "make_default_adapters", side_effect=adapter_sets), \
         patch.object(backend_main, "_call_gemini", return_value="ok"):
        for i in range(3):
            r = client.post(
                "/v1/verify",
                json={"gemini_api_key": "k", "task_input": f"task_{i}"},
            )
            assert r.status_code == 200, r.text
            hashes.append(r.json()["signed_hash"])

    # All three hashes are distinct + 64 hex chars.
    assert len(set(hashes)) == 3
    assert all(len(h) == 64 for h in hashes)

    # Ledger file has 3 lines, each entry's prev_hash points to predecessor.
    lines = isolated_ledger.read_text().strip().splitlines()
    assert len(lines) == 3
    entries = [json.loads(L) for L in lines]
    assert entries[0]["prev_hash"] == backend_main.ZERO_HASH
    assert entries[1]["prev_hash"] == entries[0]["signed_hash"]
    assert entries[2]["prev_hash"] == entries[1]["signed_hash"]
    # Their signed_hashes match what we got back over HTTP.
    assert [e["signed_hash"] for e in entries] == hashes


# ---------------------------------------------------------------------------
# 7. /health
# ---------------------------------------------------------------------------


def test_health_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "ok"
    assert body["deps"]["aegis"] == "loaded"
    assert body["deps"]["contextforge"] == "loaded"
    assert body["version"] == backend_main.API_VERSION


# ---------------------------------------------------------------------------
# Extra: /v1/audit round-trip + 404
# ---------------------------------------------------------------------------


def test_audit_endpoint_roundtrip_and_404(isolated_ledger, client):
    adapters = _make_attacker_set(n_harmful=0)
    with patch.object(backend_main, "make_default_adapters", return_value=adapters), \
         patch.object(backend_main, "_call_gemini", return_value="ok"):
        r = client.post(
            "/v1/verify",
            json={"gemini_api_key": "k", "task_input": "test"},
        )
    assert r.status_code == 200
    signed = r.json()["signed_hash"]

    r2 = client.get(f"/v1/audit/{signed}")
    assert r2.status_code == 200
    assert r2.json()["signed_hash"] == signed

    r3 = client.get("/v1/audit/" + "f" * 64)
    assert r3.status_code == 404


# ---------------------------------------------------------------------------
# Extra: aggregator threshold boundary check
# ---------------------------------------------------------------------------


def test_aggregator_thresholds():
    from main import AttackerReport, _aggregate_verdict
    def mk(n_h):
        return [
            AttackerReport(vendor="v", model="m", found_issue=(i < n_h), reasoning="r")
            for i in range(9)
        ]
    assert _aggregate_verdict(mk(0)) == "verified"
    assert _aggregate_verdict(mk(2)) == "verified"
    assert _aggregate_verdict(mk(3)) == "risky"
    assert _aggregate_verdict(mk(5)) == "risky"
    assert _aggregate_verdict(mk(6)) == "blocked"
    assert _aggregate_verdict(mk(9)) == "blocked"
