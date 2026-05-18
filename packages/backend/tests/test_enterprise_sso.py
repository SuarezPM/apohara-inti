"""Tests for enterprise/sso.py — JWT mint/verify roundtrip + edge cases."""
from __future__ import annotations

import time

import pytest

# Import under test — pyjwt is installed in this env.
from enterprise.sso import (
    PYJWT_AVAILABLE,
    AUTHLIB_AVAILABLE,
    issue_apohara_jwt,
    verify_apohara_jwt,
    configure_oidc,
    is_enterprise_mode,
)

_SECRET = "test-secret-32-bytes-xxxxxxxxxxx"


def test_jwt_mint_and_verify_roundtrip():
    """Mint a JWT then verify it; claims must round-trip."""
    token = issue_apohara_jwt(
        sub="user@example.com",
        org_id="org-123",
        role="admin",
        secret=_SECRET,
    )
    assert isinstance(token, str)
    claims = verify_apohara_jwt(token, secret=_SECRET)
    assert claims["sub"] == "user@example.com"
    assert claims["org_id"] == "org-123"
    assert claims["role"] == "admin"
    assert claims["iss"] == "https://api.apohara.dev"
    assert "jti" in claims


def test_expired_token_rejected():
    """JWT with ttl_seconds=0 must be rejected by verify (exp in the past)."""
    # Mint with ttl=0 → exp == iat → expired immediately
    token = issue_apohara_jwt(
        sub="u",
        org_id="org-x",
        secret=_SECRET,
        ttl_seconds=-1,  # already expired
    )
    import jwt as pyjwt
    with pytest.raises(pyjwt.ExpiredSignatureError):
        verify_apohara_jwt(token, secret=_SECRET)


def test_missing_secret_raises():
    """issue_apohara_jwt and verify_apohara_jwt must raise when secret is empty."""
    import os
    os.environ.pop("APOHARA_JWT_SECRET", None)
    with pytest.raises(RuntimeError, match="APOHARA_JWT_SECRET"):
        issue_apohara_jwt(sub="u", org_id="o", secret="")
    # Mint a valid token first with a known secret, then verify without secret.
    token = issue_apohara_jwt(sub="u", org_id="o", secret=_SECRET)
    with pytest.raises(RuntimeError, match="APOHARA_JWT_SECRET"):
        verify_apohara_jwt(token, secret="")


def test_configure_oidc_degrades_gracefully_without_authlib():
    """configure_oidc raises RuntimeError when authlib is absent; no crash on import."""
    if AUTHLIB_AVAILABLE:
        # authlib IS installed — call succeeds; just verify it returns an OAuth obj.
        result = configure_oidc(
            issuer_url="https://accounts.example.com",
            client_id="client-id",
            client_secret="client-secret",
        )
        assert result is not None
    else:
        # authlib not installed — must raise RuntimeError with install hint.
        with pytest.raises(RuntimeError, match="authlib"):
            configure_oidc(
                issuer_url="https://accounts.example.com",
                client_id="client-id",
                client_secret="client-secret",
            )
