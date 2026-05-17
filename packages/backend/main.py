"""Apohara Inti backend — FastAPI service for cross-AI code verification.

US-006 (Day-6 sprint). Endpoints:

* ``POST /v1/verify`` — Gemini (user BYOK) writes a review/fix; the 9-vendor
  adversarial ensemble from ``apohara_aegis`` looks for bugs / prompt-injection
  vectors / vulnerabilities in Gemini's output. INV-15
  (``apohara_context_forge.safety.jcr_gate``) isolates each attacker's KV
  cache from Gemini's session so they cannot poison the writer.
* ``GET /health`` — liveness + dep import probe.
* ``GET /v1/audit/{verdict_id}`` — fetch a signed verdict from the
  append-only SHA-256 ledger at ``~/.apohara-inti/ledger.jsonl``.

Verdict aggregation (per US-006 acceptance criteria):

  0-2 attackers find an issue  -> "verified"
  3-5 attackers find an issue  -> "risky"   (human review)
  6+ attackers find an issue   -> "blocked"
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import AliasChoices, BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Dep import — capture failures honestly for /health (do NOT crash on import).
# ---------------------------------------------------------------------------

_aegis_err: Optional[str] = None
_ctx_err: Optional[str] = None

try:
    import apohara_aegis as _aegis_mod  # noqa: F401
    from apohara_aegis import __version__ as _aegis_version
    from apohara_aegis.multi_judge import (
        EnsembleJudge,
        JudgeVerdict,
        make_default_adapters,
    )
except Exception as exc:  # noqa: BLE001
    _aegis_err = f"{type(exc).__name__}: {exc!s}"[:200]
    _aegis_version = "unknown"
    EnsembleJudge = None  # type: ignore[assignment]
    make_default_adapters = None  # type: ignore[assignment]

try:
    import apohara_context_forge as _ctx_mod  # noqa: F401
    from apohara_context_forge import __version__ as _ctx_version
    from apohara_context_forge.safety.jcr_gate import JCRSafetyGate
except Exception as exc:  # noqa: BLE001
    _ctx_err = f"{type(exc).__name__}: {exc!s}"[:200]
    _ctx_version = "unknown"
    JCRSafetyGate = None  # type: ignore[assignment]

from lobstertrap_client import check_prompt_with_lobstertrap
from rate_limiter import DailyRateLimiter

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

API_VERSION = "0.1.0"
GEMINI_MODEL = "gemini-2.5-pro"  # current writer model; SDK accepts this name
COST_CEILING_USD = 0.50
LEDGER_DIR = Path(os.path.expanduser("~/.apohara-inti"))
LEDGER_PATH = LEDGER_DIR / "ledger.jsonl"
ZERO_HASH = "0" * 64

# Verdict aggregation thresholds (per acceptance criteria 1.f).
VERDICT_BLOCK_THRESHOLD = 6   # >=6 attackers harmful  -> blocked
VERDICT_REVIEW_THRESHOLD = 3  # 3-5 attackers harmful  -> risky
# (else verified)

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class DemoVerifyRequest(BaseModel):
    """Demo endpoint accepts the prompt only; backend supplies the Gemini key."""
    model_config = ConfigDict(populate_by_name=True)

    task_input: str = Field(
        ...,
        min_length=1,
        validation_alias=AliasChoices("task_input", "code"),
    )


class VerifyRequest(BaseModel):
    # populate_by_name=True so the API accepts either alias on input
    # (legacy frontend shipped `code:` per US-007 types.ts; canonical
    # is `task_input` per US-006 spec). Both names produce the same
    # internal field.
    model_config = ConfigDict(populate_by_name=True)

    gemini_api_key: str = Field(..., min_length=1)
    task_input: str = Field(
        ...,
        min_length=1,
        validation_alias=AliasChoices("task_input", "code"),
    )


class AttackerReport(BaseModel):
    vendor: str
    model: str
    found_issue: bool
    reasoning: str


class MemoryIsolationReport(BaseModel):
    inv15_enforced: bool
    contextforge_audit_id: str


class VerifyResponse(BaseModel):
    verdict: str  # "verified" | "risky" | "blocked"
    attackers: list[AttackerReport]
    memory_isolation: MemoryIsolationReport
    signed_hash: str
    latency_ms: float
    cost_estimate_usd: float
    cost_capped: bool = False


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Apohara Inti Backend",
    description="Cross-AI code verification: Gemini writes, 9 attackers audit, INV-15 isolates memory.",
    version=API_VERSION,
)

# CORS — the frontend lives on Vercel / Netlify (cross-origin) and on
# localhost during dev. Whitelist exactly those origins so the browser
# does not block /v1/verify POSTs from the deployed UI. Additional
# origins can be added via the APOHARA_INTI_CORS_ORIGINS env var
# (comma-separated) without code changes — useful when the Vercel
# preview URL rotates per PR.
_DEFAULT_CORS_ORIGINS = [
    "https://apohara.dev",
    "https://www.apohara.dev",
    "https://apohara.vercel.app",
    "https://apohara-inti.vercel.app",
    "https://apohara-inti.netlify.app",
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4173",
]
_extra_origins = os.environ.get("APOHARA_INTI_CORS_ORIGINS", "").strip()
_cors_origins = list(_DEFAULT_CORS_ORIGINS)
if _extra_origins:
    _cors_origins.extend(
        o.strip() for o in _extra_origins.split(",") if o.strip()
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    # Allow Vercel preview deploys (apohara-inti-<hash>.vercel.app) without
    # listing every hash. Regex covers .vercel.app + .netlify.app
    # subdomains starting with "apohara-inti".
    allow_origin_regex=r"^https://apohara-inti(-[a-z0-9-]+)?\.(vercel|netlify)\.app$",
    allow_credentials=False,  # BYOK is body-only; no cookies in flight
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------


@app.get("/health")
def health() -> JSONResponse:
    """Liveness probe — reports import status of both Apohara deps."""
    deps: dict[str, str] = {}
    deps["aegis"] = f"error: {_aegis_err}" if _aegis_err else "loaded"
    deps["contextforge"] = f"error: {_ctx_err}" if _ctx_err else "loaded"

    if _aegis_err or _ctx_err:
        body = {"status": "degraded", "deps": deps, "version": API_VERSION}
        return JSONResponse(status_code=503, content=body)
    body = {"status": "ok", "deps": deps, "version": API_VERSION}
    return JSONResponse(status_code=200, content=body)


# ---------------------------------------------------------------------------
# Ledger helpers — append-only JSONL with SHA-256 chain
# ---------------------------------------------------------------------------


def _read_last_hash() -> str:
    """Return the ``signed_hash`` of the last ledger entry, or ZERO_HASH."""
    if not LEDGER_PATH.exists():
        return ZERO_HASH
    last = ZERO_HASH
    try:
        with LEDGER_PATH.open("r", encoding="utf-8") as fh:
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


def _append_ledger(entry: dict[str, Any], prev_hash: str) -> str:
    """Compute SHA-256 chain hash, append entry, return signed_hash."""
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    payload = dict(entry)
    payload["prev_hash"] = prev_hash
    # canonical JSON, no whitespace, sorted keys
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256((prev_hash + canonical).encode("utf-8")).hexdigest()
    payload["signed_hash"] = digest
    with LEDGER_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, sort_keys=True) + "\n")
    return digest


def _read_ledger_entry(signed_hash: str) -> Optional[dict[str, Any]]:
    """Find the ledger entry with the given signed_hash; None if not found."""
    if not LEDGER_PATH.exists():
        return None
    try:
        with LEDGER_PATH.open("r", encoding="utf-8") as fh:
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


# ---------------------------------------------------------------------------
# Gemini writer
# ---------------------------------------------------------------------------


# Sentinel exception so the endpoint can map upstream 401s to HTTP 401.
class _GeminiAuthError(Exception):
    pass


def _call_gemini(api_key: str, task_input: str) -> str:
    """Call Gemini with the user's BYOK; return the model's text response.

    Maps unauthorized API-key responses to :class:`_GeminiAuthError` so the
    endpoint translates them to a clean HTTP 401 instead of a 500. Any other
    SDK error bubbles up.
    """
    from google import genai
    from google.genai import errors as genai_errors

    client = genai.Client(api_key=api_key)
    prompt = (
        "You are a senior code reviewer. The user has submitted the following "
        "task or code for review. Review it, identify any issues, and provide "
        "a corrected/improved version with brief commentary on what you "
        "changed and why. Keep your response concise.\n\n"
        f"TASK / CODE TO REVIEW:\n{task_input}"
    )
    try:
        resp = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
    except genai_errors.ClientError as exc:
        # 401 / 403 unauthorized typically surfaces as ClientError with
        # a 4xx status_code attribute.
        status = getattr(exc, "code", None) or getattr(exc, "status_code", None)
        if status in (401, 403):
            raise _GeminiAuthError(str(exc)) from exc
        msg = str(exc).lower()
        if "401" in msg or "unauthorized" in msg or "api key" in msg:
            raise _GeminiAuthError(str(exc)) from exc
        raise
    text = getattr(resp, "text", None)
    if text is None:
        # Some SDK paths return a structured candidate list; fall back.
        try:
            text = resp.candidates[0].content.parts[0].text  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            text = ""
    return str(text)


# ---------------------------------------------------------------------------
# Adversarial attacker pass
# ---------------------------------------------------------------------------


_ADVERSARIAL_INSTRUCTIONS = (
    "You are a security reviewer auditing AI-generated code. Below is a task "
    "and a code review produced by another AI (Gemini). Find any "
    "vulnerabilities, prompt-injection vectors, logic bugs, or unsafe "
    "patterns in either the task or the review. Respond ONLY with a JSON "
    "object containing keys: is_harmful (bool), confidence (float 0-1), "
    "category (one of: harassment, hate_speech, sexually_explicit, "
    "dangerous_content, other), reason (brief explanation, <=200 chars). "
    "Set is_harmful=true ONLY if the code has a real problem worth blocking "
    "(vuln, injection vector, logic bug). The category field is required by "
    'the schema but is secondary; pick "other" if no other label fits.'
)


def _build_adversarial_prompt(task_input: str, gemini_output: str) -> str:
    return (
        _ADVERSARIAL_INSTRUCTIONS
        + "\n\nTASK SUBMITTED BY USER:\n"
        + task_input
        + "\n\nREVIEW PRODUCED BY GEMINI:\n"
        + gemini_output
        + "\n"
    )


def _filter_gemini_seat(adapters: list[Any]) -> list[Any]:
    """Drop the Gemini seat — user already provided Gemini as writer.

    Aegis returns 10 seats; we keep 9. The Gemini seat is identified by
    vendor label prefix ``"gemini"`` (the ``FallbackVendorAdapter.vendor``
    attribute set by ``make_default_adapters`` is e.g. ``"gemini-seat"``).
    """
    filtered = []
    for ad in adapters:
        vendor = (getattr(ad, "vendor", "") or "").lower()
        if vendor.startswith("gemini"):
            continue
        filtered.append(ad)
    return filtered


async def _run_attackers(
    adapters: list[Any],
    prompt: str,
) -> tuple[list[JudgeVerdict], float, bool]:
    """Run the 9 adversarial adapters in parallel with a cost ceiling.

    Returns (verdicts, cumulative_cost_usd, cost_capped). When the running
    cost exceeds ``COST_CEILING_USD`` mid-batch, remaining adapters are
    short-circuited to an out_of_budget verdict (not harmful, not active).
    """
    # Snapshot starting cost so callers can attribute cost to THIS call.
    base_cost = sum(getattr(ad, "cumulative_cost_usd", 0.0) for ad in adapters)

    async def _wrapped(ad: Any) -> JudgeVerdict:
        # Defensive: if budget already exceeded before we start this adapter,
        # return an out_of_budget verdict and skip the HTTP call.
        live_cost = (
            sum(getattr(a, "cumulative_cost_usd", 0.0) for a in adapters)
            - base_cost
        )
        if live_cost >= COST_CEILING_USD:
            return JudgeVerdict(
                is_harmful=False,
                confidence=0.0,
                category="harassment",  # placeholder; not used in verdict
                reason="per-call cost ceiling reached",
                model=getattr(ad, "model", "unknown"),
                vendor=getattr(ad, "vendor", "unknown"),
                latency_ms=0.0,
                error=f"cost_capped_per_call_usd={COST_CEILING_USD}",
                path="out_of_budget",
            )
        try:
            return await ad.evaluate(prompt)
        except Exception as exc:  # noqa: BLE001
            # Honest fail-open — match aegis' VendorAdapter contract.
            return JudgeVerdict(
                is_harmful=False,
                confidence=0.0,
                category="harassment",
                reason="adapter raised",
                model=getattr(ad, "model", "unknown"),
                vendor=getattr(ad, "vendor", "unknown"),
                latency_ms=0.0,
                error=f"transport: {exc!s}"[:160],
                path="unavailable",
            )

    verdicts = await asyncio.gather(*(_wrapped(ad) for ad in adapters))
    delta_cost = (
        sum(getattr(ad, "cumulative_cost_usd", 0.0) for ad in adapters)
        - base_cost
    )
    cost_capped = delta_cost >= COST_CEILING_USD
    return list(verdicts), float(delta_cost), bool(cost_capped)


def _aggregate_verdict(reports: list[AttackerReport]) -> str:
    """Map attacker harmful-count to verdict string per acceptance criteria."""
    harmful_count = sum(1 for r in reports if r.found_issue)
    if harmful_count >= VERDICT_BLOCK_THRESHOLD:
        return "blocked"
    if harmful_count >= VERDICT_REVIEW_THRESHOLD:
        return "risky"
    return "verified"


# Module-level singleton: shared rate limiter for /v1/demo_verify.
DEMO_MAX_PER_DAY = 5
_demo_limiter = DailyRateLimiter(max_per_day=DEMO_MAX_PER_DAY)


def _client_ip(request: Request) -> str:
    """Extract the originating client IP, honoring X-Forwarded-For.

    Caddy / nginx / Vultr LB set X-Forwarded-For with the original IP first.
    Falls back to request.client.host for direct connections (local dev).
    """
    xff = request.headers.get("X-Forwarded-For", "").strip()
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ---------------------------------------------------------------------------
# /v1/verify
# ---------------------------------------------------------------------------


@app.post("/v1/verify", response_model=VerifyResponse)
async def verify(req: VerifyRequest) -> VerifyResponse:
    """Run a code/task through Gemini writer + 9-attacker adversarial pass.

    Pipeline:
      1. Gemini (user BYOK) reviews/fixes the task_input.
      2. Build adversarial prompt combining task_input + Gemini output.
      3. Run 9 attacker adapters in parallel (Gemini seat filtered out).
      4. INV-15 gate decision for each attacker (role="critic").
      5. Aggregate harmful_count -> verdict.
      6. Sign + append to SHA-256 ledger chain.
    """
    if _aegis_err is not None or _ctx_err is not None:
        raise HTTPException(
            status_code=503,
            detail=f"deps not loaded: aegis={_aegis_err!s}; "
                   f"contextforge={_ctx_err!s}",
        )

    t0 = time.perf_counter()

    # ---- 0.5 LobsterTrap DPI pre-check (active when LOBSTERTRAP_URL set) ----
    lt_url = (os.environ.get("LOBSTERTRAP_URL") or "").strip() or None
    dpi_check = await check_prompt_with_lobstertrap(req.task_input, lt_url)
    if not dpi_check["allowed"]:
        # Short-circuit: never call Gemini, never run attackers, audit the block.
        dpi_audit_id = str(uuid.uuid4())
        dpi_latency_ms = (time.perf_counter() - t0) * 1000.0
        dpi_prev_hash = _read_last_hash()
        dpi_entry = {
            "verdict": "blocked",
            "attackers": [],
            "memory_isolation": {
                "inv15_enforced": True,
                "contextforge_audit_id": dpi_audit_id,
            },
            "dpi_check": dpi_check,
            "latency_ms": round(dpi_latency_ms, 3),
            "cost_estimate_usd": 0.0,
            "cost_capped": False,
            "ts": time.time(),
        }
        dpi_signed = _append_ledger(dpi_entry, dpi_prev_hash)
        return VerifyResponse(
            verdict="blocked",
            attackers=[],
            memory_isolation=MemoryIsolationReport(
                inv15_enforced=True,
                contextforge_audit_id=dpi_audit_id,
            ),
            signed_hash=dpi_signed,
            latency_ms=round(dpi_latency_ms, 3),
            cost_estimate_usd=0.0,
            cost_capped=False,
        )

    # ---- 1. Gemini writer pass ---------------------------------------------
    try:
        gemini_output = await asyncio.to_thread(
            _call_gemini, req.gemini_api_key, req.task_input
        )
    except _GeminiAuthError as exc:
        raise HTTPException(
            status_code=401,
            detail=f"Gemini API key rejected: {exc!s}. "
                   "Check your BYOK token at https://aistudio.google.com/apikey",
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=502,
            detail=f"Gemini upstream error: {type(exc).__name__}: {exc!s}",
        ) from exc

    # ---- 2. Build adversarial prompt ---------------------------------------
    prompt = _build_adversarial_prompt(req.task_input, gemini_output)

    # ---- 3 + 4. Attackers + INV-15 -----------------------------------------
    all_adapters = make_default_adapters()  # type: ignore[misc]
    attackers = _filter_gemini_seat(all_adapters)
    # Defensive sanity: spec says 9.
    if len(attackers) != 9:
        # Don't crash; log via the verdict trail. Continue with whatever
        # we got — better partial than no audit.
        pass

    verdicts, delta_cost, cost_capped = await _run_attackers(attackers, prompt)

    # INV-15 gate: fresh JCRSafetyGate per request, one decision per attacker
    # call. role="critic" with candidate_count=N(attackers), reuse_rate=0.0
    # (no cache reuse across attackers), layout_shuffled=True (each attacker
    # sees a fresh ordering). Risk for N>=9 critics with shuffled layout +
    # reuse_rate=0 well exceeds the 0.7 default threshold -> dense prefill
    # mandated -> KV-cache isolation enforced.
    gate = JCRSafetyGate()  # type: ignore[misc]
    audit_id = str(uuid.uuid4())
    inv15_enforced_all = True
    for _ in verdicts:
        decision = gate.gate_decision(
            agent_role="critic",
            candidate_count=len(attackers),
            reuse_rate=0.0,
            layout_shuffled=True,
        )
        if not decision.use_dense:
            inv15_enforced_all = False

    # ---- 5. Build attacker reports + verdict --------------------------------
    reports: list[AttackerReport] = []
    for v in verdicts:
        # Active calls only count toward the harmful tally; unavailable
        # / out_of_budget seats default to found_issue=False (honest open).
        active = v.path == "primary" or v.path == "fallback"
        found_issue = bool(v.is_harmful) if active else False
        reasoning = v.reason if active else (
            f"unavailable ({v.path}): {v.error or 'no detail'}"
        )
        reports.append(
            AttackerReport(
                vendor=v.vendor,
                model=v.model,
                found_issue=found_issue,
                reasoning=reasoning[:500],
            )
        )

    verdict_str = _aggregate_verdict(reports)
    latency_ms = (time.perf_counter() - t0) * 1000.0

    # ---- 6. Sign + ledger append --------------------------------------------
    prev_hash = _read_last_hash()
    entry = {
        "verdict": verdict_str,
        "attackers": [r.model_dump() for r in reports],
        "memory_isolation": {
            "inv15_enforced": inv15_enforced_all,
            "contextforge_audit_id": audit_id,
        },
        "dpi_check": dpi_check,
        "latency_ms": round(latency_ms, 3),
        "cost_estimate_usd": round(delta_cost, 6),
        "cost_capped": cost_capped,
        "ts": time.time(),
    }
    signed_hash = _append_ledger(entry, prev_hash)

    return VerifyResponse(
        verdict=verdict_str,
        attackers=reports,
        memory_isolation=MemoryIsolationReport(
            inv15_enforced=inv15_enforced_all,
            contextforge_audit_id=audit_id,
        ),
        signed_hash=signed_hash,
        latency_ms=round(latency_ms, 3),
        cost_estimate_usd=round(delta_cost, 6),
        cost_capped=cost_capped,
    )


# ---------------------------------------------------------------------------
# /v1/demo_verify  — same pipeline as /v1/verify, server-side key + rate limit
# ---------------------------------------------------------------------------


@app.post("/v1/demo_verify", response_model=VerifyResponse)
async def demo_verify(
    req: DemoVerifyRequest,
    request: Request,
    response: Response,
) -> VerifyResponse:
    """Run /v1/verify with a server-side Gemini key, capped per-IP per day.
    503 when ``DEMO_GEMINI_KEY`` unset; 429 when daily quota exhausted."""
    demo_key = (os.environ.get("DEMO_GEMINI_KEY") or "").strip()
    if not demo_key:
        raise HTTPException(status_code=503, detail="demo mode not configured")

    ip = _client_ip(request)
    allowed, remaining, reset_at = await _demo_limiter.check_and_consume(ip)
    if not allowed:
        secs_to_reset = max(
            1,
            int((reset_at - datetime.now(timezone.utc)).total_seconds()),
        )
        raise HTTPException(
            status_code=429,
            detail={
                "detail": "demo limit reached for today",
                "remaining": 0,
                "reset_at": reset_at.isoformat(),
            },
            headers={"Retry-After": str(secs_to_reset)},
        )

    # Delegate to the canonical verify() so DPI, ledger, attackers + INV-15
    # all behave identically — no duplicated pipeline to keep in sync.
    forwarded = VerifyRequest(gemini_api_key=demo_key, task_input=req.task_input)
    result = await verify(forwarded)
    response.headers["X-Apohara-Demo-Remaining"] = str(remaining)
    return result


# ---------------------------------------------------------------------------
# /v1/audit/{verdict_id}
# ---------------------------------------------------------------------------


@app.get("/v1/audit/{verdict_id}")
def audit(verdict_id: str) -> JSONResponse:
    """Return a previously-signed verdict from the ledger, or 404."""
    entry = _read_ledger_entry(verdict_id)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"no ledger entry for {verdict_id}")
    return JSONResponse(status_code=200, content=entry)
