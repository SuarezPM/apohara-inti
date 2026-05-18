"""Multi-tenant model for Apohara PROBANT SaaS layer.

Each tenant has: org_id (UUID), per-org HMAC key (rotated from global),
plan (free/pro/enterprise), monthly_quota, used_calls_this_month,
stripe_customer_id, created_at.

Backed by SQLite at $APOHARA_TENANT_DB (default /opt/apohara-inti/tenants.db).
Activated only when APOHARA_MULTI_TENANT=1 env set — single-tenant mode
preserved as default for hackathon stability.
"""
from __future__ import annotations

import os
import sqlite3
import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_DB_PATH = Path(os.environ.get("APOHARA_TENANT_DB", "/opt/apohara-inti/tenants.db"))

PLAN_QUOTAS = {
    "free": 100,        # 100 /v1/verify calls per month
    "pro": 5_000,
    "enterprise": 100_000,
}


def init_schema(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Create tables if not exist. Idempotent."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tenants (
                org_id TEXT PRIMARY KEY,
                org_name TEXT NOT NULL,
                hmac_key TEXT NOT NULL,
                plan TEXT NOT NULL DEFAULT 'free',
                monthly_quota INTEGER NOT NULL,
                used_calls_this_month INTEGER NOT NULL DEFAULT 0,
                quota_reset_at TEXT NOT NULL,
                stripe_customer_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_tenants_plan ON tenants(plan);
            CREATE INDEX IF NOT EXISTS idx_tenants_stripe ON tenants(stripe_customer_id);
        """)
        conn.commit()
    finally:
        conn.close()


def create_tenant(
    org_name: str,
    plan: str = "free",
    db_path: Path = DEFAULT_DB_PATH,
) -> dict:
    """Create a new tenant with fresh HMAC key. Returns full record."""
    if plan not in PLAN_QUOTAS:
        raise ValueError(f"unknown plan: {plan}")
    init_schema(db_path)
    org_id = str(uuid.uuid4())
    hmac_key = secrets.token_hex(32)
    now = datetime.now(timezone.utc).isoformat()
    quota_reset = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            "INSERT INTO tenants (org_id, org_name, hmac_key, plan, monthly_quota, "
            "used_calls_this_month, quota_reset_at, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?)",
            (org_id, org_name, hmac_key, plan, PLAN_QUOTAS[plan], quota_reset, now, now),
        )
        conn.commit()
    finally:
        conn.close()
    return get_tenant(org_id, db_path)


def get_tenant(org_id: str, db_path: Path = DEFAULT_DB_PATH) -> Optional[dict]:
    """Return tenant by org_id or None."""
    init_schema(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM tenants WHERE org_id = ?", (org_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def check_quota(org_id: str, db_path: Path = DEFAULT_DB_PATH) -> tuple[bool, int]:
    """Return (allowed, remaining). Decrements used count if allowed.

    Returns (False, 0) if tenant not found.
    """
    init_schema(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM tenants WHERE org_id = ?", (org_id,)).fetchone()
        if not row:
            return (False, 0)
        used = row["used_calls_this_month"]
        quota = row["monthly_quota"]
        if used >= quota:
            return (False, 0)
        conn.execute(
            "UPDATE tenants SET used_calls_this_month = used_calls_this_month + 1, "
            "updated_at = ? WHERE org_id = ?",
            (datetime.now(timezone.utc).isoformat(), org_id),
        )
        conn.commit()
        return (True, quota - used - 1)
    finally:
        conn.close()


def link_stripe_customer(org_id: str, stripe_customer_id: str, db_path: Path = DEFAULT_DB_PATH) -> None:
    """Attach a Stripe customer ID to an existing tenant."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            "UPDATE tenants SET stripe_customer_id = ?, updated_at = ? WHERE org_id = ?",
            (stripe_customer_id, datetime.now(timezone.utc).isoformat(), org_id),
        )
        conn.commit()
    finally:
        conn.close()
