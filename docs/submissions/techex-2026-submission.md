# TechEx 2026 — Apohara Inti submission (paste-ready)

> Target tracks: **Veea Agent Security & AI Governance** (primary) ·
> AI Agents with Google AI Studio · Data & Intelligence
> Deadline: 2026-05-19. Live: https://www.apohara.dev

---

## Field: Project name
```
Apohara Inti — Cross-AI Code Verifier
```

## Field: Tagline (max ~80 chars)
```
A different AI audits the code your AI just wrote. 9-vendor ensemble · INV-15 isolated.
```

## Field: Short pitch (max ~200 chars)
```
Open-source cross-AI verification: Gemini writes code, a 9-vendor adversarial ensemble (Claude+GPT+DeepSeek+Kimi+GLM+Qwen+Nemotron+MiniMax+Big-Pickle) audits it. Formal INV-15 KV-cache isolation. Every verdict HMAC-signed.
```

## Field: Long description (max ~2000 chars)
```
Apohara Inti is a cross-AI code verification platform. Gemini writes a
review; a 9-vendor adversarial ensemble (Claude, GPT, DeepSeek, Kimi, GLM,
Qwen, Nemotron, MiniMax, Big-Pickle) independently audits the output for
prompt injection, vulnerabilities, and logic bugs.

Verifiable, not claimed:
- 9 vendors via OpenRouter, each in an isolated KV-cache enforced by the
  INV-15 JCRSafetyGate formal invariant (paper DOI
  10.5281/zenodo.20114594, 0/1210 violations in exhaustive sweep).
- JBB-Behaviors block rate 93.75% (Wilson 95% CI [86.2%, 97.3%], n=80
  holdout). Numbers from logs/*.json in repo, not marketing.
- 350+ pytest tests + 15+ measurement JSON logs as evidence layer.
- Multi-hardware: AMD MI300X (ROCm 7.2) + NVIDIA H100.

Three hardening layers shipped this sprint (auditable in repo):
1. Prompt envelope (envelope.py) — untrusted blocks wrapped in per-call
   nonce-tagged sentinels (Hines et al. arXiv 2403.14720 Spotlighting).
   Tag-forgery injection cannot break framing. AST linter
   (scripts/prompt_envelope_audit.py) gates CI on raw f-string use of
   untrusted attrs.
2. HMAC-signed verdict chain (verdict_vault.py) — every /v1/verify
   response carries HMAC-SHA256 + SHA-256 chain link. verify_chain()
   detects payload tamper, signature tamper, key rotation.
3. NO-HEDGING gate (judge_gates.py) — judge hedging (might/maybe/...)
   auto-annotated [HEDGED:word] so operators see uncertainty surfaced.

Stack: FastAPI/Python 3.11+, React+Vite, Apache-2.0, monorepo across
three GitHub orgs. Live demo accepts BYOK Gemini or 5 free calls/IP/day.
Cost ceiling $0.50/call, p50 latency ~30s for 9-vendor pass.
```

## Field: Demo URL
```
https://www.apohara.dev
```
Backup health endpoint: https://api.apohara.dev/health

## Field: GitHub repo URL(s)
```
https://github.com/SuarezPM/apohara-inti           (frontend+backend monorepo)
https://github.com/SuarezPM/Apohara_Context_Forge  (KV-cache + INV-15 core + paper)
https://github.com/SuarezPM/apohara-aegis          (9-vendor adversarial ensemble)
```

## Field: Video URL
*(Pablo to record + upload — ~3min: live demo + repo tour + paper page)*

## Category tags (for lablab.ai)
```
Agent Security & AI Governance · Veea
Generative AI Studio
AI Agents with Google AI Studio
Data & Intelligence
LLM Security
Open Source
```

## Notes for the submission form
- Use the Apache-2.0 license badge in the screenshot grid (we have a real LICENSE file).
- Direct judges to `logs/baseline_aegis-ensemble-10frontier_day5_FALLBACK_20260515T212737Z.json` for the JBB block-rate evidence (commit hash `c9dc9ac` corrected the citation).
- Paper PDF lives at `paper/inv15_paper.pdf` in the Context_Forge repo (v2.0.1).
- AUDIT.md in Context_Forge documents the 10 V6.0 overclaims that were closed in V7.0.0-rc.2 — judges who open it see we hold ourselves to the same standard we hold competitors to.

## What differentiates from competitor submissions (Pantheon, Vela, Trusyn, PromptGuard, Sentinel, Execution-Enforcer-v2)

Without naming them in the pitch, the contrast judges will see when they open our repo vs theirs:
- Ours: 350+ pytest tests passing + 15+ measurement JSONs + paper with DOI + Wilson CI + multi-hardware logs + real LICENSE file
- Theirs (consistent pattern): 0 tests, hardcoded vanity numbers, decks claiming features not in code, single-vendor LLM, LICENSE file missing or inconsistent with README

The auditable-vs-aspirational contrast is the submission's strongest framing — let the artifacts do the talking.
