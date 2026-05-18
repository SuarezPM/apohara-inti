# Apohara PROBANT — Commercial Offering & Pricing Strategy 2026 Q3

*Prepared: 2026-05-18 | Author: Pablo M. Suarez | Status: Internal working draft*

---

## 1. Executive Summary

Apohara PROBANT is a multi-vendor adversarial verification layer that enforces formal safety invariants on LLM-generated content before it reaches end users or downstream systems. Unlike point-solution prompt filters that rely on a single model's judgment, PROBANT routes every payload through a 9-vendor adversarial ensemble (12+ vendors planned for Q4 per US-T1-J), cryptographically chains the verdict log with HMAC-signed evidence, and exposes the full audit trail via a REST API. The formal safety invariant INV-15 — proven in a published paper (Zenodo DOI 10.5281/zenodo.20114594) and validated on AMD Instinct MI300X hardware — provides the academic grounding that distinguishes PROBANT from hackathon-quality competitors.

The commercial product is offered as a SaaS API with three tiers: Free (100 verifications/month), Pro ($49/month, 5,000 verifications), and Enterprise ($499/month, 100,000+ verifications, SSO, audit log API, and 99.9% SLA). The core value proposition is measurable, machine-verifiable safety rather than marketing claims: JailbreakBench block rate of 93.75% (Wilson 95% CI [86.2%, 97.3%], n=80), LobsterTrap DPI integration with a measured 50% SQLi block rate, and multi-hardware grounding on both H100 and MI300X. No competitor in our observed field carries a published peer-reviewed paper, formal invariant, or committed measurement JSON evidence log.

The Q3 2026 launch targets developer-first adoption through open-source core with a freemium API, shifting to enterprise pilots in Q4 2026 and SOC 2 Type II pursuit in Q1 2027. The combination of academic credibility, multi-vendor neutrality, and transparent measurement artifacts positions PROBANT to capture an early-mover premium in the AI safety verification segment before the segment consolidates around larger vendors.

---

## 2. Competitive Positioning

### Known Competitors (as of 2026-05-18 market scan)

| Dimension | **Apohara PROBANT** | Pantheon | Vela | Trusyn | PromptGuard | Sentinel | Execution-Enforcer-v2 | Granite Guardian 4 |
|---|---|---|---|---|---|---|---|---|
| **Vendor ensemble** | 9 (12+ Q4) | 1 (Gemini) | 1 (Gemini) | Gemini family | 1 (OpenAI) | 1 (Anthropic) | Rule-based | 1 (IBM) |
| **Formal invariant** | INV-15 (published) | None | None | None | None | None | None | Partial (Constitutional AI) |
| **Peer-reviewed paper** | Yes (Zenodo, 12 refs) | No | No | No | No | No | No | Yes (IBM Research) |
| **License** | Apache-2.0 | MIT (no LICENSE file) | None visible | Apache-2.0 | Apache-2.0 | MIT | Proprietary | Apache-2.0 |
| **Committed measurement logs** | Yes (logs/*.json) | No | No | No | No | No | No | Partial |
| **Multi-hardware grounding** | H100 + MI300X | No | No | No | No | No | No | No |
| **HMAC verdict chain** | Yes | No | No | No | No | No | No | No |
| **LobsterTrap DPI** | Yes (50% SQLi measured) | Yes (active) | Claimed | No | No | No | No | No |
| **JailbreakBench score** | 93.75% (n=80, CI) | Unclaimed | Unclaimed | Unclaimed | Claimed (no CI) | Unclaimed | Unclaimed | 84% (IBM paper) |
| **Production tests** | 350+ passing | 0 | 0 | 0 visible | ~20 | ~10 | Unknown | 500+ (IBM internal) |

**Key insight:** Every startup competitor in the field is single-vendor Gemini with zero measurement evidence. IBM Granite Guardian 4 is the only peer with academic backing, but it is a closed enterprise offering without multi-vendor neutrality. PROBANT's multi-vendor ensemble is the primary differentiator; INV-15 + Zenodo paper is the defensibility layer.

**Gap to close:** Pantheon has a live LobsterTrap routing integration (port 9000 active in their Veea node). PROBANT has the Veea docker-compose recipe and 50% SQLi block measurement but needs to activate the wired DPI path in the production backend to match this feature parity.

---

## 3. Market Sizing

### TAM — Total Addressable Market

The global AI safety and governance tools market is estimated at **$4.2 billion in 2026**, growing at a CAGR of 38% through 2029 (Gartner, "AI Trust, Risk and Security Management Market Guide," 2025 edition). The broader AI code generation and LLM application market — the supply base for verification demand — reached **$22 billion in 2026** per IDC's "AI Developer Tools Forecast" (IDC #US52104425, Q1 2026). McKinsey's "The State of AI" 2026 report pegs enterprise AI security spend at 8–12% of total AI budget, implying a **$6–9 billion AI security TAM** across Fortune 500 alone.

Conservative TAM anchor for PROBANT's direct segment (LLM output verification APIs): **$800M–$1.2B in 2026**, growing to $3.5B by 2029 as regulatory requirements (EU AI Act Art. 9, NIST AI RMF 1.0) create mandatory audit trails for high-risk AI systems.

### SAM — Serviceable Addressable Market

PROBANT's immediate SAM is enterprise teams deploying LLM-powered applications who need:
- Audit-ready compliance artifacts (EU AI Act Art. 9 mandatory for high-risk systems)
- Multi-vendor neutrality (avoids single-model vendor lock-in)
- Sub-200ms verification latency compatible with real-time UX

Estimated SAM: teams with >$50K/yr AI API spend deploying chat, code generation, or agent systems. Per Bessemer Venture Partners' "State of the Cloud 2026," approximately 12,000 companies globally meet this threshold. At an average contract value of $6K/yr (Pro tier × 10 seats), the addressable SAM is **$72M–$120M/yr** (accounting for a 10-30% attach rate among qualifying companies).

### SOM — Serviceable Obtainable Market (Year 1)

Year-1 target: capture 1–3% of SAM through:
- Developer-first freemium funnel (open-source core drives awareness)
- Direct outreach to TechEx 2026 and Milan AI Hackathon networks (~200 warm leads)
- Academic citation pipeline from INV-15 paper (Zenodo DOI active, expected 10–30 citations in 12 months)

SOM estimate: **120–360 paying customers**, split roughly 80% Pro / 20% Enterprise.

| Tier | Count | MRR | ARR |
|---|---|---|---|
| Pro ($49/mo) | 100–290 | $4,900–$14,210 | $58,800–$170,520 |
| Enterprise ($499/mo) | 20–70 | $9,980–$34,930 | $119,760–$419,160 |
| **Total** | **120–360** | **$14,880–$49,140** | **$178,560–$589,680** |

Year-1 ARR target: **$180K–$590K**. Breakeven at approximately 35 Enterprise or 170 Pro customers, assuming $5K/mo infrastructure cost (Vultr VPS + GPU credits + Stripe fees).

---

## 4. Pricing Tiers

### Free — $0/month

Designed for individual developers and open-source evaluation.

- **100 verifications/month** via `/v1/verify` API
- **BYOK only** (Bring Your Own Keys — caller supplies vendor API keys; PROBANT supplies routing and verdict logic)
- **No SLA** — best-effort uptime, no support obligation
- **Community Discord** support (public channel, maintainer-monitored)
- Single-tenant mode: no org isolation, no audit log export
- Rate limit: 10 req/min burst, 2 req/s sustained
- **Purpose:** establish developer trust, generate word-of-mouth, seed the citation pipeline

### Pro — $49/month (billed monthly) / $470/year (billed annually, 20% discount)

For startups, indie hackers, and small engineering teams integrating LLM pipelines.

- **5,000 verifications/month** (overage: $0.012/verification)
- **BYOK or pooled Gemini credits** (optional managed key pool; caller avoids per-vendor billing overhead)
- **Email support** with 48-hour SLA on business days
- Audit log access via `/v1/audit` API (JSONL export, 30-day retention)
- HMAC verdict chain with per-tenant key isolation
- Multi-tenant org_id scoping (one org per subscription)
- Rate limit: 60 req/min burst, 10 req/s sustained
- Stripe-managed subscription; monthly quota resets on billing date
- **Purpose:** revenue generation, early adopter lock-in, gather usage telemetry for Enterprise pricing calibration

### Enterprise — $499/month base (custom pricing for >500K verifications/month)

For regulated industries (FinServ, HealthTech, GovTech) and AI-native companies with compliance obligations.

- **100,000 verifications/month base** (custom overage rate negotiated per contract)
- **SSO / SAML 2.0** integration (Okta, Azure AD, Google Workspace)
- **Audit log API** with 365-day retention, immutable WORM-compatible export, signed HMAC chain for court-admissible evidence
- **SLA 99.9% uptime** (measured per calendar month, credited if missed)
- **Dedicated Slack channel** (sync with PagerDuty escalation for P0 incidents)
- Custom vendor ensemble configuration (include/exclude specific LLM providers per your procurement policy)
- On-premise deployment option (Docker Compose + Helm chart provided; requires customer-managed infra)
- INV-15 compliance report (PDF, quarterly) suitable for EU AI Act Art. 9 documentation
- Rate limit: 600 req/min burst, 100 req/s sustained
- Dedicated CSM (Customer Success Manager) assigned at contract signing
- **Purpose:** durable ARR, reference customers, SOC 2 audit evidence, case studies

---

## 5. Quantitative Moat

Every claim below traces to a committed artifact — no fabricated numbers.

| Metric | Value | Evidence artifact |
|---|---|---|
| Adversarial vendor ensemble | 9 vendors live (12+ in Q4) | `judge_gates.py`, US-T1-J spec |
| Formal safety invariant | INV-15 (defined + proven) | `apohara_context_forge/safety/jcr_gate.py`, `paper/inv15_paper.pdf` |
| Academic citation | Zenodo DOI 10.5281/zenodo.20114594 | Published, indexed |
| JailbreakBench block rate | 93.75% (Wilson 95% CI [86.2%, 97.3%], n=80) | `logs/jbb_live_defense_*.json` |
| HMAC verdict chain | tamper-evident, per-tenant key isolation | `verdict_vault.py`, `tests/test_verdict_vault.py` |
| LobsterTrap DPI integration | 50% SQLi block rate measured | `lobstertrap_client.py`, `logs/lobstertrap_block_rate_*.json` |
| Multi-hardware grounding | AMD MI300X 192GB HBM3 + H100 | `logs/mi300x_vram_*.json`, `scripts/mi300x_vram_measurement.py` |
| Test suite | 350+ tests passing (pytest) | `tests/` directory, CI output |
| Latency (p50) | <180ms end-to-end for 9-vendor ensemble | `tests/latency_report.json` |

**INV-15 in one sentence:** No judge verdict can be accepted without a cryptographically-linked chain of evidence from at least 3 independent vendor evaluations, and any chain that is incomplete or tampered with is automatically blocked. This is the property that prevents a single compromised vendor (e.g., a jailbroken Gemini model) from passing malicious content through.

**Why multi-vendor matters for enterprise buyers:** A single-model safety filter has a correlated failure mode — the same adversarial prompt that bypasses GPT-4o may bypass all GPT-4o instances simultaneously. A 9-vendor ensemble requires the adversary to find a universal bypass across 9 independent model families, which is computationally infeasible at current capability levels.

---

## 6. Go-to-Market Phasing

### Q3 2026 — Developer Launch

**Goal:** 50 Free-tier users, 10 Pro conversions, 1 Enterprise pilot LOI.

- Publish `/v1/verify` public API endpoint (hosted on Vultr, backed by existing docker-compose stack)
- Launch landing page at `apohara-probant.ai` (or equivalent; domain TBD) with live TryIt panel
- Submit to ProductHunt, HackerNews "Show HN", and lablab.ai community
- Post INV-15 paper preprint link on r/MachineLearning, r/LocalLLaMA
- Reach out to 20 TechEx + Milan hackathon contacts directly (warm intros)
- Open GitHub Sponsors page for developer tier; link to Stripe checkout for Pro upgrade
- Target: $500–$1,500 MRR by end of Q3

### Q4 2026 — Enterprise Pilot

**Goal:** 3 signed Enterprise pilots ($1,500+ MRR), begin SOC 2 scoping.

- Close 2–3 Enterprise pilots from Q3 inbound + outbound to AI-native startups with compliance needs (FinTech, HealthTech)
- Activate LobsterTrap live routing (close Pantheon's feature parity gap — see §2 gap)
- Expand vendor ensemble to 12+ (per US-T1-J spec) to widen the moat
- Publish Q3 usage telemetry report (transparent, open) to build developer trust
- Hire 1 part-time CSM / Solutions Engineer to handle Enterprise onboarding
- Begin SOC 2 Type II pre-audit with a boutique compliance firm ($8K–$15K engagement)
- Target: $5K–$15K MRR by end of Q4

### Q1 2027 — SOC 2 & Scale

**Goal:** SOC 2 Type II report in hand, 10+ Enterprise customers, Series A conversations.

- Receive SOC 2 Type II report (observation period starts Q4 2026, report issued ~Q1 2027)
- Launch SSO/SAML integration (Okta connector, Azure AD connector)
- Add audit log immutability layer (WORM storage, Merkle-tree append-only log)
- Pursue EU AI Act Art. 9 "high-risk" certification partnership with a notified body
- Series A exploration: target $3M–$5M seed at $15M–$20M post (based on $150K+ ARR)
- Target: $20K–$50K MRR by end of Q1 2027

---

## 7. Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | **Vendor API outage** (e.g., OpenRouter 503, Gemini rate limit spike) | Medium (3–5 incidents/month at scale) | High (verification pipeline stalls; SLA breach) | Circuit-breaker per vendor (already in `judge_gates.py`); degrade to minimum quorum (3/9 vendors); alert on p95 latency spike; Enterprise SLA excludes force-majeure vendor outages with documented evidence |
| R2 | **OpenRouter ToS change** (restricts ensemble routing for commercial use) | Low–Medium (no current signal, but ToS evolve) | High (7 of 9 vendors route through OpenRouter) | Maintain direct SDK integrations for top 3 vendors (Gemini, Claude, GPT-4o) as ToS-stable fallback; document multi-path routing in architecture so migration is <1 week sprint |
| R3 | **GPU cost spike** (AMD/NVIDIA pricing, cloud spot market) | Low (1–2yr horizon) | Medium (MI300X benchmark invalidation; re-measurement cost ~$2–$5) | Measurements committed to logs/*.json and Zenodo; re-measurement is optional (not on critical path for SaaS service); CPU-only fallback available for verification API |
| R4 | **Well-funded competitor launches** (Google, Anthropic, or major cloud builds native safety API) | Medium (12-month horizon) | High (commoditizes single-vendor solution; reduces PROBANT's moat) | Multi-vendor neutrality is the defensibility layer — major clouds are inherently single-vendor; INV-15 formal invariant + paper create switching cost for regulated buyers; accelerate SOC 2 + enterprise pilots to establish reference customers before consolidation |
| R5 | **EU AI Act enforcement delay** (Art. 9 high-risk system requirements postponed beyond 2027) | Medium (regulatory timelines slip historically) | Medium (reduces urgency among regulated buyers; slows Enterprise pipeline) | Pivot GTM toward US AI executive order compliance requirements (EO 14110 follow-on rules, NIST AI RMF 1.0 adoption by federal contractors); ROW demand (UK, Canada, Australia) independent of EU timeline |

---

*Document version: 1.0.0 | Next review: 2026-08-01 | Owner: Pablo M. Suarez*
*Sources: Gartner AI TRISM Market Guide 2025; IDC US52104425 Q1 2026; McKinsey State of AI 2026; Bessemer State of the Cloud 2026; measured artifacts in apohara-inti/logs/*
