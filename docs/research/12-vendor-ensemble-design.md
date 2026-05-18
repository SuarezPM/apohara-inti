# 12-Vendor Ensemble Expansion Design

**Status:** Proposal — pending sister-repo implementation in `apohara-aegis`  
**Date:** 2026-05-18  
**Author:** Pablo M. Suarez  
**Related:** [apohara-aegis#TBD](https://github.com/SuarezPM/apohara-aegis) (filed as part of this doc)

---

## Current State (9-vendor ensemble)

`apohara_aegis.multi_judge.make_default_adapters()` returns 9 vendor adapters:

| # | Vendor key | Model |
|---|-----------|-------|
| 1 | claude-opus-47-seat | claude-opus-4-7 |
| 2 | gpt-55-seat | gpt-5.5 |
| 3 | deepseek-v4-seat | deepseek-v4-pro |
| 4 | kimi-k26-seat | kimi-k2.6 |
| 5 | glm-51-seat | glm-5.1 |
| 6 | qwen36-plus-seat | qwen3.6-plus |
| 7 | nemotron-3-super-seat | nvidia/nemotron-3-super-120b-a12b |
| 8 | minimax-m27-seat | MiniMax-M2.7 |
| 9 | big-pickle-seat | big-pickle (via OpenRouter) |

Estimated cost per full pipeline call: **~$0.038 USD** (9 × average ~$0.004).  
Current verdict aggregation thresholds: **≥3 harmful → risky**, **≥6 harmful → blocked**.

---

## Proposed Additions (target: 12 vendors)

### Vendor 10 — Mistral Large 2411

- **Route:** `mistralai/mistral-large-2411` via OpenRouter  
- **Rationale:** European AI company subject to EU AI Act compliance constraints.  
  Mistral's RLHF and safety tuning differ substantially from US-trained models,  
  providing a distinct training distribution that catches bias patterns  
  invisible to GPT/Claude. Adds regulatory diversity to the ensemble.  
- **Cost per call:** ~$0.004 USD (comparable to existing vendors)

### Vendor 11 — Grok-2-1212

- **Route:** `x-ai/grok-2-1212` via OpenRouter  
- **Rationale:** X.ai's flagship model trained on a different data distribution  
  (heavy social/real-time corpus). Its anomalous reasoning patterns surface  
  adversarial prompt vectors that academic-corpus models miss. Adding a  
  non-OpenAI, non-Anthropic, non-Google frontier model strengthens ensemble  
  coverage at the frontier tier.  
- **Cost per call:** ~$0.005 USD

### Vendor 12 — Perplexity Sonar Large 128k Online

- **Route:** `perplexity/llama-3.1-sonar-large-128k-online` via OpenRouter  
- **Rationale:** Web-grounded variant — performs live retrieval before  
  generating its verdict. This uniquely positions it to catch CVE references  
  in submitted code snippets, deprecated API patterns with known exploits,  
  and supply-chain vulnerabilities linked to current advisories (e.g. PyPI  
  packages flagged post-submission). No other vendor in the current ensemble  
  is web-grounded.  
- **Cost per call:** ~$0.008 USD (retrieval premium)

---

## Cost Impact

| Scenario | Vendors | Est. cost/call | vs. baseline |
|----------|---------|---------------|--------------|
| Current | 9 | ~$0.038 USD | — |
| Proposed | 12 | ~$0.055 USD | +45% |
| COST_CEILING_USD | — | $0.50 | well under ceiling |

Cost ceiling (`COST_CEILING_USD = 0.50` in `main.py`) remains safe. The per-vendor  
soft cap in `_run_attackers()` is unchanged.

---

## Verdict Aggregation Threshold Rescaling

Current thresholds were calibrated for 9 vendors.  
Scaling proportionally to 12 vendors (note: rounding to nearest integer):

| Signal | Current (9-vendor) | Proposed (12-vendor) |
|--------|-------------------|---------------------|
| risky  | ≥ 3 harmful        | ≥ 4 harmful          |
| blocked | ≥ 6 harmful       | ≥ 8 harmful          |

**This change must land as a separate PR** from the adapter expansion,  
after running the full regression suite with the updated thresholds.  
`VERDICT_REVIEW_THRESHOLD` and `VERDICT_BLOCK_THRESHOLD` are constants in  
`packages/backend/main.py` — update there **and** in `AUDIT.md`.

---

## Integration Pattern

The adapter list lives exclusively in the sister repo:

```
apohara-aegis/
  apohara_aegis/
    multi_judge.py      # make_default_adapters() → returns list of adapters
```

Steps to implement:

1. **apohara-aegis PR:** Add `_MistralAdapter`, `_GrokAdapter`, `_SonarAdapter`  
   to `multi_judge.py` following the existing `_OpenRouterAdapter` pattern.  
   Append to the return value of `make_default_adapters()`.
2. **apohara-probant PR (threshold only):** Update `VERDICT_REVIEW_THRESHOLD = 4`  
   and `VERDICT_BLOCK_THRESHOLD = 8` in `packages/backend/main.py`.  
   Update docstring in module header. Update `AUDIT.md`.
3. **Regression:** `PYTHONPATH=. python3 -m pytest packages/backend/tests/ -q`  
   must pass (currently 32 tests). Add 3 new adapter smoke tests.

---

## Threat Model

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Vendor outage (any 1 of 12) | Medium | Low — other 11 still vote | `_run_attackers()` already has per-adapter exception catch; returning `latency_ms=0.0` with `found_issue=False` on timeout. Consider explicit `found_issue=None` / abstain path. |
| OpenRouter rate-limit ceiling | Low | Medium — all 3 new vendors route via OpenRouter | Add OpenRouter tier upgrade check to onboarding docs. Implement exponential backoff with jitter in `_OpenRouterAdapter.evaluate()`. |
| Prompt-template divergence | Low | Medium — vendor misreads task format | Existing envelope (`TaintedString + build_envelope`) is vendor-agnostic. New adapters must pass the full prompt string unchanged; no vendor-specific template transformations. |
| Cost spike (web-retrieval on Sonar) | Low | Low — ceiling enforced | Cost cap in `_run_attackers()` already terminates on `COST_CEILING_USD` breach. No additional action required. |

---

## Acceptance Criteria (for apohara-aegis PR)

- `make_default_adapters()` returns exactly 12 adapters when all env vars set  
- Each new adapter passes the existing `test_verify_happy_path_verified` fixture  
- `scripts/check_honesty.sh` passes (no hardcoded cost literals)  
- All 32 existing `test_*.py` tests pass unmodified  
- 3 new unit tests: `test_mistral_adapter_calls_openrouter`, `test_grok_adapter_calls_openrouter`, `test_sonar_adapter_calls_openrouter`

---

## Design Doc Location

This file: `docs/research/12-vendor-ensemble-design.md`  
Canonical URL (post-rename): <https://github.com/SuarezPM/apohara-probant/blob/main/docs/research/12-vendor-ensemble-design.md>
