# Milan AI Week 2026 — Apohara Inti submission (paste-ready)

> Target track: **Agent Bench** (primary, agentic benchmarking + governance)
> Deadline: 2026-05-20. Live: https://www.apohara.dev

---

## Field: Project name
```
Apohara Inti — Cross-AI Code Verifier
```

## Field: Tagline (max ~80 chars)
```
Cross-AI verification with formal KV-cache isolation. EU AI Act ready.
```

## Field: Short pitch (max ~200 chars)
```
Open-source agent benchmark: 9 frontier LLMs adversarially audit AI-generated code in isolated KV-caches. Formal INV-15 safety invariant. Tamper-evident verdict chain. Apache-2.0. Built for EU AI Act Article 14 governance requirements.
```

## Field: Long description (max ~2000 chars)
```
Apohara Inti is a reproducible benchmark + production tool for adversarial
auditing of AI-generated code. Gemini writes a review; 9 frontier vendors
(Claude, GPT, DeepSeek, Kimi, GLM, Qwen, Nemotron, MiniMax, Big-Pickle)
independently judge it. Aggregation: 0-2 harmful = verified · 3-5 = risky
· 6+ = blocked. Transparent rule, no black box.

Reproducibility:
- 350+ pytest tests + 15+ measurement JSONs in /logs/.
- JBB-Behaviors block rate 93.75% (Wilson 95% CI [86.2%, 97.3%], n=80
  holdout). Auditable methodology; numbers not hand-picked.
- Multi-hardware: AMD MI300X (ROCm 7.2) + NVIDIA H100.
- Honesty CI guard (scripts/check_honesty.sh) blocks hardcoded benchmark
  values in production code paths.

Formal safety:
- INV-15 JCRSafetyGate: published formal invariant for multi-agent
  KV-cache isolation (paper DOI 10.5281/zenodo.20114594). Judges never
  contaminate the writer's memory under adversarial prompt-injection
  load. Mechanically enforced per request, 0/1210 violations in sweep.

Defenses shipped this sprint:
- Prompt envelope (envelope.py) — untrusted blocks wrapped in per-call
  nonce-tagged sentinels (Spotlighting, Hines et al. arXiv 2403.14720).
  AST linter (scripts/prompt_envelope_audit.py) gates CI.
- HMAC-signed verdict chain (verdict_vault.py) — every /v1/verify
  response HMAC-SHA256 + SHA-256 chain-linked. verify_chain() re-derived
  independently.
- NO-HEDGING gate (judge_gates.py) — judge hedging auto-flagged.

EU AI Act relevance: Article 14 (human oversight) + Article 15 (accuracy,
robustness, cybersecurity) align with the auditable verdict trail, formal
invariant, and adversarial ensemble. Aug 2 2026 enforcement window makes
the toolkit timely.

Stack: FastAPI/Python 3.11+, React+Vite, Apache-2.0. Live demo BYOK or
5 free calls/IP/day. Cost ceiling $0.50/call.
```

## Field: Demo URL
```
https://www.apohara.dev
```
API health: https://api.apohara.dev/health

## Field: GitHub repo URL(s)
```
https://github.com/SuarezPM/apohara-inti
https://github.com/SuarezPM/Apohara_Context_Forge
https://github.com/SuarezPM/apohara-aegis
```

## Field: Video URL
*(Pablo to record + upload — ~3min: live demo, paper page, AUDIT.md walkthrough)*

## Category tags
```
Agent Bench · Multi-Agent · LLM Security · Formal Methods
Open Source · EU AI Act · Benchmark Reproducibility · Adversarial Validation
```

## Notes specific to Milan audience

- Frame around EU AI Act timeline: Article 14 (human oversight) + Article 15
  (cybersecurity) enforcement Aug 2 2026. Apohara's auditable verdict chain
  + adversarial ensemble + formal invariant maps directly to these articles.
- Avoid the CSAM-adjacent framing of the sister project (Apohara Guard);
  Milan judges and audience are general AI/agent researchers, not T&S
  specialists. Keep the focus on cross-AI verification of code/agent
  outputs.
- Cite the INV-15 paper DOI prominently — European audiences value
  peer-reviewable artifacts; the Zenodo deposit is the cleanest signal
  of "this is real research, not vibes."
- Mention the contrast with single-vendor "agent governance" demos
  (without naming) — the European Commission's own JRC guidance on
  AI agent evaluation explicitly recommends multi-vendor benchmarks.
