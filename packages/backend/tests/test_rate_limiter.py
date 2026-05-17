"""Tests for packages/backend/rate_limiter.py — 5 cases covering the
acceptance-criteria paths (under_limit, at_limit, over_limit,
midnight_reset_drops_yesterday, distinct_ips_independent)."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import rate_limiter
from rate_limiter import DailyRateLimiter


def _set_clock(monkeypatch, dt: datetime) -> None:
    monkeypatch.setattr(rate_limiter, "_utc_now", lambda: dt)


def test_under_limit_allows_with_decreasing_remaining(monkeypatch):
    limiter = DailyRateLimiter(max_per_day=5)
    _set_clock(monkeypatch, datetime(2026, 5, 17, 12, 0, tzinfo=timezone.utc))
    for i in range(4):
        ok, remaining, reset_at = asyncio.run(limiter.check_and_consume("1.2.3.4"))
        assert ok is True, f"call {i+1} should be allowed"
        assert remaining == 5 - (i + 1)
        assert reset_at == datetime(2026, 5, 18, 0, 0, tzinfo=timezone.utc)


def test_at_limit_last_call_allows_with_zero_remaining(monkeypatch):
    limiter = DailyRateLimiter(max_per_day=5)
    _set_clock(monkeypatch, datetime(2026, 5, 17, 12, 0, tzinfo=timezone.utc))
    for _ in range(4):
        asyncio.run(limiter.check_and_consume("1.2.3.4"))
    ok, remaining, _ = asyncio.run(limiter.check_and_consume("1.2.3.4"))
    assert ok is True
    assert remaining == 0


def test_over_limit_denies_without_state_change(monkeypatch):
    limiter = DailyRateLimiter(max_per_day=3)
    _set_clock(monkeypatch, datetime(2026, 5, 17, 12, 0, tzinfo=timezone.utc))
    for _ in range(3):
        asyncio.run(limiter.check_and_consume("1.2.3.4"))
    ok, remaining, reset_at = asyncio.run(limiter.check_and_consume("1.2.3.4"))
    assert ok is False
    assert remaining == 0
    assert reset_at == datetime(2026, 5, 18, 0, 0, tzinfo=timezone.utc)
    ok2, remaining2, _ = asyncio.run(limiter.check_and_consume("1.2.3.4"))
    assert ok2 is False
    assert remaining2 == 0


def test_midnight_reset_drops_yesterday(monkeypatch):
    limiter = DailyRateLimiter(max_per_day=2)
    _set_clock(monkeypatch, datetime(2026, 5, 17, 23, 30, tzinfo=timezone.utc))
    asyncio.run(limiter.check_and_consume("1.2.3.4"))
    asyncio.run(limiter.check_and_consume("1.2.3.4"))
    ok_pre, _, _ = asyncio.run(limiter.check_and_consume("1.2.3.4"))
    assert ok_pre is False, "limit reached on day 1"
    _set_clock(monkeypatch, datetime(2026, 5, 18, 0, 15, tzinfo=timezone.utc))
    ok_post, remaining, reset_at = asyncio.run(limiter.check_and_consume("1.2.3.4"))
    assert ok_post is True, "fresh day → quota restored"
    assert remaining == 1
    assert reset_at == datetime(2026, 5, 19, 0, 0, tzinfo=timezone.utc)


def test_distinct_ips_independent(monkeypatch):
    limiter = DailyRateLimiter(max_per_day=2)
    _set_clock(monkeypatch, datetime(2026, 5, 17, 12, 0, tzinfo=timezone.utc))
    asyncio.run(limiter.check_and_consume("1.2.3.4"))
    asyncio.run(limiter.check_and_consume("1.2.3.4"))
    ok_a, _, _ = asyncio.run(limiter.check_and_consume("1.2.3.4"))
    assert ok_a is False
    ok_b, remaining_b, _ = asyncio.run(limiter.check_and_consume("5.6.7.8"))
    assert ok_b is True
    assert remaining_b == 1
