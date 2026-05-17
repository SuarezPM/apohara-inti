"""In-memory per-IP daily quota for /v1/demo_verify. UTC-midnight rollover,
asyncio.Lock for concurrent safety; state is process-local (restarts reset)."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone


def _utc_now() -> datetime:
    """Indirection so tests can monkeypatch the clock."""
    return datetime.now(timezone.utc)


def _next_utc_midnight(now: datetime) -> datetime:
    """Next 00:00 UTC strictly after ``now`` (or equal-to ``now`` if exact)."""
    midnight_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight_today + timedelta(days=1)


class DailyRateLimiter:
    """Per-IP daily quota with UTC-midnight rollover; thread-safe under asyncio."""

    def __init__(self, max_per_day: int = 5) -> None:
        self.max_per_day = max_per_day
        self._ip_to_timestamps: dict[str, list[datetime]] = {}
        self._lock = asyncio.Lock()

    async def check_and_consume(
        self, ip: str
    ) -> tuple[bool, int, datetime]:
        """Try to consume one quota slot for ``ip``. Returns
        ``(allowed, remaining_today, reset_at_utc_midnight)``. Denial is
        idempotent: when allowed=False no state changes."""
        now = _utc_now()
        reset_at = _next_utc_midnight(now)
        today_start = reset_at - timedelta(days=1)
        async with self._lock:
            ts = [t for t in self._ip_to_timestamps.get(ip, []) if t >= today_start]
            if len(ts) >= self.max_per_day:
                self._ip_to_timestamps[ip] = ts
                return False, 0, reset_at
            ts.append(now)
            self._ip_to_timestamps[ip] = ts
            remaining = self.max_per_day - len(ts)
            return True, remaining, reset_at
