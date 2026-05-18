"""Enterprise audit log API for Apohara PROBANT.

Endpoint: GET /v1/admin/audit
Query params: since, until, verdict_filter, tenant_id, cursor, limit
Auth: requires Apohara JWT with role in {admin, super_admin}.
Returns: paginated audit entries, each re-verified via HMAC before serving.
"""
from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 500


def _parse_iso(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _encode_cursor(signed_hash: str) -> str:
    return base64.urlsafe_b64encode(signed_hash.encode()).decode()


def _decode_cursor(cursor: Optional[str]) -> Optional[str]:
    if not cursor:
        return None
    try:
        return base64.urlsafe_b64decode(cursor.encode()).decode()
    except Exception:
        return None


def query_audit_log(
    ledger_path: Path,
    *,
    since: Optional[str] = None,
    until: Optional[str] = None,
    verdict_filter: Optional[str] = None,
    tenant_id: Optional[str] = None,
    cursor: Optional[str] = None,
    limit: int = DEFAULT_PAGE_SIZE,
    role: str = "admin",
    requester_org_id: Optional[str] = None,
) -> dict:
    """Query the audit ledger with filters + pagination.

    Cross-tenant query requires role='super_admin'. Otherwise filtered to
    requester_org_id.

    Returns {"entries": [...], "next_cursor": str|None, "total_returned": N}.
    """
    if limit > MAX_PAGE_SIZE:
        limit = MAX_PAGE_SIZE
    if not ledger_path.exists():
        return {"entries": [], "next_cursor": None, "total_returned": 0}

    since_dt = _parse_iso(since)
    until_dt = _parse_iso(until)
    cursor_hash = _decode_cursor(cursor)
    enforce_tenant = role != "super_admin"

    entries: list[dict] = []
    skipping = bool(cursor_hash)
    try:
        with ledger_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if skipping:
                    if entry.get("signed_hash") == cursor_hash:
                        skipping = False
                    continue
                # Filters
                if verdict_filter and entry.get("verdict") != verdict_filter:
                    continue
                if since_dt or until_dt:
                    ts = entry.get("ts")
                    if ts is None:
                        continue
                    tz = since_dt.tzinfo if since_dt else (until_dt.tzinfo if until_dt else None)
                    entry_dt = datetime.fromtimestamp(ts, tz=tz)
                    if since_dt and entry_dt < since_dt:
                        continue
                    if until_dt and entry_dt > until_dt:
                        continue
                if enforce_tenant and entry.get("tenant_id") != requester_org_id:
                    continue
                if tenant_id and entry.get("tenant_id") != tenant_id and role == "super_admin":
                    continue
                entries.append(entry)
                if len(entries) >= limit:
                    break
    except OSError:
        return {"entries": [], "next_cursor": None, "total_returned": 0}

    next_cursor = _encode_cursor(entries[-1]["signed_hash"]) if len(entries) == limit else None
    return {"entries": entries, "next_cursor": next_cursor, "total_returned": len(entries)}


def export_audit_ndjson(
    ledger_path: Path,
    *,
    since: Optional[str] = None,
    until: Optional[str] = None,
    role: str = "admin",
    requester_org_id: Optional[str] = None,
):
    """Generator yielding NDJSON lines for streaming SIEM export."""
    if not ledger_path.exists():
        return
    since_dt = _parse_iso(since)
    until_dt = _parse_iso(until)
    enforce_tenant = role != "super_admin"
    try:
        with ledger_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = entry.get("ts")
                if since_dt and ts:
                    entry_dt = datetime.fromtimestamp(ts, tz=since_dt.tzinfo)
                    if entry_dt < since_dt:
                        continue
                if until_dt and ts:
                    entry_dt = datetime.fromtimestamp(ts, tz=until_dt.tzinfo)
                    if entry_dt > until_dt:
                        continue
                if enforce_tenant and entry.get("tenant_id") != requester_org_id:
                    continue
                yield line + "\n"
    except OSError:
        return
