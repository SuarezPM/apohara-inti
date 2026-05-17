# Apohara Inti

> A different AI reviews the code your AI just wrote, while your agent memory stays isolated.

Open-source defense-in-depth for AI-generated code. Gemini writes and audits the
code, then 9 frontier vendors adversarially attack the output before merge,
while [Apohara ContextForge](https://github.com/SuarezPM/Apohara_Context_Forge)
enforces `INV-15` memory isolation between the writer agent and every attacker.

---

## Try it live

**Live demo (TechEx 2026 judging window, May 14 – May 26):**
[https://149.28.56.91.nip.io/](https://149.28.56.91.nip.io/)

Two zero-friction entry paths:

- **Try with demo key** (no signup): click the "Try with demo key" button under the API-key field. Uses a server-side Gemini key shared across visitors, rate-limited to **5 calls per IP per UTC day**. Returns 429 with the next reset timestamp when you hit the cap.
- **Bring your own Gemini key** (BYOK): paste your key — we never store it. Get one at [aistudio.google.com/apikey](https://aistudio.google.com/apikey); the free tier covers hundreds of verifications.

Either path runs the same pipeline: 9-vendor adversarial attackers (Claude Opus 4.7, GPT-5.5, DeepSeek V4 Pro, MiniMax M2.7, Kimi K2.6, GLM 5.1, Qwen 3.6 Plus, Nemotron 3 Super 120B, Big Pickle) on our shared credit pool, INV-15 memory isolation enforced, SHA-256-signed verdict ledger.

The demo URL uses [nip.io](https://nip.io) wildcard DNS pointing at
our Vultr droplet (`149.28.56.91`), with Caddy auto-issued TLS via
Let's Encrypt. We did NOT register `apohara-inti.dev`; if/when we do,
this section will get the prettier URL.

Backend health probe: `curl -sf https://149.28.56.91.nip.io/health`.

---

## Milan AI Week — multi-agent inference angle

The same stack also answers the **AI Agent Olympics** theme (Milan AI
Week 2026, prize $28K+, deadline 2026-05-20): ContextForge is the
multi-agent KV-cache registry foundation that lets 5+ agents share a
RAG prefix without leaking KV state between writer and critic. The
Milan benchmark (`logs/milan_5agent_benchmark_1778943206.json` in the
[sister repo](https://github.com/SuarezPM/Apohara_Context_Forge))
reports **76% HBM saved per the closed-form model (CPU-mock fallback,
H100 deferred)** — full honesty disclosure in the JSON `honesty_note`.
13-page paper preprint at [`papers/inv15_v2.pdf`](https://github.com/SuarezPM/Apohara_Context_Forge/blob/main/papers/inv15_v2.pdf).

---

## Sanity check

- **What is it?** — Cross-AI code reviewer where Gemini writes/audits and 9 frontier vendors adversarially attack the output before merge.
- **For whom?** — Engineering teams using AI-assisted code generation (Cursor, Claude Code, Cline, Copilot) who need pre-merge verification.
- **Why now?** — EU AI Act Article 14 fully applicable 2026-08-02 (78 days); OWASP LLM 2026 elevated Tool Poisoning to LLM02.
- **What does it replace?** — Single-AI self-review (Cursor /best-of-n is same-model parallel, not cross-vendor) and trust-the-LLM-output workflows.
- **Cost to use?** — Free OSS Apache-2.0; user provides 1 Gemini API key (BYOK); 9 attackers run on Apohara's pre-funded credit pool.
- **Next step after install?** — `apohara verify <github-pr-url>` returns signed JSON `verdict: verified|risky|blocked` with INV-15-verified ContextForge audit id.

---

## How we compare

A scan of the May 2026 LLM-safety / cross-AI-review space. Each column is
sourced from a primary reference (links below). Where a column cannot be
confirmed from public material, we say so explicitly rather than guess.

| Product | Approach | Adversarial testing | Memory isolation | License | User cost | Reproducible benchmark |
|---|---|---|---|---|---|---|
| **Apohara Inti** (us) → | **multi-vendor consensus** | **Yes** | **ContextForge INV-15** | **Apache-2.0** | **free with BYOK** | **Yes (see `logs/`)** |
| Gemini Code Assist [^1] | single-vendor LLM | No | none | proprietary | free (33 PR/day) + paid enterprise | No |
| DeepSource BYOK AI Review [^2] | hybrid static + AI | No | none | commercial | paid enterprise (BYOK) | No |
| LlamaGuard / Purple Llama [^3] | safety classifier (single-vendor) | Yes (CyberSec Eval) | none | Llama Community License | free OSS | Partial (CyberSec Eval public) |
| NeMo Guardrails [^4] | guardrail framework | Yes (jailbreak scan) | none | Apache-2.0 | free OSS | Partial (eval tool, no public log) |
| Pantheon (TechEx) [^5] | proprietary classifier (Gemini + Lobster Trap) | Yes (red-teams every action) | Aegis-style runtime SOC | Unknown (hackathon, no public repo) | Unknown | No |
| TrusynAI [^6] | single-vendor LLM (Gemini) | No | none | Apache-2.0 | Unknown | No |
| Vela (TechEx) | Unknown (no TechEx team page found; only Milan AI Week submission cited) | Unknown | Unknown | Unknown | Unknown | Unknown |
| Granite Guardian 4 [^7] | safety classifier (single-vendor) | Yes (internal red-team) | none | Apache-2.0 | free OSS (Lite plan) | Yes — `ibm/granite-4-h-small` on **same JBB-Behaviors n=80 holdout we use**: **79/80 = 98.75%, Wilson [93.3%, 99.8%], p50=522ms** ([log][gg4-log]) |

[^1]: <https://developers.google.com/gemini-code-assist/docs/review-repo-code>
[^2]: <https://deepsource.com/blog/byok>
[^3]: <https://github.com/meta-llama/PurpleLlama>
[^4]: <https://github.com/NVIDIA/NeMo-Guardrails>
[^5]: <https://lablab.ai/ai-hackathons/techex-intelligent-enterprise-solutions-hackathon>
[^6]: <https://github.com/Trusyn-AI/trusyn-ai>
[^7]: <https://huggingface.co/ibm-granite/granite-guardian-3.3-8b>
[gg4-log]: https://github.com/SuarezPM/apohara-aegis/blob/main/logs/granite4_jbb_n80_20260516T164541Z.json

### Honest note on the Granite Guardian 4 result

Granite Guardian 4 (`ibm/granite-4-h-small`) hits **98.75%** on the same
n=80 JBB-Behaviors holdout where the Apohara ensemble hits **93.75%** — and
it is **~19× faster** (p50 522 ms vs 10063 ms). On *prompt-level safety
classification*, a purpose-built classifier from IBM beats a 9-vendor
adversarial ensemble. We measured it, we are not hiding the number, and
the [log][gg4-log] is committed to the public repo.

That said, Apohara Inti solves a different problem: **adversarial review
of generated code with memory isolation**. Granite-4 cannot simulate nine
different attacker perspectives reviewing the same patch (it is one model),
it cannot enforce INV-15 KV-cache isolation (no such surface exists in
watsonx today), and it is a single point of failure for both availability
(watsonx outage = no review) and false-negative blind spots (one
vendor's training data gaps = one shared blind spot). The matrix is
**not** "who scores highest on JBB-Behaviors" — it is "who covers all six
columns simultaneously" — and Granite still has `none` for memory
isolation and `Yes (internal red-team)` for adversarial testing of code
(not of prompts).

### Why this matrix matters

No other product in the table combines all six: multi-vendor consensus,
adversarial testing, INV-15 memory isolation, open license, BYOK-free user
cost, and a reproducible benchmark log. Single-vendor reviewers cannot
catch their own blind spots, safety classifiers do not vet code semantics,
and the closest hackathon peers either lack memory isolation or are
proprietary. Regulatory pressure makes this gap urgent: [EU AI Act
Article 14][8] (human-oversight obligation) becomes fully applicable on
2026-08-02 (78 days), and [OWASP Top-10 for LLM Apps 2026][9] (released
2026-04-14) elevated **Tool Poisoning to LLM02** — precisely the surface
Apohara Inti's cross-vendor attacker ensemble targets.

[8]: https://artificialintelligenceact.eu/article/14/
[9]: https://owasp.org/www-project-top-10-for-large-language-model-applications/

---

## Deploy to TerraFabric

Run the full Apohara Inti stack behind Veea's Lobster Trap DPI proxy with one
command. The recipe brings up four services on a shared docker network:
Lobster Trap as the ingress DPI, the FastAPI backend, the ContextForge MCP
sidecar, and a mock VeeaONE control plane stub.

```bash
cd deploy && docker-compose up -d --build
```

This is the integration pattern for production [Veea TerraFabric][tf-mwc]
deployments — the local VeeaONE stub will be swapped for the real control
plane client once you have TerraFabric API credentials. See
[`deploy/terrafabric-stack.md`](deploy/terrafabric-stack.md) for the detailed
recipe (architecture diagram, required env vars, smoke test, image registry
notes).

[tf-mwc]: https://aithority.com/machine-learning/veea-launches-terrafabric-paving-the-way-to-operate-ai-and-autonomous-systems-at-the-edge/

### Request-path DPI (active LobsterTrap routing)

When `LOBSTERTRAP_URL` is set on the backend, every `POST /v1/verify`
request triggers an inline DPI pre-check against the Lobster Trap proxy
**before** Gemini is invoked. Three outcomes:

| Lobster Trap response | Backend behavior |
|---|---|
| Allow (2xx) | Continues to Gemini writer + 9-attacker pass; ledger entry records `dpi_check.source = "lobstertrap"` for the audit trail |
| Deny (403 or `id="lobstertrap-deny"` in body) | Short-circuits to `verdict="blocked"` with `attackers=[]`, `cost_estimate_usd=0`, INV-15 still enforced, ledger entry records the deny reason |
| Unreachable (timeout / connect error) | Fail-open: continues current flow; ledger entry records `dpi_check.source = "unreachable-fallback"` (the 9-vendor ensemble is the primary safety layer, Lobster Trap is a fast perimeter pre-filter) |

When `LOBSTERTRAP_URL` is unset, the pre-check returns
`source="disabled"` without any HTTP call — zero overhead, identical
behavior to versions without DPI wiring. The `docker-compose` stack
in [`deploy/docker-compose.yml`](deploy/docker-compose.yml) wires this
env var automatically for the `aegis-backend` service.

---

## Powered by Apohara Context Forge

Apohara Inti's memory plane runs on
[**Apohara Context Forge**](https://github.com/SuarezPM/Apohara_Context_Forge),
the only open-source multi-agent KV-cache registry for vLLM that ships
with a formal safety invariant — `INV-15` — enforced at every judge
call. ContextForge is a distinct upstream project (Apache-2.0,
hardware-validated on AMD Instinct MI300X, V7.0.0-rc.2); Inti imports
it as a git dependency, not as a vendored copy.

**What it does.** ContextForge is a KV-cache coordination layer for
vLLM. It gives each agent in a multi-agent pipeline an isolated
KV-cache state, then proves the isolation held with a signed audit
trail. The `JCRSafetyGate` (Judge–Critic–Responder gate) is the
runtime entry point: every attacker invocation in Inti's `/v1/verify`
pipeline calls it once with `role="critic"`, and the gate's decision —
plus a UUID-format audit id — is attached to the verdict JSON before
it is signed into the SHA-256 ledger.

**Why memory isolation matters here.** Inti spins up nine adversarial
attacker agents against every Gemini-written review. Without
isolation, a poisoned attacker prompt could mutate the writer's
KV-cache state and propagate to subsequent calls — a class of
indirect prompt-injection attack. **INV-15 mathematically guarantees
that judge agents cannot reuse KV-cache state derived from candidate
agents, preventing a class of indirect prompt injection attacks.**

**Read more.**

- [View the Apohara Context Forge repo](https://github.com/SuarezPM/Apohara_Context_Forge)
- [Read the INV-15 paper (Zenodo DOI 10.5281/zenodo.20114594)](https://doi.org/10.5281/zenodo.20114594)

---

## Install

Coming in US-006 / US-007. Not yet installable.

---

## Coming soon

- **US-006** — FastAPI backend with `/verify` endpoint, Gemini writer, 9-vendor attacker ensemble.
- **US-007** — Tauri + React desktop client with PR-URL verification UI.
- **US-008** — Side-by-side comparison vs Cursor /best-of-n, GitHub Copilot Reviews, and trust-only workflows.
- **US-011** — BENCHMARKS.md grounded in `logs/` evidence files.
- **Featured integration** — Apohara ContextForge audit ids on every verdict, surfacing INV-15 memory isolation between Gemini-writer and the 9 attackers.

---

## License

Apache-2.0. See [LICENSE](LICENSE).
