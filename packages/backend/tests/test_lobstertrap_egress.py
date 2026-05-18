"""Tests for LobsterTrap egress DPI — check_response_with_lobstertrap.

3 cases:
1. Credential-shaped output is blocked when LT binary returns DENY.
2. Benign output is allowed when LT binary returns ALLOW.
3. LOBSTERTRAP_CHECK_EGRESS unset means no-op (disabled, fail-open).
"""
from __future__ import annotations

import asyncio
import os

import pytest

import lobstertrap_client
from lobstertrap_client import check_response_with_lobstertrap


# ---------------------------------------------------------------------------
# Helpers — monkeypatch _check_via_subprocess so we never spawn a real process
# ---------------------------------------------------------------------------


def _make_deny_subprocess(monkeypatch):
    """Patch _check_via_subprocess to simulate LT returning DENY."""
    async def _fake_check(text: str, bin_path: str, policy_path: str) -> dict:
        return {
            "allowed": False,
            "reason": "[LOBSTERTRAP-EGRESS] Blocked: model attempted to leak credentials.",
            "latency_ms": 1.0,
            "source": "lobstertrap-subprocess",
            "raw_stdout": "",
        }
    monkeypatch.setattr(lobstertrap_client, "_check_via_subprocess", _fake_check)


def _make_allow_subprocess(monkeypatch):
    """Patch _check_via_subprocess to simulate LT returning ALLOW."""
    async def _fake_check(text: str, bin_path: str, policy_path: str) -> dict:
        return {
            "allowed": True,
            "reason": "ok",
            "latency_ms": 0.8,
            "source": "lobstertrap-subprocess",
            "raw_stdout": "",
        }
    monkeypatch.setattr(lobstertrap_client, "_check_via_subprocess", _fake_check)


# ---------------------------------------------------------------------------
# Test 1 — credential-shaped response is blocked
# ---------------------------------------------------------------------------


def test_egress_blocks_credential_leak(monkeypatch):
    """When LT detects credentials in model output, check_response_with_lobstertrap
    returns allowed=False with the LOBSTERTRAP-EGRESS deny message."""
    _make_deny_subprocess(monkeypatch)
    credential_output = "API key: sk-test-12345 OPENAI_API_KEY=sk-proj-abc"
    result = asyncio.run(
        check_response_with_lobstertrap(credential_output, lt_bin="/opt/lobstertrap/lobstertrap")
    )
    assert result["allowed"] is False
    assert "LOBSTERTRAP-EGRESS" in result["reason"]
    assert result["direction"] == "egress"
    assert result["latency_ms"] >= 0


# ---------------------------------------------------------------------------
# Test 2 — benign model output is allowed
# ---------------------------------------------------------------------------


def test_egress_allows_benign_response(monkeypatch):
    """When model output contains no flagged content, LT returns ALLOW."""
    _make_allow_subprocess(monkeypatch)
    benign_output = "The function looks correct. Consider adding a docstring."
    result = asyncio.run(
        check_response_with_lobstertrap(benign_output, lt_bin="/opt/lobstertrap/lobstertrap")
    )
    assert result["allowed"] is True
    assert result["reason"] == "ok"
    assert result["direction"] == "egress"


# ---------------------------------------------------------------------------
# Test 3 — env var off means no-op (LOBSTERTRAP_CHECK_EGRESS not set)
# ---------------------------------------------------------------------------


def test_egress_disabled_when_no_bin(monkeypatch):
    """When LOBSTERTRAP_BIN is not set and lt_bin=None, check_response_with_lobstertrap
    is a no-op and fails open (allowed=True, source=disabled)."""
    # Ensure env var is absent
    monkeypatch.delenv("LOBSTERTRAP_BIN", raising=False)
    result = asyncio.run(
        check_response_with_lobstertrap("any model output", lt_bin=None)
    )
    assert result["allowed"] is True
    assert result["source"] == "disabled"
    assert result["latency_ms"] == 0.0
