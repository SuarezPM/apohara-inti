# Granite Guardian 4 — Integration Research Note

**Summary**: IBM Granite Guardian 4 probe on JBB holdout (n=80) achieved 98.75% block rate; current status is probe-only, not in default ensemble seat.

---

## What is Granite Guardian 4?

IBM Granite Guardian 4 is an open-source safety-specialized model from IBM's Granite family, trained with RLHF specifically for safety judgment tasks rather than general instruction following. Unlike GPT-class models prompted with a safety rubric, Granite Guardian is fine-tuned end-to-end on harm detection datasets, giving it a safety-oriented inductive bias that generic large language models lack. It is smaller than frontier GPT/Claude/Gemini models but outperforms them on safety-specific benchmarks at a fraction of the inference cost, making it attractive as a dedicated judge seat rather than a general-purpose seat.

---

## Measurement Summary

| Phase | n | Block rate | p̂ | 95% Wilson CI | Log |
|---|---|---|---|---|---|
| US-004 probe | 5 | 5/5 (100%) | 1.000 | — (n too small) | `logs/granite4_probe_n5_20260516T163113Z.json` |
| US-004 followup | 80 | 79/80 (98.75%) | 0.9875 | [93.3%, 99.8%] | `logs/granite4_jbb_n80_20260516T164541Z.json` |

Wilson CI computed with z=1.96, formula: center = (p̂ + z²/2n) / (1 + z²/n), margin = z·√(p̂(1−p̂)/n + z²/4n²) / (1 + z²/n).

Both logs are committed in the `apohara-aegis` repository.

---

## Why Integrate?

- **Specialty safety bias**: Granite Guardian 4 is RLHF-fine-tuned for harm detection, not prompted. This gives it a qualitatively different failure mode than the 9 generic-LLM-as-judge seats currently in the ensemble — diversification that matters when adversarial prompts are designed to exploit generic instruction-following framing.
- **Regulatory diversity**: IBM's open-source license and IBM Cloud pricing make Granite Guardian 4 attractive for deployments requiring vendor diversity across the judge panel (e.g., EU AI Act Article 13 multi-source validation requirements).
- **Cost efficiency**: Granite Guardian 4 is significantly cheaper per-token than GPT-4o or Claude 3.7 Sonnet. Adding it as a dedicated safety seat does not materially increase per-inference cost and may allow downsizing a more expensive generic seat.

---

## Integration Status

- **Current**: probe-only. Granite Guardian 4 is NOT in a default ensemble seat and does NOT appear in `DEFAULT_COST_CAPS_USD`.
- **Pending**: cost-ledger entry in `DEFAULT_COST_CAPS_USD` (IBM Cloud pricing TBD; IBM offers dedicated inference pricing for Granite models via watsonx.ai).
- **Production integration**: tracked as post-hackathon followup. Requires: (1) IBM watsonx.ai API credentials in secrets store, (2) `GraniteGuardian4Adapter` class in `apohara_aegis/openrouter_adapters.py` or a dedicated `ibm_adapters.py`, (3) threshold rescale of `CONSENSUS_THRESHOLD` if GG4 is added as seat 11 or 12, (4) re-run JBB-80 with ensemble+GG4 to measure actual ensemble-level impact.

---

## Honest Note

**98.75% on JBB-80 is a single-model, single-run number — not an ensemble number.** Adding Granite Guardian 4 as an 11th or 12th seat does NOT trivially add 98.75% to ensemble performance. Vendor agreement dynamics mean GG4's vote weight interacts with the existing 9–10 seats in ways that can raise OR lower the ensemble block rate depending on which inputs GG4 disagrees on. The correct claim is: "GG4 alone achieved 98.75% on the JBB holdout; ensemble impact is unmeasured and must be quantified post-integration via threshold rescale." This measurement is tracked as post-hackathon work.

---

## Cross-References

- apohara-aegis commit [`0b2cf32`](https://github.com/SuarezPM/apohara-aegis/commit/0b2cf32) — US-004 probe (n=5)
- apohara-aegis commit [`cd1f439`](https://github.com/SuarezPM/apohara-aegis/commit/cd1f439) — US-004 followup head-to-head (n=80)
- `AUDIT.md` entries #20 / #21 — Granite Guardian 4 probe + followup measurement records
- Judge FAQ — see [`../submissions/JUDGE-FAQ.md`](../submissions/JUDGE-FAQ.md)
