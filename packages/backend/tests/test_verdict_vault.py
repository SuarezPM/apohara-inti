"""Tests for HMAC-signed verdict vault."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from verdict_vault import VerdictVault, ZERO_HASH


@pytest.fixture
def vault(tmp_path: Path) -> VerdictVault:
    return VerdictVault(
        ledger_path=tmp_path / "ledger.jsonl",
        hmac_key=b"test-key-32-bytes-ok-padpadpadpad",
    )


def test_append_returns_three_derived_fields(vault: VerdictVault) -> None:
    out = vault.append({"verdict": "verified", "ts": 1.0})
    assert set(out.keys()) == {"prev_hash", "signed_hash", "signature"}
    assert out["prev_hash"] == ZERO_HASH
    assert len(out["signed_hash"]) == 64
    assert len(out["signature"]) == 64  # HMAC-SHA256 hex


def test_chain_links_via_prev_hash(vault: VerdictVault) -> None:
    a = vault.append({"verdict": "verified", "ts": 1.0})
    b = vault.append({"verdict": "risky", "ts": 2.0})
    assert b["prev_hash"] == a["signed_hash"]


def test_verify_chain_clean(vault: VerdictVault) -> None:
    vault.append({"verdict": "verified", "ts": 1.0})
    vault.append({"verdict": "risky", "ts": 2.0})
    valid, errors = vault.verify_chain()
    assert valid, f"Expected clean chain, got errors: {errors}"
    assert errors == []


def test_verify_chain_detects_entry_tamper(vault: VerdictVault) -> None:
    vault.append({"verdict": "verified", "ts": 1.0})
    with vault.ledger_path.open() as fh:
        entry = json.loads(fh.read())
    entry["verdict"] = "blocked"  # mutate payload
    with vault.ledger_path.open("w") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")
    valid, errors = vault.verify_chain()
    assert not valid
    assert any("signed_hash mismatch" in e for e in errors)


def test_verify_chain_detects_signature_tamper(vault: VerdictVault) -> None:
    vault.append({"verdict": "verified", "ts": 1.0})
    with vault.ledger_path.open() as fh:
        entry = json.loads(fh.read())
    entry["signature"] = "f" * 64  # mutate signature only, leave payload intact
    with vault.ledger_path.open("w") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")
    valid, errors = vault.verify_chain()
    assert not valid
    assert any("signature mismatch" in e for e in errors)


def test_ephemeral_key_warning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("APOHARA_LEDGER_HMAC_KEY", raising=False)
    with pytest.warns(RuntimeWarning, match="ephemeral key"):
        v = VerdictVault(ledger_path=tmp_path / "ledger.jsonl")
    assert v.key_source == "ephemeral"


def test_env_key_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APOHARA_LEDGER_HMAC_KEY", "production-key-from-env")
    v = VerdictVault(ledger_path=tmp_path / "ledger.jsonl")
    assert v.key_source == "env"


def test_explicit_key_source(tmp_path: Path) -> None:
    v = VerdictVault(
        ledger_path=tmp_path / "ledger.jsonl",
        hmac_key=b"explicit-key",
    )
    assert v.key_source == "explicit"


def test_read_entry_by_hash(vault: VerdictVault) -> None:
    out = vault.append({"verdict": "verified", "ts": 1.0})
    entry = vault.read_entry(out["signed_hash"])
    assert entry is not None
    assert entry["verdict"] == "verified"
    assert entry["signature"] == out["signature"]


def test_read_entry_missing_returns_none(vault: VerdictVault) -> None:
    vault.append({"verdict": "verified", "ts": 1.0})
    assert vault.read_entry("a" * 64) is None


def test_read_last_hash_empty(vault: VerdictVault) -> None:
    assert vault.read_last_hash() == ZERO_HASH


def test_read_last_hash_after_appends(vault: VerdictVault) -> None:
    a = vault.append({"verdict": "v1"})
    b = vault.append({"verdict": "v2"})
    assert vault.read_last_hash() == b["signed_hash"]
    assert a["signed_hash"] != b["signed_hash"]
