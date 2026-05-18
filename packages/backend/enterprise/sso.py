"""OIDC SSO client for Apohara PROBANT enterprise mode.

PoC implementation using authlib. SAML 2.0 deferred to follow-up.
Wired only when APOHARA_ENTERPRISE_MODE=1 env set.

Flow:
1. GET /v1/sso/login?redirect=... -> builds OIDC authorization URL + state cookie
2. User auths at IdP (Okta, Auth0, Azure AD, custom)
3. IdP redirects back to /v1/sso/callback?code=...&state=...
4. We exchange code for token, validate id_token, mint Apohara JWT
5. Set Apohara JWT cookie + redirect to dashboard
"""
from __future__ import annotations

import os
import secrets
import time
from typing import Optional

try:
    from authlib.integrations.starlette_client import OAuth
    AUTHLIB_AVAILABLE = True
except ImportError:
    AUTHLIB_AVAILABLE = False

try:
    import jwt as pyjwt
    PYJWT_AVAILABLE = True
except ImportError:
    PYJWT_AVAILABLE = False


APOHARA_JWT_SECRET = os.environ.get("APOHARA_JWT_SECRET", "")
APOHARA_JWT_ISSUER = "https://api.apohara.dev"
APOHARA_JWT_TTL_SECONDS = 15 * 60  # 15 minutes


def is_enterprise_mode() -> bool:
    return os.environ.get("APOHARA_ENTERPRISE_MODE", "").strip().lower() in ("1", "true", "yes")


def issue_apohara_jwt(
    sub: str,
    org_id: str,
    role: str = "admin",
    secret: str = "",
    ttl_seconds: int = APOHARA_JWT_TTL_SECONDS,
) -> str:
    """Mint Apohara JWT after SSO callback.

    Claims: sub (IdP subject), org_id, role, iat, exp, iss, jti.
    Algorithm: HS256 (uses APOHARA_JWT_SECRET).
    """
    if not PYJWT_AVAILABLE:
        raise RuntimeError("pyjwt not installed. Run: pip install pyjwt")
    secret = secret or APOHARA_JWT_SECRET
    if not secret:
        raise RuntimeError("APOHARA_JWT_SECRET env var required")
    now = int(time.time())
    claims = {
        "sub": sub,
        "org_id": org_id,
        "role": role,
        "iat": now,
        "exp": now + ttl_seconds,
        "iss": APOHARA_JWT_ISSUER,
        "jti": secrets.token_hex(16),
    }
    return pyjwt.encode(claims, secret, algorithm="HS256")


def verify_apohara_jwt(
    token: str,
    secret: str = "",
    expected_iss: str = APOHARA_JWT_ISSUER,
) -> dict:
    """Verify Apohara JWT signature + claims. Returns claims dict or raises."""
    if not PYJWT_AVAILABLE:
        raise RuntimeError("pyjwt not installed. Run: pip install pyjwt")
    secret = secret or APOHARA_JWT_SECRET
    if not secret:
        raise RuntimeError("APOHARA_JWT_SECRET env var required")
    claims = pyjwt.decode(
        token,
        secret,
        algorithms=["HS256"],
        issuer=expected_iss,
        options={"require": ["sub", "exp", "iat", "iss", "org_id", "role"]},
    )
    return claims


def configure_oidc(
    *,
    issuer_url: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str = "https://api.apohara.dev/v1/sso/callback",
) -> Optional["OAuth"]:
    """Configure OIDC client. Returns authlib OAuth instance.

    PoC: caller is responsible for setting up the actual /v1/sso/login and
    /v1/sso/callback endpoints + cookie/session handling. This function
    just wires the OIDC discovery + token exchange config.
    """
    if not AUTHLIB_AVAILABLE:
        raise RuntimeError("authlib not installed. Run: pip install authlib")
    oauth = OAuth()
    oauth.register(
        name="apohara_idp",
        server_metadata_url=f"{issuer_url.rstrip('/')}/.well-known/openid-configuration",
        client_id=client_id,
        client_secret=client_secret,
        client_kwargs={"scope": "openid profile email", "acr_values": "phr"},  # MFA hint
    )
    return oauth
