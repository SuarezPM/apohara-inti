# Latency Profile — Apohara PROBANT Pipeline

**Date:** 2026-05-18T16:22:58Z  
**Log:** `logs/latency_profile_20260518T162409Z.json`  
**Harness:** `packages/backend/tests/latency_profile.py`

---

## Methodology

Five parallel calls (`asyncio.gather`) were issued against `https://api.apohara.dev/v1/demo_verify`
using five diverse benign code-review prompts (binary search, MD5 hashing, async fetch, SQL JOIN, Java token validator).
All calls were fired simultaneously; wall-clock time was 70.9 s.

**N = 5 intended, N = 3 successful.** Two calls received HTTP 429 (Too Many Requests)
from the 5-calls/IP/day rate limiter, returning in ~845 ms each. Statistics below
are computed on the 3 successful calls only.

---

## Pipeline Total Latency

| Metric | Value |
|--------|-------|
| Successful calls | 3 / 5 |
| p50 latency | **52,849 ms** (52.8 s) |
| p95 latency | **69,083 ms** (69.1 s) |
| mean latency | **54,763 ms** (54.8 s) |
| min latency | 40,554 ms (40.6 s) |
| max latency | 70,887 ms (70.9 s) |
| mean cost | **$0.0462 USD/call** |

The 40–70 s range reflects real upstream Gemini + 9-vendor attacker ensemble wall-clock,
including Gemini writing a review, then the 9 OpenRouter/opencode_zen adapters evaluating
in parallel.

---

## Per-Vendor Presence and Issue Rate

| Vendor:Model | Observations | Issue Rate | Wilson 95% CI | p50 ms | p95 ms |
|---|---|---|---|---|---|
| opencode_zen:big-pickle | 3 | 0.0% | [0.000, 0.561] | n/a | n/a |
| opencode_zen:deepseek-v4-flash-free | 1 | 0.0% | [0.000, 0.793] | n/a | n/a |
| opencode_zen:minimax-m2.7 | 3 | 0.0% | [0.000, 0.561] | n/a | n/a |
| openrouter:anthropic/claude-opus-4.7-fast | 3 | 0.0% | [0.000, 0.561] | n/a | n/a |
| openrouter:deepseek/deepseek-v4-pro | 2 | 0.0% | [0.000, 0.658] | n/a | n/a |
| openrouter:moonshotai/kimi-k2.6 | 3 | 0.0% | [0.000, 0.561] | n/a | n/a |
| openrouter:nvidia/nemotron-3-super-120b-a12b | 3 | 0.0% | [0.000, 0.561] | n/a | n/a |
| openrouter:openai/gpt-5.5 | 3 | 0.0% | [0.000, 0.561] | n/a | n/a |
| openrouter:qwen/qwen3.6-plus | 3 | 0.0% | [0.000, 0.561] | n/a | n/a |
| openrouter:z-ai/glm-5.1 | 3 | 0.0% | [0.000, 0.561] | n/a | n/a |
|---|---|---|---|---|---|
| **PIPELINE TOTAL** | 3/5 calls | — | — | **52849** | **69083** |

All 3 successful calls returned `verdict: "verified"`. The benign prompts produced
zero `found_issue: true` votes across all 10 vendor slots observed. The wide Wilson 95%
confidence intervals (e.g. [0.000, 0.561]) reflect the small n=3 sample — these are
not meaningful issue-rate estimates.

---

## Schema Gap: Per-Vendor Latency Not Available

The `AttackerReport` model (`packages/backend/main.py`) exposes only:
`vendor`, `model`, `found_issue`, `reasoning`. No `latency_ms` field is returned
per attacker. The p50/p95/mean columns above show "n/a" for this reason.

To enable per-vendor latency profiling in future runs, the upstream schema must be extended:

1. Add `latency_ms: float` to `AttackerReport` in `main.py`
2. Populate it in `_run_attackers()` by timing each `adapter.evaluate()` call individually
3. Surface it in the JSON response

---

## Honesty Caveats

- **Small n=5 (3 effective):** Two 429s from the demo rate limiter. p50/p95 estimates
  have large uncertainty — treat as order-of-magnitude only.
- **Single-IP measurement:** The 429 behaviour itself is evidence of the rate limiter
  functioning correctly. In a real load scenario, per-IP throttling would cap
  abuse at 5 calls/day.
- **Demo quota consumed:** This run exhausted the full 5-call/IP/day quota for 2026-05-18.
  Re-runs not possible today from the same IP without key rotation.
- **opencode_zen adapters returned HTTP 401:** `deepseek-v4-flash-free`, `minimax-m2.7`,
  and `big-pickle` returned `"unavailable (unavailable): transport: HTTP Error 401: Unauthorized"`
  in their reasoning field. These adapters are gracefully degraded (verdict = not harmful,
  so they do not inflate the block count). This suggests the opencode_zen credentials on
  the prod droplet need rotation.
- **z-ai/glm-5.1 and kimi-k2.6 returned `parse_error`** in some calls — known upstream
  instability on OpenRouter for these models.
