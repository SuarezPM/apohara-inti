"""US-002 RFC 3161 TSA integration tests (Step 5a minimum-to-ship).

Two more tests (test_tsa_token_tamper, test_tsa_token_fallback)
are deferred to Step 5b — see plan kill-gate logic.
"""
import json
import pytest
from pathlib import Path
from verdict_vault import VerdictVault, ZERO_HASH


def test_tsa_optional_field_backward_compat(tmp_path: Path):
    """Pre-TSA verdicts (no tsa_token field) must verify as valid."""
    ledger = tmp_path / "ledger.jsonl"
    vault = VerdictVault(ledger, hmac_key=b"x" * 32)

    # Append entry WITHOUT requesting TSA (default behavior)
    result = vault.append({"verdict": "verified", "actor": "test"})

    # Entry must have no tsa_token field
    with ledger.open() as fh:
        line = fh.readline()
        entry = json.loads(line)
    assert "tsa_token" not in entry, "default append should not include tsa_token"
    assert "tsa_status" not in entry

    # verify_chain still works
    is_valid, errors = vault.verify_chain()
    assert is_valid is True, f"backward-compat verify_chain failed: {errors}"
    assert errors == []


@pytest.mark.network
def test_tsa_token_roundtrip_freetsa(tmp_path: Path):
    """Live Freetsa.org call: TSA token attached + verify_tsa_token parses it.

    Marked @pytest.mark.network because it requires internet.
    Skip in offline environments.
    """
    ledger = tmp_path / "ledger.jsonl"
    vault = VerdictVault(ledger, hmac_key=b"y" * 32)

    result = vault.append({"verdict": "blocked", "actor": "jailbreak_test"}, request_tsa=True)

    # Either we got a real token, or TSA was unreachable (CI-tolerant)
    if result.get("tsa_status") == "unavailable":
        pytest.skip("TSA endpoint unreachable; test cannot validate roundtrip")

    assert "tsa_token" in result, "expected tsa_token in result when request_tsa=True"
    assert result.get("tsa_authority") in {"freetsa", "digicert"}
    assert "tsa_timestamp" in result

    # Read the entry back and verify the token parses
    with ledger.open() as fh:
        entry = json.loads(fh.readline())

    verify_result = vault.verify_tsa_token(entry)
    assert verify_result["valid"] is True, f"token verify failed: {verify_result.get('error')}"
    assert verify_result["authority"] in {"freetsa", "digicert"}

    # CRITICAL: chain still verifies even with TSA fields present
    is_valid, errors = vault.verify_chain()
    assert is_valid is True, f"chain broken by TSA fields: {errors}"
