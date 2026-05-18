"""Per-vendor latency profile for the Apohara PROBANT /v1/demo_verify endpoint.

US-T1-K acceptance criterion: measure real pipeline latency across N=5 parallel
calls and emit a structured JSON log to logs/latency_profile_{ISO8601-ts}.json.

Honesty note: AttackerReport in the current schema exposes only:
  vendor, model, found_issue, reasoning
It does NOT expose per-vendor latency_ms. Therefore this script measures
total pipeline latency per call only. Per-vendor breakdown requires an upstream
schema change (expose attackers[].latency_ms from _run_attackers() into the
AttackerReport model). See methodology.gap in the output JSON.

Run:
    cd /home/linconx/Documentos/apohara-inti/packages/backend
    python3 tests/latency_profile.py

Quota note: uses /v1/demo_verify which is rate-limited 5 calls/IP/day.
This script issues exactly N_CALLS=5 requests — consumes the full daily quota.
"""
from __future__ import annotations

import asyncio
import json
import math
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

API_BASE = "https://api.apohara.dev"
ENDPOINT = "/v1/demo_verify"
N_CALLS = 5
TIMEOUT_S = 90  # demo endpoint can be slow on cold start

# Diverse benign prompts — cover real code review scenarios
PROMPTS = [
    "def binary_search(arr, target):\n    lo, hi = 0, len(arr) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1",
    "import hashlib\n\ndef hash_password(password: str) -> str:\n    return hashlib.md5(password.encode()).hexdigest()",
    "async function fetchUserData(userId) {\n  const response = await fetch(`/api/users/${userId}`);\n  return response.json();\n}",
    "SELECT u.name, u.email, o.total FROM users u JOIN orders o ON u.id = o.user_id WHERE o.status = 'pending';",
    "public class TokenValidator {\n  public boolean validate(String token) {\n    return token.equals(System.getenv(\"SECRET_TOKEN\"));\n  }\n}",
]

LOGS_DIR = Path(__file__).parents[3] / "logs"


# ---------------------------------------------------------------------------
# Stats helpers
# ---------------------------------------------------------------------------

def _percentile(sorted_vals: list[float], p: float) -> float:
    """Compute p-th percentile (0-100) via linear interpolation."""
    if not sorted_vals:
        return float("nan")
    n = len(sorted_vals)
    idx = (p / 100.0) * (n - 1)
    lo, hi = int(idx), min(int(idx) + 1, n - 1)
    frac = idx - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def _wilson_95_ci(successes: int, n: int) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion, 95% confidence."""
    if n == 0:
        return (0.0, 1.0)
    z = 1.96  # 95% two-tailed
    p_hat = successes / n
    denom = 1 + z ** 2 / n
    centre = (p_hat + z ** 2 / (2 * n)) / denom
    margin = z * math.sqrt(p_hat * (1 - p_hat) / n + z ** 2 / (4 * n ** 2)) / denom
    return (max(0.0, round(centre - margin, 4)), min(1.0, round(centre + margin, 4)))


# ---------------------------------------------------------------------------
# HTTP call
# ---------------------------------------------------------------------------

async def _single_call(
    client: httpx.AsyncClient,
    prompt: str,
    call_idx: int,
) -> dict:
    """Issue one POST to /v1/demo_verify and return timing + parsed body."""
    t0 = time.perf_counter()
    try:
        resp = await client.post(
            ENDPOINT,
            json={"task_input": prompt},
            timeout=TIMEOUT_S,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        resp.raise_for_status()
        body = resp.json()
        return {
            "call_idx": call_idx,
            "success": True,
            "latency_ms": round(elapsed_ms, 3),
            "status_code": resp.status_code,
            "verdict": body.get("verdict", "unknown"),
            "cost_estimate_usd": body.get("cost_estimate_usd", None),
            "cost_capped": body.get("cost_capped", False),
            "attackers": body.get("attackers", []),
        }
    except Exception as exc:  # noqa: BLE001
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "call_idx": call_idx,
            "success": False,
            "latency_ms": round(elapsed_ms, 3),
            "error": str(exc)[:200],
            "attackers": [],
        }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def run_profile() -> dict:
    ts_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"[latency_profile] Starting {N_CALLS} parallel calls to {API_BASE}{ENDPOINT}")
    print(f"[latency_profile] Timestamp: {ts_utc}")

    async with httpx.AsyncClient(base_url=API_BASE) as client:
        t_total_start = time.perf_counter()
        results = await asyncio.gather(
            *[_single_call(client, PROMPTS[i], i) for i in range(N_CALLS)]
        )
        wall_clock_ms = (time.perf_counter() - t_total_start) * 1000.0

    # -----------------------------------------------------------------------
    # Pipeline total aggregation
    # -----------------------------------------------------------------------
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    if failed:
        print(f"[latency_profile] WARNING: {len(failed)} call(s) failed:")
        for f in failed:
            print(f"  call {f['call_idx']}: {f.get('error', '?')}")

    pipeline_latencies = sorted(r["latency_ms"] for r in successful)
    costs = [r["cost_estimate_usd"] for r in successful if r.get("cost_estimate_usd") is not None]

    pipeline_stats = {
        "n_successful": len(successful),
        "n_failed": len(failed),
        "wall_clock_ms": round(wall_clock_ms, 3),
    }
    if pipeline_latencies:
        pipeline_stats["p50_ms"] = round(_percentile(pipeline_latencies, 50), 3)
        pipeline_stats["p95_ms"] = round(_percentile(pipeline_latencies, 95), 3)
        pipeline_stats["mean_ms"] = round(statistics.mean(pipeline_latencies), 3)
        pipeline_stats["min_ms"] = round(min(pipeline_latencies), 3)
        pipeline_stats["max_ms"] = round(max(pipeline_latencies), 3)
        pipeline_stats["mean_cost_usd"] = round(statistics.mean(costs), 6) if costs else None

    # -----------------------------------------------------------------------
    # Per-vendor aggregation — from AttackerReport fields only
    #
    # NOTE: AttackerReport schema (vendor, model, found_issue, reasoning)
    # does NOT include latency_ms. We can track: how often each vendor
    # found an issue (success_rate proxy) and whether it appeared in the
    # response at all.
    # -----------------------------------------------------------------------
    vendor_obs: dict[str, list[bool]] = {}
    for r in successful:
        for attacker in r.get("attackers", []):
            key = f"{attacker.get('vendor', 'unknown')}:{attacker.get('model', 'unknown')}"
            vendor_obs.setdefault(key, []).append(attacker.get("found_issue", False))

    per_vendor: dict[str, dict] = {}
    for key, observations in vendor_obs.items():
        n = len(observations)
        successes = sum(1 for v in observations if v)
        lo, hi = _wilson_95_ci(successes, n)
        per_vendor[key] = {
            "n_observations": n,
            "found_issue_count": successes,
            "issue_rate": round(successes / n, 4) if n else 0.0,
            "wilson_95_ci": [lo, hi],
            # per-vendor latency_ms: NOT AVAILABLE in current schema
            "p50_ms": None,
            "p95_ms": None,
            "mean_ms": None,
        }

    # -----------------------------------------------------------------------
    # Summary table (markdown)
    # -----------------------------------------------------------------------
    table_rows = []
    table_rows.append("| Vendor:Model | Observations | Issue Rate | Wilson 95% CI | p50 ms | p95 ms |")
    table_rows.append("|---|---|---|---|---|---|")
    for key in sorted(per_vendor):
        pv = per_vendor[key]
        ci = pv["wilson_95_ci"]
        p50 = "n/a" if pv["p50_ms"] is None else f"{pv['p50_ms']:.0f}"
        p95 = "n/a" if pv["p95_ms"] is None else f"{pv['p95_ms']:.0f}"
        table_rows.append(
            f"| {key} | {pv['n_observations']} | {pv['issue_rate']:.1%} "
            f"| [{ci[0]:.3f}, {ci[1]:.3f}] | {p50} | {p95} |"
        )
    if pipeline_latencies:
        table_rows.append("|---|---|---|---|---|---|")
        table_rows.append(
            f"| **PIPELINE TOTAL** | {len(successful)}/{N_CALLS} calls | — | — "
            f"| **{pipeline_stats.get('p50_ms', 'n/a')}** | **{pipeline_stats.get('p95_ms', 'n/a')}** |"
        )
    summary_table_md = "\n".join(table_rows)

    # -----------------------------------------------------------------------
    # Assemble output
    # -----------------------------------------------------------------------
    gap_note = (
        "Per-vendor latency_ms is NOT exposed in /v1/verify or /v1/demo_verify "
        "AttackerReport schema (fields: vendor, model, found_issue, reasoning). "
        "Total pipeline latency measured; per-vendor breakdown requires upstream "
        "schema change: add latency_ms to AttackerReport and populate it in "
        "_run_attackers() from the individual adapter .evaluate() timing."
    )

    output = {
        "methodology": {
            "n_calls": N_CALLS,
            "api_base": API_BASE,
            "endpoint": ENDPOINT,
            "ts_utc": ts_utc,
            "wall_clock_ms": round(wall_clock_ms, 3),
            "parallelism": "asyncio.gather (all N_CALLS in flight simultaneously)",
            "gap": gap_note,
        },
        "per_vendor": per_vendor,
        "pipeline_total": pipeline_stats,
        "raw_results": results,
        "summary_table_md": summary_table_md,
    }

    return output


def main() -> None:
    result = asyncio.run(run_profile())

    # Write to logs/
    ts_file = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = LOGS_DIR / f"latency_profile_{ts_file}.json"
    out_path.write_text(json.dumps(result, indent=2) + "\n")
    print(f"\n[latency_profile] Wrote {out_path}")

    # Print summary
    ps = result["pipeline_total"]
    print(f"\n=== Pipeline Total ===")
    print(f"  Successful calls : {ps.get('n_successful', 0)}/{N_CALLS}")
    if ps.get("n_failed"):
        print(f"  Failed calls     : {ps['n_failed']}")
    if "p50_ms" in ps:
        print(f"  p50 latency      : {ps['p50_ms']} ms")
        print(f"  p95 latency      : {ps['p95_ms']} ms")
        print(f"  mean latency     : {ps['mean_ms']} ms")
    if ps.get("mean_cost_usd") is not None:
        print(f"  mean cost        : ${ps['mean_cost_usd']:.6f} USD")
    print(f"\n=== Per-Vendor (issue rate, latency n/a — schema gap) ===")
    for key in sorted(result["per_vendor"]):
        pv = result["per_vendor"][key]
        print(f"  {key}: n={pv['n_observations']} issue_rate={pv['issue_rate']:.1%}")
    print(f"\n{result['summary_table_md']}")
    print(f"\n[HONESTY] {result['methodology']['gap']}")


if __name__ == "__main__":
    main()
