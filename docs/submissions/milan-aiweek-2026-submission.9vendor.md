# Milan AI Week 2026 — Apohara PROBANT submission (paste-ready) · 9-VENDOR STAGED VARIANT

> **PRIMARY VARIANT (2026-05-18). Use when droplet upgrade has not yet landed at submission time.**
> 12-vendor expansion is complete in apohara-aegis main, staged for next deploy cycle.
> Target track: **Agent Bench** (primary, agentic benchmarking + governance)
> Deadline: 2026-05-20. Live: https://www.apohara.dev

---

## Field: Project name
```
Apohara PROBANT — Cross-AI Code Verifier
```

## Field: Tagline (max ~80 chars)
```
Cross-AI verification with Z3-proven KV-cache isolation. EU AI Act ready.
```

## Field: Short pitch (max ~200 chars)
```
9 frontier LLMs adversarially audit AI-generated code in isolated KV-caches. INV-15 Z3-proven. Tamper-evident verdict chain. Apache-2.0. EU AI Act Article 14 ready.
```

## Field: Long description (max ~2000 chars)
```
Apohara PROBANT is a reproducible benchmark + production tool for adversarial
auditing of AI-generated code. Gemini writes a review; 9 frontier vendors
(Claude, GPT, DeepSeek, Kimi, GLM, Qwen, Nemotron, MiniMax, Big-Pickle)
independently judge it. Aggregation: 0-2 harmful = verified · 3-5 = risky
· 6+ = blocked. Transparent rule, no black box.

12-vendor expansion (Mistral Large, Grok 2, Perplexity Sonar) is complete
in apohara-aegis main, staged for the next production deploy cycle.

Reproducibility:
- 128 pytest tests + 15+ measurement JSONs in /logs/.
- JBB-Behaviors block rate 93.75% (Wilson 95% CI [86.2%, 97.3%], n=80
  holdout). Auditable methodology; numbers not hand-picked.
- Multi-hardware: AMD MI300X (ROCm 7.2) + NVIDIA H100.
- Honesty CI guard blocks hardcoded benchmark values in production code.

Formal safety:
- INV-15 JCRSafetyGate: formal invariant for multi-agent KV-cache
  isolation (DOI 10.5281/zenodo.20114594). Paper v3.0 adds Z3 SMT
  proof: negation of INV-15 is UNSAT in 10.08 ms. Empirical sweep:
  0/1210 violations. Judges never contaminate the writer's memory.

Defenses (four layers, all auditable):
- Veea LobsterTrap DPI subprocess pre-check: SQLi blocked before reaching
  Gemini. Measured: 50% SQLi block (n=20, Wilson CI [29.9%,70.1%]
  directional), 9.8% benign FPR (n=51). logs/lobstertrap_block_rate_*.json.
- Prompt envelope (envelope.py) — nonce-tagged Spotlighting (Hines et
  al. arXiv 2403.14720) + AST linter CI gate.
- HMAC-signed verdict chain (verdict_vault.py) — verify_chain() detects
  any tamper.
- NO-HEDGING gate (judge_gates.py) — judge hedging auto-flagged.

Distribution: Cursor VSIX, MCP server (stdio), SSE /v1/verify_stream, /dashboard.

EU AI Act: Article 14 (human oversight) + Article 15 (cybersecurity).
Aug 2 2026 enforcement. SOC2 + ISO 27001 control-mapping in docs/compliance/.

Stack: FastAPI/Python 3.11+, React+Vite, Apache-2.0. BYOK or 5 free/IP/day.
```

## Field: Demo URL
```
https://www.apohara.dev
```
API health: https://api.apohara.dev/health

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
| [apohara-aegis](https://github.com/SuarezPM/apohara-aegis) | 9-vendor adversarial ensemble (12-vendor staged in main, next deploy) |
| [Apohara-Guard](https://github.com/SuarezPM/Apohara-Guard) | Kernel-level sandbox (seccomp + namespace isolation) |

## Field: Video URL
*(Pablo to record + upload — ~3min: live demo, paper page, AUDIT.md walkthrough)*

## Category tags
```
Agent Bench · Multi-Agent · LLM Security · Formal Methods
Open Source · EU AI Act · Benchmark Reproducibility · Adversarial Validation
```

## Notes for the submission form
- Phase 3 delta (what shipped in the last 6 hours): `docs/submissions/PHASE3-DELTA.md`.
- Paper v3.0 Z3 proof is the strongest differentiator for the European academic audience — lead with it in any oral pitch.
- SOC2 / ISO 27001 mapping docs at `docs/compliance/` are the enterprise procurement hook.
- Paper PDF: `paper/inv15_paper.pdf` in Context_Forge repo. DOI 10.5281/zenodo.20114594.

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
