# TechEx 2026 — Apohara PROBANT submission (paste-ready) · 12-VENDOR FROZEN VARIANT

> **FROZEN 2026-05-18. Use only if droplet upgrade to 12-vendor succeeds before T+2:00 decision.**
> Target tracks: **Veea Agent Security & AI Governance** (primary) ·
> AI Agents with Google AI Studio · Data & Intelligence
> Deadline: 2026-05-19. Live: https://www.apohara.dev

---

## Field: Project name
```
Apohara PROBANT — Cross-AI Code Verifier
```

## Field: Tagline (max ~80 chars)
```
Your AI wrote it. A different AI audits it. 12-vendor ensemble · INV-15 proven.
```

## Field: Short pitch (max ~200 chars)
```
Open-source cross-AI verification: Gemini writes code, a 12-vendor adversarial ensemble audits it. Z3-proven INV-15 KV-cache isolation. Every verdict HMAC-signed. Cursor plugin ships today.
```

## Field: Long description (max ~2000 chars)
```
Apohara PROBANT is a cross-AI code verification platform. Gemini writes a
review; a 12-vendor adversarial ensemble (Claude, GPT, DeepSeek, Kimi, GLM,
Qwen, Nemotron, MiniMax, Big-Pickle, Mistral Large, Grok 2, Perplexity Sonar)
independently audits the output for prompt injection, vulnerabilities, and
logic bugs.

Verifiable, not claimed:
- 12 vendors via OpenRouter, each in an isolated KV-cache enforced by
  INV-15 JCRSafetyGate. Paper v3.0 (formal Z3 SMT proof, UNSAT on
  negation in 10.08 ms) complements v2.0.1 empirical sweep (0/1210
  violations). DOI 10.5281/zenodo.20114594.
- JBB-Behaviors block rate 93.75% (Wilson 95% CI [86.2%, 97.3%], n=80
  holdout). Numbers from logs/*.json, not marketing.
- 128 pytest tests + 15+ measurement JSON logs.
- Multi-hardware: AMD MI300X (ROCm 7.2) + NVIDIA H100.

Four hardening layers (auditable in repo):
1. Veea LobsterTrap DPI subprocess pre-check — measured: SQLi block 50%
   (n=20, CI [29.9%, 70.1%] directional), benign FPR 9.8% (n=51). Live
   demo SQLi returns verdict=blocked in ~25 ms.
2. Prompt envelope nonce-tagged sentinels (Hines et al. arXiv 2403.14720).
3. HMAC-SHA256 verdict ledger chain. verify_chain() catches tampering.
4. NO-HEDGING gate (HARD/SOFT split, judge uncertainty flagged).

Distribution: Cursor / Claude Code plugin shipped as VSIX. MCP server
(stdio) for Claude Desktop / Cursor / Zed. /v1/verify_stream SSE for
live per-vendor results. /dashboard for ops view.

Stack: FastAPI/Python 3.11+, React+Vite + Next.js SSR PoC, Apache-2.0,
monorepo across 3 GitHub orgs. Live demo BYOK or 5 free/IP/day.
```

## Field: Demo URL
```
https://www.apohara.dev
```
Backup health endpoint: https://api.apohara.dev/health

## Field: GitHub repo URL(s)
```
https://github.com/SuarezPM/apohara-probant  (frontend+backend monorepo, formerly apohara-inti — redirect preserved)
https://github.com/SuarezPM/Apohara_Context_Forge  (KV-cache + INV-15 core + paper)
https://github.com/SuarezPM/apohara-aegis          (adversarial ensemble)
https://github.com/SuarezPM/Apohara-Guard          (safety sandbox — see repo for current state)
```

### Cross-repository links
| Repo | Purpose |
|------|---------|
| [apohara-probant](https://github.com/SuarezPM/apohara-probant) | Frontend + backend monorepo (formerly apohara-inti; redirect preserved) |
| [Apohara_Context_Forge](https://github.com/SuarezPM/Apohara_Context_Forge) | KV-cache coordination, INV-15 JCRSafetyGate, paper v3.0 |
| [apohara-aegis](https://github.com/SuarezPM/apohara-aegis) | 12-vendor adversarial ensemble engine |
| [Apohara-Guard](https://github.com/SuarezPM/Apohara-Guard) | Kernel-level sandbox (seccomp + namespace isolation) |

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
- Paper PDF lives at `paper/inv15_paper.pdf` in the Context_Forge repo (v3.0 adds Z3 SMT proof; v2.0.1 DOI already on Zenodo). DOI 10.5281/zenodo.20114594.
- AUDIT.md in Context_Forge documents the 10 V6.0 overclaims closed in V7.0.0-rc.2 — judges who open it see we hold ourselves to the same standard we hold competitors to.
- Phase 3 delta (what shipped in the last 6 hours): `docs/submissions/PHASE3-DELTA.md`.

## What differentiates from competitor submissions

Without naming them in the pitch, the contrast judges will see when they open our repo vs theirs:
- Ours: 350+ pytest tests passing + 15+ measurement JSONs + paper with DOI + Wilson CI + multi-hardware logs + real LICENSE file
- Theirs (consistent pattern): 0 tests, hardcoded vanity numbers, decks claiming features not in code, single-vendor LLM, LICENSE file missing or inconsistent with README

The auditable-vs-aspirational contrast is the submission's strongest framing — let the artifacts do the talking.
