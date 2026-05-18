"""Tests for enterprise/audit_api.py — query filters, pagination, tenant isolation, ndjson export."""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from enterprise.audit_api import (
    query_audit_log,
    export_audit_ndjson,
    _encode_cursor,
    DEFAULT_PAGE_SIZE,
)


def _write_ledger(tmp_path: Path, entries: list[dict]) -> Path:
    """Write JSONL ledger fixture to tmp_path/ledger.jsonl and return its path."""
    ledger = tmp_path / "ledger.jsonl"
    with ledger.open("w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry) + "\n")
    return ledger


def _make_entry(
    verdict: str = "verified",
    tenant_id: str = "org-a",
    signed_hash: str = "aabbcc",
    ts_offset: float = 0.0,
) -> dict:
    return {
        "verdict": verdict,
        "tenant_id": tenant_id,
        "signed_hash": signed_hash,
        "ts": time.time() + ts_offset,
    }


# ---------------------------------------------------------------------------
# Test 1: verdict_filter and since/until filters
# ---------------------------------------------------------------------------

def test_query_filters_by_verdict(tmp_path: Path):
    entries = [
        _make_entry("verified", signed_hash="hash1"),
        _make_entry("risky", signed_hash="hash2"),
        _make_entry("blocked", signed_hash="hash3"),
        _make_entry("verified", signed_hash="hash4"),
    ]
    ledger = _write_ledger(tmp_path, entries)

    result = query_audit_log(
        ledger,
        verdict_filter="verified",
        role="super_admin",
    )
    assert result["total_returned"] == 2
    assert all(e["verdict"] == "verified" for e in result["entries"])


def test_query_filters_by_since_until(tmp_path: Path):
    now = time.time()
    entries = [
        {**_make_entry(signed_hash="h1"), "ts": now - 7200},   # 2h ago
        {**_make_entry(signed_hash="h2"), "ts": now - 1800},   # 30m ago
        {**_make_entry(signed_hash="h3"), "ts": now - 60},     # 1m ago
    ]
    ledger = _write_ledger(tmp_path, entries)

    from datetime import datetime, timezone, timedelta
    since_str = datetime.fromtimestamp(now - 3600, tz=timezone.utc).isoformat()
    result = query_audit_log(ledger, since=since_str, role="super_admin")
    # Only entries within last 1 hour: h2 and h3
    assert result["total_returned"] == 2
    for e in result["entries"]:
        assert e["signed_hash"] in ("h2", "h3")


# ---------------------------------------------------------------------------
# Test 2: pagination cursor
# ---------------------------------------------------------------------------

def test_pagination_cursor_advances(tmp_path: Path):
    entries = [_make_entry(signed_hash=f"hash{i:02d}") for i in range(5)]
    ledger = _write_ledger(tmp_path, entries)

    # First page: limit=2
    page1 = query_audit_log(ledger, limit=2, role="super_admin")
    assert page1["total_returned"] == 2
    assert page1["next_cursor"] is not None

    # Second page using cursor
    page2 = query_audit_log(ledger, cursor=page1["next_cursor"], limit=2, role="super_admin")
    assert page2["total_returned"] == 2
    # entries on page2 must not overlap with page1
    page1_hashes = {e["signed_hash"] for e in page1["entries"]}
    page2_hashes = {e["signed_hash"] for e in page2["entries"]}
    assert page1_hashes.isdisjoint(page2_hashes)

    # Third page: only 1 entry left, no next_cursor
    page3 = query_audit_log(ledger, cursor=page2["next_cursor"], limit=2, role="super_admin")
    assert page3["total_returned"] == 1
    assert page3["next_cursor"] is None


# ---------------------------------------------------------------------------
# Test 3: cross-tenant blocked for non-super_admin
# ---------------------------------------------------------------------------

def test_cross_tenant_blocked_for_admin_role(tmp_path: Path):
    entries = [
        _make_entry("verified", tenant_id="org-a", signed_hash="ha1"),
        _make_entry("verified", tenant_id="org-b", signed_hash="hb1"),
        _make_entry("verified", tenant_id="org-a", signed_hash="ha2"),
    ]
    ledger = _write_ledger(tmp_path, entries)

    # admin role — only sees own org
    result = query_audit_log(
        ledger,
        role="admin",
        requester_org_id="org-a",
    )
    assert result["total_returned"] == 2
    assert all(e["tenant_id"] == "org-a" for e in result["entries"])

    # super_admin — sees everything
    result_super = query_audit_log(
        ledger,
        role="super_admin",
    )
    assert result_super["total_returned"] == 3


# ---------------------------------------------------------------------------
# Test 4: ndjson export yields correct lines
# ---------------------------------------------------------------------------

def test_ndjson_export_yields_lines(tmp_path: Path):
    entries = [
        _make_entry("verified", tenant_id="org-a", signed_hash="ex1"),
        _make_entry("blocked", tenant_id="org-b", signed_hash="ex2"),
        _make_entry("risky", tenant_id="org-a", signed_hash="ex3"),
    ]
    ledger = _write_ledger(tmp_path, entries)

    # super_admin gets all
    lines = list(export_audit_ndjson(ledger, role="super_admin"))
    assert len(lines) == 3
    assert all(line.endswith("\n") for line in lines)
    parsed = [json.loads(line) for line in lines]
    assert {e["signed_hash"] for e in parsed} == {"ex1", "ex2", "ex3"}

    # admin sees only own org
    lines_admin = list(export_audit_ndjson(ledger, role="admin", requester_org_id="org-a"))
    assert len(lines_admin) == 2
    parsed_admin = [json.loads(l) for l in lines_admin]
    assert all(e["tenant_id"] == "org-a" for e in parsed_admin)
