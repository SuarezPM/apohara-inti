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
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
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

    def append(self, entry: dict[str, Any]) -> dict[str, str]:
        """Append entry with ``prev_hash`` + ``signed_hash`` + ``signature``.

        Returns the three derived fields so callers can echo them.
        """
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        prev_hash = self.read_last_hash()
        payload = dict(entry)
        payload["prev_hash"] = prev_hash
        canonical = self._canonical(payload)
        signed_hash = hashlib.sha256(
            (prev_hash + canonical).encode("utf-8")
        ).hexdigest()
        payload["signed_hash"] = signed_hash
        signature = self._sign(canonical + signed_hash)
        payload["signature"] = signature
        with self.ledger_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, sort_keys=True) + "\n")
        return {
            "prev_hash": prev_hash,
            "signed_hash": signed_hash,
            "signature": signature,
        }

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
                    redo = dict(entry)
                    redo.pop("signed_hash", None)
                    redo.pop("signature", None)
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
