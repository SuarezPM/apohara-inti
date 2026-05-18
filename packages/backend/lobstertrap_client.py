"""LobsterTrap async DPI pre-check for /v1/verify. Fail-open on unreachable:
the 9-vendor adversarial ensemble is the primary safety layer."""
from __future__ import annotations

import asyncio
import json
import os
import time
from typing import Optional

import httpx

LOBSTERTRAP_PATH = "/dpi/inspect"
LOBSTERTRAP_TIMEOUT = 5.0
DENY_MARKER = "lobstertrap-deny"

LOBSTERTRAP_BIN_PATH = os.environ.get("LOBSTERTRAP_BIN", "/opt/lobstertrap/lobstertrap")
LOBSTERTRAP_POLICY_PATH = os.environ.get(
    "LOBSTERTRAP_POLICY", "/opt/apohara-inti/lobstertrap-policy.yaml"
)


def _make_client() -> httpx.AsyncClient:
    """Factory the tests monkeypatch to inject a MockTransport."""
    return httpx.AsyncClient(timeout=LOBSTERTRAP_TIMEOUT)


def _safe_json(resp: httpx.Response) -> dict:
    try:
        body = resp.json()
        return body if isinstance(body, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def _extract_reason(resp: httpx.Response, default: str) -> str:
    body = _safe_json(resp)
    for key in ("reason", "detail", "message"):
        v = body.get(key)
        if isinstance(v, str):
            return v[:240]
    return default


def _parse_subprocess_verdict(combined: str) -> tuple[str, str]:
    """Return (verdict, reason) from ``lobstertrap inspect`` combined stdout+stderr.

    LT v0.1.0 prints DPI metadata JSON to stdout AND the Policy Decision
    block ("Action:  DENY/ALLOW/LOG", "Rule: ...", "Message: ...") to
    stderr. Callers MUST pass the concatenated stream. We scan line-by-line
    for the "Action:" prefix which is the canonical verdict source.
    """
    verdict = "ALLOW"
    reason = ""
    rule = ""
    message = ""
    for line in combined.splitlines():
        stripped_upper = line.strip().upper()
        if stripped_upper.startswith("ACTION:"):
            rhs = stripped_upper.split(":", 1)[1].strip()
            if rhs.startswith("DENY") or rhs.startswith("BLOCK"):
                verdict = "DENY"
            elif rhs.startswith("LOG"):
                verdict = "LOG"
            elif rhs.startswith("ALLOW"):
                verdict = "ALLOW"
        elif stripped_upper.startswith("RULE:"):
            rule = line.split(":", 1)[1].strip()
        elif stripped_upper.startswith("MESSAGE:"):
            message = line.split(":", 1)[1].strip()
    if verdict in ("DENY", "BLOCK", "LOG"):
        reason = (message or rule or f"verdict={verdict}")[:240]
    else:
        reason = "ok"
    return verdict, reason


async def _check_via_subprocess(text: str, bin_path: str, policy_path: str) -> dict:
    """Invoke lobstertrap inspect via asyncio subprocess."""
    started = time.perf_counter()
    try:
        proc = await asyncio.create_subprocess_exec(
            bin_path, "inspect", text, "--policy", policy_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=5.0
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            return {
                "allowed": True,
                "reason": "lobstertrap subprocess timeout",
                "latency_ms": (time.perf_counter() - started) * 1000.0,
                "source": "lobstertrap-subprocess-failed",
            }
        stdout = stdout_bytes.decode(errors="replace")
        stderr = stderr_bytes.decode(errors="replace")
        # LT v0.1.0 writes metadata JSON to stdout AND the "Policy Decision"
        # section (Action: DENY/ALLOW/LOG) to stderr. Combine for parsing.
        combined = stdout + "\n" + stderr
        latency_ms = (time.perf_counter() - started) * 1000.0
        verdict, reason = _parse_subprocess_verdict(combined)
        if verdict in ("DENY", "BLOCK"):
            return {
                "allowed": False,
                "reason": reason,
                "latency_ms": latency_ms,
                "source": "lobstertrap-subprocess",
                "raw_stdout": stdout[:500],
            }
        return {
            "allowed": True,
            "reason": "ok",
            "latency_ms": latency_ms,
            "source": "lobstertrap-subprocess",
            "raw_stdout": stdout[:500],
        }
    except FileNotFoundError:
        return {
            "allowed": True,
            "reason": f"lobstertrap subprocess unavailable: binary not found at {bin_path}",
            "latency_ms": (time.perf_counter() - started) * 1000.0,
            "source": "lobstertrap-subprocess-failed",
        }
    except OSError as exc:
        return {
            "allowed": True,
            "reason": f"lobstertrap subprocess unavailable: {exc}",
            "latency_ms": (time.perf_counter() - started) * 1000.0,
            "source": "lobstertrap-subprocess-failed",
        }


async def check_prompt_with_lobstertrap(
    prompt: str,
    lt_url: Optional[str],
) -> dict:
    """Forward ``prompt`` to LobsterTrap for DPI inspection.

    Returns a dict ``{allowed, reason, latency_ms, source}``.

    Code path selection:
    - LOBSTERTRAP_BIN env set → subprocess mode (lobstertrap inspect CLI)
    - LOBSTERTRAP_URL / lt_url set, no BIN → HTTP mode (legacy)
    - Neither set → disabled, fail-open
    """
    bin_path = os.environ.get("LOBSTERTRAP_BIN", "")
    if bin_path:
        return await _check_via_subprocess(
            prompt, bin_path, os.environ.get("LOBSTERTRAP_POLICY", LOBSTERTRAP_POLICY_PATH)
        )

    if not lt_url:
        return {
            "allowed": True,
            "reason": "LOBSTERTRAP_URL not set",
            "latency_ms": 0.0,
            "source": "disabled",
        }

    url = lt_url.rstrip("/") + LOBSTERTRAP_PATH
    started = time.perf_counter()
    try:
        async with _make_client() as client:
            resp = await client.post(
                url,
                json={"content": prompt, "direction": "inbound"},
            )
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError) as exc:
        return {
            "allowed": True,
            "reason": f"lobstertrap unreachable: {type(exc).__name__}",
            "latency_ms": (time.perf_counter() - started) * 1000.0,
            "source": "unreachable-fallback",
        }

    latency_ms = (time.perf_counter() - started) * 1000.0

    if resp.status_code == 403:
        return {
            "allowed": False,
            "reason": _extract_reason(resp, default="403 deny"),
            "latency_ms": latency_ms,
            "source": "lobstertrap",
        }

    if 200 <= resp.status_code < 300:
        body = _safe_json(resp)
        if body.get("id") == DENY_MARKER or body.get("verdict") == "deny":
            return {
                "allowed": False,
                "reason": _extract_reason(resp, default="deny marker in body"),
                "latency_ms": latency_ms,
                "source": "lobstertrap",
            }
        return {
            "allowed": True,
            "reason": "ok",
            "latency_ms": latency_ms,
            "source": "lobstertrap",
        }

    return {
        "allowed": True,
        "reason": f"unexpected status {resp.status_code}",
        "latency_ms": latency_ms,
        "source": "unreachable-fallback",
    }


async def check_response_with_lobstertrap(
    text: str,
    lt_bin: Optional[str],
) -> dict:
    """Forward model output ``text`` to LobsterTrap for egress DPI inspection.

    Symmetric to ``check_prompt_with_lobstertrap`` but operates on model
    output rather than user input. LobsterTrap's ``inspect`` command runs
    the full policy including egress_rules — egress rules fire on
    ``contains_credentials``, ``contains_exfiltration``, and
    ``contains_sensitive_paths`` fields that LT detects in the text.

    Returns a dict ``{allowed, reason, latency_ms, source}``.

    Code path selection:
    - LOBSTERTRAP_BIN env OR ``lt_bin`` argument set → subprocess mode
    - Neither set → disabled, fail-open (LOBSTERTRAP_CHECK_EGRESS guard
      is handled by the caller; this function is always fail-open when
      the binary is unavailable).
    """
    bin_path = lt_bin or os.environ.get("LOBSTERTRAP_BIN", "")
    if not bin_path:
        return {
            "allowed": True,
            "reason": "LOBSTERTRAP_BIN not set",
            "latency_ms": 0.0,
            "source": "disabled",
        }

    policy_path = os.environ.get("LOBSTERTRAP_POLICY", LOBSTERTRAP_POLICY_PATH)
    result = await _check_via_subprocess(text, bin_path, policy_path)
    # Tag the source so callers can distinguish ingress vs egress checks.
    result["direction"] = "egress"
    return result
