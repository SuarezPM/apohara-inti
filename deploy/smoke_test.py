#!/usr/bin/env python3
"""End-to-end smoke test for the Apohara Inti deployed stack.

Probes the four user-facing endpoints (frontend root, backend /health,
/v1/verify with a tiny test payload, and /v1/audit/<id> for the
verdict produced by the verify call), records latency and HTTP status
for each, and writes a timestamped JSON report to logs/.

Usage::

    # Default URLs.
    python3 deploy/smoke_test.py

    # Override.
    FRONTEND_URL=https://example.vercel.app \\
      BACKEND_URL=https://example.nip.io \\
      INTI_TEST_GEMINI_KEY=<key> \\
      python3 deploy/smoke_test.py

The Gemini key is only consumed by the /v1/verify probe. Without it
the probe records the 401/422 it gets back (still a useful liveness
signal — proves the backend is routed and CORS isn't blocking).

Output: logs/deploy_smoke_<unix_ts>.json. The script ALWAYS writes the
file (even on partial failure) so we can commit it as evidence.
Returns exit 0 if /health probe passes; non-zero otherwise.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request


def _probe(
    url: str,
    *,
    method: str = "GET",
    body: bytes | None = None,
    timeout: float = 30.0,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Hit ``url`` and return {status, latency_ms, body, error}."""
    req = urllib_request.Request(url, method=method, data=body)
    req.add_header("User-Agent", "apohara-inti-smoke-test/0.1")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    if body is not None and "Content-Type" not in (headers or {}):
        req.add_header("Content-Type", "application/json")

    t0 = time.perf_counter()
    try:
        with urllib_request.urlopen(req, timeout=timeout) as resp:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            raw = resp.read()
            ctype = resp.headers.get("Content-Type", "")
            parsed: Any = None
            if "json" in ctype:
                try:
                    parsed = json.loads(raw.decode("utf-8"))
                except json.JSONDecodeError:
                    parsed = raw.decode("utf-8", errors="replace")[:500]
            else:
                parsed = raw.decode("utf-8", errors="replace")[:500]
            return {
                "status": resp.status,
                "latency_ms": round(latency_ms, 2),
                "body": parsed,
                "error": None,
            }
    except urllib_error.HTTPError as exc:
        latency_ms = (time.perf_counter() - t0) * 1000.0
        try:
            raw = exc.read().decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            raw = ""
        return {
            "status": exc.code,
            "latency_ms": round(latency_ms, 2),
            "body": raw[:500],
            "error": f"HTTPError {exc.code}: {exc.reason}",
        }
    except (urllib_error.URLError, TimeoutError, OSError) as exc:
        latency_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "status": 0,
            "latency_ms": round(latency_ms, 2),
            "body": None,
            "error": f"{type(exc).__name__}: {exc!s}",
        }


def main() -> int:
    frontend_url = os.environ.get(
        "FRONTEND_URL", "https://apohara-inti.vercel.app"
    ).rstrip("/")
    backend_url = os.environ.get(
        "BACKEND_URL", "https://149.28.56.91.nip.io"
    ).rstrip("/")
    gemini_key = os.environ.get("INTI_TEST_GEMINI_KEY", "").strip()

    print(f"Frontend URL: {frontend_url}", file=sys.stderr)
    print(f"Backend URL : {backend_url}", file=sys.stderr)
    print(
        f"Gemini key  : {'<set, '+str(len(gemini_key))+' chars>' if gemini_key else '<unset — /v1/verify probe will record 401/422>'}",
        file=sys.stderr,
    )

    probes: dict[str, dict[str, Any]] = {}

    # --- 1. Frontend root --------------------------------------------------
    probes["frontend_root"] = _probe(f"{frontend_url}/", timeout=15.0)

    # --- 2. Backend /health -----------------------------------------------
    probes["backend_health"] = _probe(f"{backend_url}/health", timeout=15.0)

    # --- 3. /v1/verify with a tiny test payload ---------------------------
    # We use a deliberately-trivial code snippet so the 9 attackers
    # don't burn meaningful budget. If no Gemini key is set, the
    # backend will return 401 — still a useful "reached the route"
    # signal.
    verify_payload = json.dumps({
        "gemini_api_key": gemini_key or "INVALID_TEST_KEY_FOR_SMOKE",
        "task_input": "def add(a, b):\n    return a + b\n",
    }).encode("utf-8")
    probes["v1_verify"] = _probe(
        f"{backend_url}/v1/verify",
        method="POST",
        body=verify_payload,
        timeout=120.0,  # 9-attacker ensemble can take 30-60s
    )

    # --- 4. /v1/audit/<id> ------------------------------------------------
    # Try to pull the signed_hash from the verify response; if that
    # failed, probe with a known-missing id (expect 404 — still proves
    # the route exists and responds).
    audit_id: str
    verify_body = probes["v1_verify"]["body"]
    if isinstance(verify_body, dict) and isinstance(
        verify_body.get("signed_hash"), str
    ):
        audit_id = verify_body["signed_hash"]
        expect_status_set = (200,)
    else:
        audit_id = "smoketest-known-missing-id-" + str(int(time.time()))
        expect_status_set = (404,)
    probes["v1_audit"] = _probe(
        f"{backend_url}/v1/audit/{audit_id}", timeout=15.0
    )

    # --- Aggregate report --------------------------------------------------
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "frontend_url": frontend_url,
        "backend_url": backend_url,
        "probes": probes,
        "verdict": (
            "all_green"
            if probes["backend_health"]["status"] == 200
            and probes["v1_verify"]["status"] in (200, 401, 422)
            and probes["v1_audit"]["status"] in expect_status_set
            else "degraded"
        ),
    }

    # Always write the file (commit-worthy evidence even on failure).
    here = Path(__file__).resolve().parent.parent
    logs_dir = here / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    out = logs_dir / f"deploy_smoke_{ts}.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}", file=sys.stderr)

    # Print summary for the operator.
    print("\nSummary:", file=sys.stderr)
    for name, p in probes.items():
        marker = "OK" if p["status"] in (200, 201, 401, 404, 422) else "FAIL"
        print(
            f"  [{marker}] {name:18s} status={p['status']:3d} "
            f"latency={p['latency_ms']:7.1f}ms"
            + (f" err={p['error']}" if p["error"] else ""),
            file=sys.stderr,
        )
    print(f"\nVerdict: {report['verdict']}", file=sys.stderr)

    # Exit 0 if /health was reachable, else 1.
    return 0 if probes["backend_health"]["status"] == 200 else 1


if __name__ == "__main__":
    sys.exit(main())
