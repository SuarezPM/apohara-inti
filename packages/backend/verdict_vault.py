"""HMAC-signed SHA-256 chain-of-custody for the Apohara Inti verdict ledger.

Port of Apohara Guard's EvidenceVault (``src/evidence/{vault,chain,crypto}.ts``)
to Python. Every appended entry carries an HMAC-SHA256 signature alongside
the SHA-256 hash chain from the original ledger design.

Tamper-evidence property: mutating any persisted entry breaks
:meth:`VerdictVault.verify_chain`. Mutating the signature alone also breaks
verification. The chain root + signatures are the publishable artifact for
forensic auditors and the lablab.ai judges.

Apohara Inti uses this so investors, judges, and end users can independently
re-derive that a returned verdict matches what was originally emitted by the
9-vendor ensemble — no trust-us layer.

US-002: RFC 3161 TSA integration (Milan AI Week / CONSILIUM plan).
TSA tokens are OPTIONAL and additive — the HMAC chain is unaffected.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import urllib.request
import warnings
from pathlib import Path
from typing import Any, Optional

ZERO_HASH = "0" * 64


class VerdictVault:
    """Append-only HMAC-signed verdict ledger with SHA-256 hash chain.

    Construct once per process; subsequent ``append`` calls re-read the
    last hash from disk to avoid stale-write races.
    """

    def __init__(
        self,
        ledger_path: Path,
        hmac_key: Optional[bytes] = None,
    ) -> None:
        self.ledger_path = ledger_path
        if hmac_key is not None:
            self._hmac_key = hmac_key
            self._key_source = "explicit"
        else:
            env_key = (os.environ.get("APOHARA_LEDGER_HMAC_KEY") or "").strip()
            if env_key:
                self._hmac_key = env_key.encode("utf-8")
                self._key_source = "env"
            else:
                # Ephemeral key — log warning, do NOT crash. Operators MUST
                # set APOHARA_LEDGER_HMAC_KEY in prod (documented in README).
                self._hmac_key = secrets.token_bytes(32)
                self._key_source = "ephemeral"
                warnings.warn(
                    "APOHARA_LEDGER_HMAC_KEY not set; using ephemeral key. "
                    "Ledger signatures will not survive restarts. "
                    "Set APOHARA_LEDGER_HMAC_KEY for production.",
                    RuntimeWarning,
                    stacklevel=2,
                )

    @property
    def key_source(self) -> str:
        """One of ``'explicit'``, ``'env'``, ``'ephemeral'``. For /health probes."""
        return self._key_source

    def _canonical(self, payload: dict[str, Any]) -> str:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    def _sign(self, message: str) -> str:
        return hmac.new(
            self._hmac_key, message.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def read_last_hash(self) -> str:
        """Return the ``signed_hash`` of the last ledger entry, or :data:`ZERO_HASH`."""
        if not self.ledger_path.exists():
            return ZERO_HASH
        last = ZERO_HASH
        try:
            with self.ledger_path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    h = entry.get("signed_hash")
                    if isinstance(h, str) and len(h) == 64:
                        last = h
        except OSError:
            return ZERO_HASH
        return last

    # -----------------------------------------------------------------------
    # US-002: RFC 3161 TSA integration
    # -----------------------------------------------------------------------

    _TSA_URLS: dict[str, str] = {
        "freetsa": "https://freetsa.org/tsr",
        "digicert": "http://timestamp.digicert.com",
    }

    def _request_tsa_token(
        self, message_bytes: bytes, authority: str = "freetsa"
    ) -> Optional[tuple[bytes, str]]:
        """Request an RFC 3161 timestamp token from a TSA.

        Args:
            message_bytes: The bytes to timestamp (typically the signed_hash bytes).
            authority: One of "freetsa" or "digicert".

        Returns:
            ``(token_der_bytes, iso_timestamp)`` on success; ``None`` on any failure.
            Never raises — callers decide what to do on None.
        """
        url = self._TSA_URLS.get(authority)
        if url is None:
            return None
        try:
            from rfc3161_client import TimestampRequestBuilder, decode_timestamp_response  # noqa: PLC0415

            builder = TimestampRequestBuilder()
            request = builder.data(message_bytes).cert_request(True).build()
            request_der = request.as_bytes()

            req = urllib.request.Request(
                url,
                data=request_der,
                headers={"Content-Type": "application/timestamp-query"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status != 200:
                    return None
                response_der = resp.read()

            ts_response = decode_timestamp_response(response_der)
            if ts_response.status != 0:
                return None

            # tst_info and gen_time are properties (not methods) on Rust-backed types.
            tst_info = ts_response.tst_info
            gen_time = tst_info.gen_time
            iso_ts = gen_time.isoformat() if hasattr(gen_time, "isoformat") else str(gen_time)
            # Store the full response DER (as_bytes) so verify_tsa_token can decode it.
            return (ts_response.as_bytes(), iso_ts)
        except Exception:  # noqa: BLE001
            return None

    def verify_tsa_token(self, entry: dict[str, Any]) -> dict[str, Any]:
        """Parse and validate the RFC 3161 TSA token stored in a ledger entry.

        Step 5a: verifies the token *exists and parses* cleanly.
        TODO (US-002 Step 5b): also verify the token's message imprint
        matches the entry's signed_hash bytes — a higher-assurance check
        that the timestamp was issued for this specific verdict.

        Args:
            entry: A deserialized ledger entry dict.

        Returns:
            ``{"valid": bool, "authority": Optional[str], "timestamp": Optional[str],
            "error": Optional[str]}``
        """
        if "tsa_token" not in entry or entry.get("tsa_status") == "unavailable":
            return {
                "valid": False,
                "authority": None,
                "timestamp": None,
                "error": "no_tsa_token",
            }
        try:
            from rfc3161_client import decode_timestamp_response  # noqa: PLC0415

            token_bytes = base64.b64decode(entry["tsa_token"])
            ts_response = decode_timestamp_response(token_bytes)
            # tst_info and gen_time are properties on the Rust-backed types.
            tst_info = ts_response.tst_info
            gen_time = tst_info.gen_time
            iso_ts = gen_time.isoformat() if hasattr(gen_time, "isoformat") else str(gen_time)
            return {
                "valid": True,
                "authority": entry.get("tsa_authority"),
                "timestamp": iso_ts,
                "error": None,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "valid": False,
                "authority": entry.get("tsa_authority"),
                "timestamp": None,
                "error": str(exc)[:200],
            }

    def append(
        self,
        entry: dict[str, Any],
        tenant_id: Optional[str] = None,
        request_tsa: bool = False,
    ) -> dict[str, Any]:
        """Append entry with ``prev_hash`` + ``signed_hash`` + ``signature``.

        Optional *tenant_id* is included in the canonical payload so that
        multi-tenant audit queries can filter by org_id.  Backward compat:
        when *tenant_id* is ``None``, no field is added and the ledger format
        is identical to the pre-enterprise single-tenant format.

        US-002: When *request_tsa* is ``True``, attempts to obtain an RFC 3161
        timestamp token (freetsa first, digicert fallback).  TSA fields are
        appended **after** ``signed_hash`` + ``signature`` are computed so they
        do **not** affect the canonical hash.  On both TSA failures, writes
        ``tsa_status="unavailable"`` and the HMAC chain is unaffected.

        Returns the derived fields so callers can echo them.
        """
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        prev_hash = self.read_last_hash()
        payload = dict(entry)
        payload["prev_hash"] = prev_hash
        if tenant_id is not None:
            payload["tenant_id"] = tenant_id
        canonical = self._canonical(payload)
        signed_hash = hashlib.sha256(
            (prev_hash + canonical).encode("utf-8")
        ).hexdigest()
        payload["signed_hash"] = signed_hash
        signature = self._sign(canonical + signed_hash)
        payload["signature"] = signature

        result: dict[str, Any] = {
            "prev_hash": prev_hash,
            "signed_hash": signed_hash,
            "signature": signature,
        }

        # TSA fields are added AFTER the canonical hash — they do not affect it.
        if request_tsa:
            message_bytes = signed_hash.encode("utf-8")
            tsa_result = None
            tsa_authority_used: Optional[str] = None
            for authority in ("freetsa", "digicert"):
                tsa_result = self._request_tsa_token(message_bytes, authority)
                if tsa_result is not None:
                    tsa_authority_used = authority
                    break
            if tsa_result is not None:
                token_der, iso_ts = tsa_result
                tsa_token_b64 = base64.b64encode(token_der).decode("ascii")
                payload["tsa_token"] = tsa_token_b64
                payload["tsa_authority"] = tsa_authority_used
                payload["tsa_timestamp"] = iso_ts
                result["tsa_token"] = tsa_token_b64
                result["tsa_authority"] = tsa_authority_used
                result["tsa_timestamp"] = iso_ts
            else:
                payload["tsa_status"] = "unavailable"
                result["tsa_status"] = "unavailable"

        with self.ledger_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, sort_keys=True) + "\n")
        return result

    def read_entry(self, signed_hash: str) -> Optional[dict[str, Any]]:
        """Find the ledger entry with the given ``signed_hash``; ``None`` if absent."""
        if not self.ledger_path.exists():
            return None
        try:
            with self.ledger_path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if entry.get("signed_hash") == signed_hash:
                        return entry
        except OSError:
            return None
        return None

    def verify_chain(self) -> tuple[bool, list[str]]:
        """Walk the ledger, re-derive each ``signed_hash`` + ``signature``.

        Returns ``(is_valid, errors)``. ``errors`` is empty on success.
        Detects: malformed JSON, missing fields, ``prev_hash`` mismatch,
        ``signed_hash`` mismatch (payload tampered), ``signature`` mismatch
        (HMAC tampered or key rotated).
        """
        errors: list[str] = []
        if not self.ledger_path.exists():
            return True, errors
        prev_hash = ZERO_HASH
        try:
            with self.ledger_path.open("r", encoding="utf-8") as fh:
                for line_no, line in enumerate(fh, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError as exc:
                        errors.append(f"line {line_no}: malformed JSON: {exc}")
                        continue
                    claimed_hash = entry.get("signed_hash")
                    claimed_sig = entry.get("signature")
                    if not isinstance(claimed_hash, str) or not isinstance(
                        claimed_sig, str
                    ):
                        errors.append(
                            f"line {line_no}: missing signed_hash or signature"
                        )
                        continue
                    if entry.get("prev_hash") != prev_hash:
                        errors.append(
                            f"line {line_no}: prev_hash mismatch "
                            f"(expected {prev_hash}, got {entry.get('prev_hash')})"
                        )
                    # Re-derive signed_hash from canonical payload (strip derived fields).
                    # US-002: also strip TSA fields — they are appended after the
                    # canonical hash is computed and must not affect re-derivation.
                    redo = dict(entry)
                    redo.pop("signed_hash", None)
                    redo.pop("signature", None)
                    redo.pop("tsa_token", None)
                    redo.pop("tsa_authority", None)
                    redo.pop("tsa_timestamp", None)
                    redo.pop("tsa_status", None)
                    canonical = self._canonical(redo)
                    expected_hash = hashlib.sha256(
                        (prev_hash + canonical).encode("utf-8")
                    ).hexdigest()
                    if expected_hash != claimed_hash:
                        errors.append(
                            f"line {line_no}: signed_hash mismatch "
                            f"(payload tampered; expected {expected_hash}, "
                            f"got {claimed_hash})"
                        )
                    expected_sig = self._sign(canonical + claimed_hash)
                    if not hmac.compare_digest(expected_sig, claimed_sig):
                        errors.append(
                            f"line {line_no}: signature mismatch "
                            f"(HMAC tampered or key rotated)"
                        )
                    prev_hash = claimed_hash
        except OSError as exc:
            errors.append(f"read failed: {exc}")
            return False, errors
        return len(errors) == 0, errors
