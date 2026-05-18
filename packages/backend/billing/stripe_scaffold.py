"""Stripe Checkout integration scaffold for Apohara PROBANT SaaS.

PoC — uses Stripe test mode only. Live API integration requires Pablo's
production Stripe account + webhook signing secret + Cloudflare-equivalent
TLS for receipt URLs.

Wire: when APOHARA_STRIPE_ENABLED=1 + STRIPE_TEST_SECRET set, callers can
build Checkout Session URLs that, on success, fire a webhook that calls
billing.tenant_model.link_stripe_customer().
"""
from __future__ import annotations

import os
from typing import Optional

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

PLAN_PRICES = {
    "pro": {"price_id_test": "price_test_pro_49", "amount_usd_cents": 4900},
    "enterprise": {"price_id_test": "price_test_enterprise_499", "amount_usd_cents": 49900},
}


def _ensure_configured() -> str:
    if not STRIPE_AVAILABLE:
        raise RuntimeError("stripe library not installed. Run: pip install stripe")
    secret = os.environ.get("STRIPE_TEST_SECRET", "").strip()
    if not secret:
        raise RuntimeError("STRIPE_TEST_SECRET env var required (Stripe test-mode API key)")
    stripe.api_key = secret
    return secret


def create_checkout_session(
    org_id: str,
    plan: str,
    success_url: str,
    cancel_url: str,
) -> dict:
    """Create a Stripe Checkout session URL for plan upgrade.

    Returns {"checkout_url": str, "session_id": str}.
    PoC — call only when caller has Stripe test-mode credentials set.
    """
    _ensure_configured()
    if plan not in PLAN_PRICES:
        raise ValueError(f"plan {plan} not in PLAN_PRICES")
    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{"price": PLAN_PRICES[plan]["price_id_test"], "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        client_reference_id=org_id,
        metadata={"apohara_org_id": org_id, "plan": plan},
    )
    return {"checkout_url": session.url, "session_id": session.id}


def is_configured() -> bool:
    """True iff Stripe test mode is configured for use."""
    return STRIPE_AVAILABLE and bool(os.environ.get("STRIPE_TEST_SECRET", "").strip())
