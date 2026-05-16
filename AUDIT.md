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
