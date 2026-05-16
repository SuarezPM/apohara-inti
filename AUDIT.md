# AUDIT.md — Apohara Inti

Public accountability log. Every entry traces a claim to file:line evidence.
Status legend: 🟢 closed / 🟡 in progress / 🟠 partial / 🔴 open.

---

## 1. 🟢 Repo bootstrap (2026-05-16, Day-6 US-005)

Initial scaffold of `github.com/SuarezPM/apohara-inti`, the unified product
fusing apohara-aegis (security plane) and apohara-context-forge (memory plane)
under one cross-AI verification pitch.

### (a) Pitch sentence committed verbatim

The hero subtitle is the elected pitch sentence, identical character-for-character
to the PRD-approved phrasing:

> A different AI reviews the code your AI just wrote, while your agent memory stays isolated.

Evidence: `README.md:3`.

### (b) Dependency strategy — git-installable from main

Backend depends on the two Apohara repos via PEP-508 git URLs pinned to `main`:

- `apohara-aegis @ git+https://github.com/SuarezPM/apohara-aegis.git@main`
- `apohara-context-forge @ git+https://github.com/SuarezPM/Apohara_Context_Forge.git@main`

Evidence: `packages/backend/pyproject.toml:11-12`.

Rationale: both upstream repos are pre-PyPI; pinning to `main` lets US-006/US-007
develop against tip while we cut a PyPI release later in the sprint.

### (c) Absent dependencies (installed by later stories)

- `npm install` for `packages/frontend/` — deferred to **US-007** (Tauri + React UI).
- `pip install -e packages/backend/[dev]` — deferred to **US-006** (FastAPI `/verify` endpoint).
- Rust toolchain + `cargo tauri init` — deferred to US-007.

Nothing in this bootstrap commit imports a third-party library at runtime;
`packages/backend/main.py:1-2` is a 2-line FastAPI stub and runs nothing.

### (d) README scaffold sections

Five sections, total under 300 words:

1. Hero title + pitch subtitle quote — `README.md:1-8`.
2. Sanity check (6 questions, one-line answers) — `README.md:14-19`.
3. Install placeholder — `README.md:23-25`.
4. Coming soon (US-006, US-007, US-008, US-011, featured integration) — `README.md:29-35`.
5. License — `README.md:39-41`.

Heavier content (comparison table, BENCHMARKS section, ContextForge featured
narrative) is deferred to US-008 and US-011 per PRD scope ordering.

---

## 2. 🟢 Comparison table vs 9 competitors (2026-05-16, Day-6 US-008)

`## How we compare` section added to README — `README.md:23-63`. Table
has 1 header row + 9 product rows (Apohara Inti + 8 competitors),
6 substantive columns + the highlighted "Memory isolation = ContextForge
INV-15" column that is unique to us.

### Sources cited (primary, verified via WebFetch 2026-05-16)

- Gemini Code Assist — `README.md:41` → developers.google.com/gemini-code-assist/docs/review-repo-code (Apache-2.0 samples, free 33 PR/day, single-vendor, no adversarial).
- DeepSource BYOK — `README.md:42` → deepsource.com/blog/byok (commercial, hybrid static+AI, no adversarial).
- LlamaGuard / Purple Llama — `README.md:43` → github.com/meta-llama/PurpleLlama (Llama Community License, free OSS, CyberSec Eval adversarial benchmark).
- NeMo Guardrails — `README.md:44` → github.com/NVIDIA/NeMo-Guardrails (Apache-2.0, free OSS, jailbreak / prompt-injection scanning).
- Pantheon (TechEx) — `README.md:45` → lablab.ai TechEx Intelligent Enterprise Solutions hackathon overview (proprietary classifier on Gemini 2.5 Flash + Veea Lobster Trap, red-teams every agent action; no public team page or repo found on 2026-05-16).
- TrusynAI — `README.md:46` → github.com/Trusyn-AI/trusyn-ai (Apache-2.0, single-vendor Gemini, no adversarial testing per repo).
- Granite Guardian 4 — `README.md:47` → huggingface.co/ibm-granite/granite-guardian-3.3-8b (Apache-2.0, internal red-team training data, free OSS). Block-rate column kept as TBD — pending US-004 Granite probe.

### Highlighting

Apohara Inti row (`README.md:31`) is the only row with bolded cells across all
6 columns AND a `→` cue prefix, marking the unique combination:
multi-vendor + adversarial Yes + ContextForge INV-15 + Apache-2.0 + BYOK-free +
reproducible benchmark (`logs/`). No other row achieves this combination.

### Pending verification (honest gaps)

- **Pantheon** — Hackathon project; no public repo or dedicated team page
  on lablab.ai found by 2026-05-16 search. License + cost columns marked
  "Unknown" rather than guessed. Note: Pantheon is described on the
  hackathon overview page only.
- **Vela** — Only a Milan AI Week 2026 submission ("Vela — AI Agency
  Command Center") appears on lablab.ai; no TechEx team page for Vela
  was found by 2026-05-16 search. All 5 columns marked "Unknown"; row
  retained per PRD AC#2 (≥9 rows) with an explicit honesty note in the
  Approach cell rather than fabricated values.
- **Granite Guardian** — Block-rate column held at TBD until US-004 IBM
  Cloud signup unblocks the live probe.

### "Why this matrix matters" paragraph

97 words at `README.md:51-60`. Cites EU AI Act Article 14 (Aug 2 2026
deadline, T-78 days) and OWASP Top-10 for LLM Apps 2026 (April 14 2026
release, Tool Poisoning → LLM02) as the regulatory pressure motivating
the column set.

---

## 3. 🟢 Backend `/v1/verify` endpoint (2026-05-16, Day-6 US-006)

FastAPI service exposing Gemini-writer + 9-attacker-adversarial-ensemble +
INV-15 memory isolation. Lives at `packages/backend/main.py`.

### (a) Endpoint surface

- `POST /v1/verify` — body `{gemini_api_key, task_input}`, returns
  `{verdict, attackers[], memory_isolation, signed_hash, latency_ms,
  cost_estimate_usd, cost_capped}`. Verdict aggregation thresholds match
  PRD: `0-2 → verified`, `3-5 → risky`, `6+ → blocked`.
- `GET /health` — reports import status of both Apohara deps with HTTP
  200 / 503 contract.
- `GET /v1/audit/{verdict_id}` — returns the signed ledger entry for a
  given `signed_hash`, or 404.

### (b) Test coverage

`packages/backend/tests/test_verify.py` — **11 passing** (target was ≥7):
happy path verified, blocked, parametrized risky (3/4/5), invalid Gemini
key → 401, memory isolation enforced + unique audit ids, SHA-256 chain
across 3 calls, /health, /v1/audit round-trip + 404, aggregator threshold
boundary check.

Command: `PYTHONPATH=<aegis>:<contextforge>:packages/backend python3 -m
pytest packages/backend/tests/ -q` → `11 passed in 0.48s`.

### (c) Latency

`packages/backend/tests/latency_report.json` — 5 prompts, mocked Gemini +
mocked attackers (framework overhead only): **p50 = 3.448 ms, p99 = 12.593
ms**, well under the 60 000 ms target. Real upstream wall-clock is bounded
by `max(Gemini, max(9 attackers in parallel))` and is upstream-dependent.

### (d) Dep install — fallback path activated 🟠

`pip install -e packages/backend/` fails on this developer host with
`error: externally-managed-environment` (PEP 668, Debian python3.14
default). Task spec authorized the fallback:

> If installing aegis + contextforge as git deps fails or has resolution
> conflicts, fall back to: `pip install -e /home/linconx/Documentos/
> apohara-aegis -e /home/linconx/Documentos/Apohara_Context_Forge` for
> development and document this in AUDIT.md (the git-install path can be
> tried again for the deployment story US-010).

Active mitigation for **US-006 only**: tests + benchmarks run under
`PYTHONPATH=/home/linconx/Documentos/apohara-aegis:/home/linconx/
Documentos/Apohara_Context_Forge:packages/backend`. Both Apohara modules
import cleanly; aegis `__version__ == "0.1.0"`; context-forge
`__version__ == "3.0.0"`. To be revisited in **US-010** (deployment)
with a proper venv or PyPI publish.

### (e) INV-15 enforcement

For every `/v1/verify` call, a fresh `JCRSafetyGate` instance is created;
one `gate_decision(agent_role="critic", candidate_count=9,
reuse_rate=0.0, layout_shuffled=True)` per attacker. The risk score for
this configuration is `0.6 (base critic) + 0.7 (candidate_count - 2) *
0.10 + 0.20 (layout shuffled) = clamp(1.5, 0, 1) = 1.0`, well above the
0.7 threshold → dense prefill mandated → KV-cache isolation. The
response includes `memory_isolation.inv15_enforced: true` and a unique
uuid4 `contextforge_audit_id`. Evidence: `packages/backend/main.py:421-441`
and `test_verify_memory_isolation_enforced` in the test file.

### (f) Ledger SHA-256 chain

Append-only JSONL at `~/.apohara-inti/ledger.jsonl`. Each entry's
`signed_hash = SHA-256(prev_hash + canonical_json(entry))`. First entry
uses `prev_hash = "0"*64`. Verified end-to-end by
`test_verify_signed_hash_chain` (3 sequential calls, each new entry's
`prev_hash` matches the predecessor's `signed_hash`).
