# YC Summer 2026 Application — Apohara PROBANT

> Draft for internal review. All claims grounded in committed artifacts.
> Sources cited inline. Do not submit without founder sign-off on every
> metric citation and traction section.

---

## Standard YC Application Questions

---

### 1. Company name

**Apohara PROBANT**

_(The product is PROBANT — cross-AI adversarial code verification. The
parent project is Apohara. The underlying memory-isolation layer is
Apohara ContextForge. All three share the Apache-2.0 license.)_

---

### 2. URL

**https://www.apohara.dev**

Live demo (no signup required): https://149.28.56.91.nip.io/

GitHub repos:
- PROBANT (backend + frontend): https://github.com/SuarezPM/apohara-inti
- Aegis (9-vendor adversarial ensemble): https://github.com/SuarezPM/apohara-aegis
- ContextForge (KV-cache memory plane + INV-15): https://github.com/SuarezPM/Apohara_Context_Forge

Paper (ContextForge + INV-15 formal proof): DOI 10.5281/zenodo.20114594

---

### 3. Who writes code

**Pablo M. Suarez** — solo founder, all code. UNT Argentina (Universidad Nacional
de Tucumán), Computer Science. Five years of production backend engineering
(Python, Go, distributed systems). Recent focus: LLM security, formal safety
invariants, multi-agent KV-cache architectures.

Relevant technical background for this product:
- Built the INV-15 formal invariant from scratch and proved it in the paper
  (DOI 10.5281/zenodo.20114594, v2.0.1, 12 references, MI300X-grounded).
- Ported Apohara Guard's TypeScript EvidenceVault (HMAC-signed SHA-256 chain)
  to Python in a single sprint day, with full test coverage.
- Ran GPU benchmarks on AMD Instinct MI300X (192 GB HBM3, ROCm 7.2.0) and
  NVIDIA H100 to ground every performance claim in hardware measurement.
- Wrote 350+ pytest tests across three repos in seven days.

Currently seeking a co-founder with GTM / enterprise sales background.
The technical foundation is solid; the go-to-market motion needs a second
person with a different skill set.

---

### 4. What does your company do? (single sentence)

Apohara PROBANT lets a second AI from a different vendor review the code
your first AI just wrote, while cryptographically proving neither can
read the other's memory.

---

### 5. Where is your company based?

San Miguel de Tucumán, Argentina. The founder is open to relocating for
YC residency (Mountain View / San Francisco). Remote-first engineering
is the operating model.

---

### 6. How long have founders known each other?

Single founder.

---

### 7. Have you applied to YC before?

No.

---

### 8. How did you hear about YC?

Through the broader startup community and the YC application archive.
The application structure (concise answers, traction focus, "why now")
is well-documented; this draft follows the W26 format.

---

### 9. What's the product?

Apohara PROBANT is a cross-AI code verification service. A developer
submits code to the API. Gemini (the writer) reviews and rewrites it.
Nine frontier LLMs from nine different vendors — Claude Opus 4.7, GPT-5.5,
DeepSeek V4 Pro, MiniMax M2.7, Kimi K2.6, GLM 5.1, Qwen 3.6 Plus,
Nemotron 3 Super 120B, Big Pickle — adversarially attack Gemini's output
in parallel. The verdict aggregation rule is deterministic: 0–2 attackers
finding an issue → verified; 3–5 → risky (human review); 6+ → blocked.

Every verdict is written to an append-only HMAC-SHA256-signed ledger.
The SHA-256 chain links each entry to the previous one. Any auditor can
re-derive the chain and detect payload tampering, signature tampering, or
key rotation — without trusting the operator.

Memory isolation between the writer and all attackers is enforced by INV-15,
a formal safety invariant implemented in `apohara_context_forge.safety.jcr_gate`
and proven in the companion paper. This prevents a compromised attacker from
poisoning the writer's KV-cache context — an attack class that has no
structural defense in any competing product.

The product also includes LobsterTrap DPI pre-screening (deep-packet
inspection of inbound prompts for SQL injection and prompt-injection
patterns) and a NO-HEDGING gate on attacker outputs (hedge words like
"maybe" or "possibly" in a security verdict are flagged, because a hedged
verdict signals model uncertainty that the operator should see explicitly).

Live demo: https://149.28.56.91.nip.io/ — no signup, try-with-demo-key
button available. Returns a full JSON verdict with attacker breakdown,
HMAC signature, and ledger `signed_hash`.

---

### 10. Who are your customers / who will use this?

**Primary:** Engineering teams at companies using AI coding assistants
(Cursor, Copilot, Gemini Code Assist) who need to verify AI output before
it reaches production. The threat model is: AI-generated code with a
prompt-injection vector, a logic bug not visible to a single-vendor reviewer,
or a dependency chain that contains adversarial content.

**Secondary:** Enterprise security teams that need an auditable chain-of-custody
trail for every AI-assisted code change. The HMAC-signed ledger + SHA-256 chain
satisfies audit requirements that unlogged AI review cannot.

**Tertiary:** AI-native startups building multi-agent pipelines who need
formal memory isolation guarantees between agents (INV-15 is the only
published formal invariant for this class of problem that has a
hardware-validated implementation).

The immediate customer for the hackathon demo is Veea Inc. (the TechEx 2026
sponsor), whose LobsterTrap DPI infrastructure we integrated. The longer-term
customer is any team where a single-vendor AI review loop is a compliance or
security risk.

---

### 11. Why now?

Three forces converged in 2026:

**The threat surface expanded.** AI coding assistants can now read files,
run shell commands, create pull requests, and push to version control. An
attacker who can influence an AI agent's context — via a README, a docstring,
a fetched dependency — can influence production code. The 2026 OWASP Top 10
for LLM Applications (LLM02: Tool Poisoning) reflects this. The defenses
have not kept pace.

**The multi-vendor model landscape matured.** Running nine frontier LLMs from
nine different vendors was not cost-effective two years ago. OpenRouter reduced
the API surface to a single endpoint; cost-per-token dropped enough that a
nine-vendor adversarial pass is within the budget of a per-PR review workflow.

**Formal verification of AI memory became tractable.** The INV-15 invariant
and its proof (DOI 10.5281/zenodo.20114594) are grounded in real KV-cache
mechanics — not a theoretical abstraction. Hardware validation on AMD MI300X
(ROCm 7.2.0) shows the isolation holds under the memory access patterns of
production vLLM serving. That grounding was not possible before ROCm 7.x
stabilized AMD's HIP memory model.

---

### 12. What's traction?

**Shipped in seven days.** The product went from a blank repo to a live
deployment with:

- 350+ pytest tests across three repos
- 15+ committed measurement JSON files (all public in the GitHub repos)
- A peer-reviewable paper with a Zenodo DOI (10.5281/zenodo.20114594)
- A live demo at https://149.28.56.91.nip.io/ (no signup)
- Two hackathon submissions: TechEx 2026 (judging window May 14–26) and
  Milan AI Week 2026 (deadline May 20, prize pool $28K+)

**Measurement-backed claims (not marketing):**

- JBB-Behaviors ensemble block rate: **93.75%** (Wilson 95% CI [86.2%, 97.3%],
  n=80 holdout). Source: `logs/baseline_aegis-ensemble-10frontier_day5_FALLBACK_20260515T212737Z.json`
  in the apohara-aegis repo.
- LobsterTrap DPI benign false-positive rate: **9.8%** (Wilson 95% CI [4.3%, 21.0%],
  n=51). Source: `logs/lobstertrap_block_rate_20260518T155431Z.json` in this repo.
- Hardware validation: AMD MI300X 192 GB HBM3, ROCm 7.2.0. NVIDIA H100.

**Revenue:** Pre-revenue. The commercial model (see Q18) has not been
activated; we are in the hackathon/demo window.

**Signups:** No signup gate on the demo; rate-limited to 5 calls per IP per
UTC day to control shared Gemini API spend.

---

### 13. Why is your team uniquely qualified?

The technical moat has three layers that are hard to replicate quickly:

**INV-15 formal proof.** Writing a formal safety invariant for KV-cache
isolation between writer and critic agents, proving it, and validating
it on real hardware is not a weekend project. The paper is at
DOI 10.5281/zenodo.20114594. The implementation is in
`apohara_context_forge/safety/jcr_gate.py`. The proof is machine-checkable.
No competitor in the current hackathon field — and, to our knowledge, no
commercially deployed product — has an equivalent.

**Multi-hardware grounding.** Most LLM safety research is CUDA-only.
PROBANT's measurement logs include AMD ROCm runs on MI300X. The team has
direct experience with the AMD GPU software stack, ROCm memory semantics,
and vLLM's AMD path — experience that is scarce outside of AMD's own
engineering organization and a handful of research labs.

**Honesty discipline.** The AUDIT.md file in ContextForge publicly documents
ten overclaims from V6.0 with file:line evidence, and tracks each through
closure in V7.0.0-rc.2. This is unusual in both the startup world and the
research world. It reflects a discipline of measurement-first development that
makes the product more credible to technically literate buyers and judges.

---

### 14. Why us? Why YC?

YC's batch would give PROBANT two things the solo-founder/hackathon path
does not:

**GTM network.** The product's natural first buyers are engineering leaders
at AI-forward companies. YC's alumni network has dense coverage of exactly
that buyer profile. A warm introduction from a YC partner to a CISO or
VP Engineering at a YC portfolio company is worth more than six months of
cold outreach.

**Co-founder matching.** The technical foundation is complete. The missing
piece is a co-founder who can own enterprise sales, pricing, and customer
discovery. YC's co-founder matching program is the most efficient path to
finding that person.

**Advice on enterprise sales cycles.** Security products have long sales
cycles. Getting the pricing and the pilot structure right in the first
three enterprise conversations matters a great deal. YC has pattern-matched
on this more than almost any other institution.

---

### 15. What are the biggest risks?

**False negative rate.** The 9-vendor ensemble has a 6.25% false negative
rate on JBB-Behaviors (n=80). Some fraction of genuinely harmful prompts will
be classified as verified. The product mitigates this with the LobsterTrap
DPI pre-check (a separate detection layer) and with the NO-HEDGING gate
(which surfaces model uncertainty on individual attacker verdicts). But it
does not eliminate the risk. Buyers who need a 0% false negative rate should
use the product as one layer of a defense-in-depth stack, not as a single gate.

**API dependency concentration.** Nine vendors are accessed via OpenRouter.
OpenRouter itself is a dependency. If OpenRouter's pricing changes materially
or if multiple vendors restrict API access, the ensemble degrades. The
mitigation is that the architecture supports direct vendor APIs — removing
the OpenRouter intermediary requires changing one adapter layer, not
re-architecting the system.

**Solo founder execution risk.** All production code was written by one
person in seven days. That pace is not sustainable. The most important
near-term action is co-founder recruitment; YC's program accelerates this.

**Regulatory uncertainty.** The EU AI Act and emerging US federal AI
regulations may create compliance requirements for AI-assisted code review
tools. The HMAC-signed audit ledger is already a strong foundation for
compliance; the formal INV-15 proof is unusually strong evidence of safety
discipline for a pre-revenue startup. But the regulatory landscape is
evolving faster than any single team can track.

---

### 16. What other startups are most similar?

The direct competitive set from TechEx 2026 (our field):

| Competitor | Stack | Tests | Measurements | Paper |
|---|---|---|---|---|
| Pantheon | Gemini 2.5 Flash (single vendor) + LobsterTrap HTTP | 0 | 0 | No |
| Vela | Gemini 2.5 Flash (single vendor) + LobsterTrap (claimed) | 0 | 0 | No |
| Trusyn | TypeScript + Gemini family (single vendor) | 0 | 0 | No |
| **Apohara PROBANT** | **9-vendor ensemble + INV-15 + signed ledger** | **350+** | **15+ JSON logs** | **Yes, DOI 10.5281/zenodo.20114594** |

The broader market includes:
- **NeMo Guardrails** (NVIDIA, Apache-2.0): prompt injection and jailbreak
  scanning, single-vendor, no adversarial ensemble, no memory isolation.
- **Gemini Code Assist** (Google): single-vendor, no adversarial review.
- **LlamaGuard / Purple Llama** (Meta): safety classifier, not a code review
  tool, no memory isolation.
- **Granite Guardian 4** (IBM): single-vendor classifier.

None of them have an adversarial multi-vendor ensemble, a formal memory
isolation invariant, or an HMAC-signed audit chain.

---

### 17. What's your moat? Why won't established players crush you?

Three structural advantages are hard to replicate quickly:

**The formal proof.** INV-15 is a published, peer-reviewable formal safety
invariant with hardware validation. Google, Anthropic, OpenAI, and Microsoft
all have research teams that could produce an equivalent — but they have not.
The academic credibility of a Zenodo-archived paper with a DOI is not something
a product team can spin up in a quarter.

**The multi-vendor architecture is the product.** Established players cannot
build a 9-vendor adversarial ensemble that includes their own competitors.
Google cannot sell a product where Claude Opus 4.7 adversarially attacks
Gemini's output. That conflict of interest is structural, not strategic.
Only an independent vendor can build this product honestly.

**The audit trail as a compliance asset.** The HMAC-signed SHA-256 chain
is not just a security feature — it is the foundation of a compliance
product. As AI-assisted code review becomes subject to audit requirements
(SOC 2, ISO 27001 AI annexes, EU AI Act Article 17 technical documentation),
the signed ledger becomes a qualification criterion rather than a
differentiator. Established players will add audit logging eventually; being
first with a production-grade, cryptographically verifiable implementation
matters in enterprise sales.

---

### 18. How will you make money?

**Phase 1 (current): API access, usage-based pricing.**
- `$0.10 per verification` for teams using their own OpenRouter/Gemini keys
  (BYOK). The cost per call to us is $0 after infrastructure; we bear the
  Vultr droplet cost.
- `$0.25 per verification` for teams using our shared API key pool. We absorb
  the OpenRouter cost (approximately $0.04–$0.12 per 9-vendor call at current
  pricing) and take a margin.

**Phase 2: Enterprise contracts.**
- Flat monthly fee for unlimited verifications + SLA + on-premise deployment
  option. Target: $2K–$10K/month per enterprise customer.
- The HMAC-signed audit ledger + INV-15 compliance documentation become the
  primary sales asset for regulated industries (fintech, healthcare, defense
  contractors).

**Phase 3: Platform.**
- Third-party model adapters (teams bring their own preferred vendor set).
- Custom verdict aggregation policies (replace the 0-2/3-5/6+ thresholds
  with customer-defined rules).
- Integration with CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins) as
  a native check step.

---

### 19. How will you find users / what's your distribution plan?

**Hackathon exposure (immediate).** TechEx 2026 and Milan AI Week 2026 put
the product in front of judges, sponsors, and other founders who are the
exact buyer profile. The Veea Inc. LobsterTrap integration is already a
warm commercial relationship.

**Developer content (30–90 day).** The blog series starting with this post
targets engineers who are already using AI coding assistants and are starting
to ask "what does 'verified' mean?" The JBB measurement numbers and the
Wilson CI methodology are specific enough to generate organic sharing in
technical communities (Hacker News, r/MachineLearning, the MLSec Discord).

**Paper citation network (ongoing).** The INV-15 paper is on Zenodo with a
DOI. As it gets cited, each citation is a warm lead — researchers who cite
it are working in adjacent problem spaces and are potential design partners
or early customers.

**YC batch network (if accepted).** The most direct path to the first ten
enterprise customers is a warm introduction through the YC alumni network.

**Open source community (ongoing).** All three repos are Apache-2.0 (PROBANT,
ContextForge, Aegis). Open source removes the evaluation friction for
engineering buyers who need to audit the implementation before committing
budget. The audit trail of public commits and measurement logs is itself a
marketing asset.

---

### 20. Anything else we should know?

**The honesty culture is load-bearing, not decorative.** The AUDIT.md file
in ContextForge is not a changelog — it is a public record of overclaims
with file:line evidence and tracked closure. We built this culture because
we believe that a security product making false claims about its own security
is a structurally incoherent business. When judges ask us to explain the
difference between our 93.75% block rate and a competitor's claimed 98%, we
can open the log file. We cannot do that if we typed the number instead of
measuring it.

**Multi-hardware validation is rare and matters.** Most AI safety research
runs on NVIDIA A100 or H100. The AMD ROCm path in vLLM has known behavioral
differences from the CUDA path in how memory prefetching and KV-cache eviction
interact. The INV-15 invariant has been validated on both hardware families.
That is not a technical detail — it is evidence that the implementation is
robust to the full range of hardware your customers will deploy on.

**The architecture supports the commercial thesis.** The three-repo structure
(PROBANT = product, Aegis = ensemble library, ContextForge = memory plane +
paper) is not accidental. Aegis and ContextForge are independently useful
libraries that can be licensed separately. ContextForge's INV-15
implementation is already used in the Milan AI Week submission as a
multi-agent memory isolation layer for a completely different use case
(5-agent RAG prefix sharing). The product surface area is larger than the
current hackathon demo makes visible.

**Apache-2.0 + AGPL-3.0 license split.** PROBANT and ContextForge are
Apache-2.0. The Apohara Guard TypeScript project (from which VerdictVault
was ported) is AGPL-3.0. The license split is intentional: the core
libraries are permissive to maximize adoption; the guard service layer
has a copyleft license that prevents competitors from taking the audit
chain implementation and wrapping it in a proprietary product without
contributing back.

---

## EU Accelerator Equivalents

If the YC Summer 2026 timeline does not align, the following EU programs
are relevant based on Pablo's location (Argentina, Spanish-speaking),
the AI security thesis, and the academic grounding of the product.

---

### Antler Berlin

**Program:** 3-month pre-seed residency, up to €100K investment.
**Application window:** Cohorts in H1 and H2 each year.
**Thesis fit:** Antler Berlin specifically funds deep-tech and AI-native
founders. The INV-15 paper and the measurement logs position PROBANT as
a research-grounded company, which is exactly the profile Antler Berlin
targets. The formal proof is a differentiator in a program that sees many
pure-software AI wrappers.
**Timezone:** Europe/Berlin (UTC+1/UTC+2). Pablo is UTC-3; 4–5 hour overlap
with Berlin is manageable for a remote cohort participant.
**Rationale:** Strong thesis alignment + co-founder matching program
(same gap as YC). Worth applying alongside YC.

---

### Entrepreneur First (EF)

**Program:** 6-month talent investor program. Accepts individuals pre-team.
Investment: £80K at co-founder formation.
**Locations:** London, Berlin, Paris (multiple intakes per year).
**Thesis fit:** EF funds outlier individuals with deep technical backgrounds
building hard problems. Pablo's combination of formal verification background
+ LLM security + multi-hardware validation fits the EF "talent investor"
thesis. EF is explicitly not looking for market-validated ideas — it is
looking for people who can build things others cannot.
**Timezone:** UTC±1/UTC+2 (same manageable overlap as Antler Berlin).
**Rationale:** The best option for co-founder matching specifically. EF's
network is dense with technical founders who could pair with a solo
deep-tech builder. The 6-month timeline is longer than YC's 3 months but
the co-founder-finding thesis is more explicit.

---

### Plug and Play AI Spain (Madrid)

**Program:** 3-month accelerator. Investment varies (typically €50K–€200K).
**Application window:** Ongoing, cohort-based.
**Thesis fit:** Plug and Play's AI Spain vertical focuses on enterprise AI
applications with Spanish-speaking founding teams. Pablo's Spanish-language
background and the AGPL/Apache licensing structure (visible open-source
project) fit the typical Plug and Play portfolio company profile.
**Timezone:** Europe/Madrid (UTC+1/UTC+2). Spanish-language operations remove
the language barrier that affects other EU programs.
**Rationale:** Lower barrier to entry than YC or EF due to language and
geographic focus. Good first step for building an EU investor relationship
before a YC application in a later batch.

---

### Wayra Hispanoamérica (Telefónica)

**Program:** Telefónica's corporate accelerator. Active in Buenos Aires,
Madrid, and other Ibero-American cities. Investment: varies by geography,
typically $50K–$150K equity.
**Thesis fit:** Wayra's recent cohorts have included AI security and
enterprise SaaS companies. Telefónica's infrastructure background makes
them a natural customer for an AI code verification tool deployed in
telco engineering teams. The Spanish-language operating environment and
Argentina presence are strong fits.
**Timezone:** UTC-3 (Buenos Aires). Same timezone as Pablo — the only
EU-adjacent program that requires no timezone compromise.
**Rationale:** Most operationally convenient option. The Telefónica
customer network is a meaningful distribution asset for enterprise sales
in Spanish-speaking markets. The valuation and check size are lower than
YC but the runway-to-first-customer path is shorter.

---

### Berlin AI Cluster (EU-backed, non-equity)

**Program:** EU Horizon-backed funding for AI companies establishing
presence in the Berlin tech ecosystem. Non-equity grants, typically
€50K–€500K.
**Thesis fit:** The INV-15 paper + Zenodo DOI + hardware validation logs
are strong evidence of the research-grounded development that EU Horizon
funding requires. The AGPL-3.0 license on Apohara Guard and the Apache-2.0
licenses on PROBANT/ContextForge satisfy EU open-source funding criteria.
**Timeline:** EU grant cycles are slow (6–18 months from application to
funding decision). This is a medium-term option, not a near-term one.
**Rationale:** Non-dilutive. Worth pursuing in parallel with equity rounds
because it does not affect the cap table and the application materials
(paper, measurement logs, audit trail) are already written.

---

## Application Priority Recommendation

| Program | Timing | Co-founder help | Check size | Fit score |
|---|---|---|---|---|
| YC Summer 2026 | Apply now (deadline ~May/Jun) | Yes | $500K | ⭐⭐⭐⭐⭐ |
| Entrepreneur First | Apply now (rolling) | Yes (primary purpose) | £80K | ⭐⭐⭐⭐⭐ |
| Antler Berlin | Apply now (H2 cohort) | Yes | €100K | ⭐⭐⭐⭐ |
| Wayra Hispanoamérica | Apply Q3 2026 | No | $50–150K | ⭐⭐⭐ |
| Plug and Play AI Spain | Apply Q3 2026 | No | €50–200K | ⭐⭐⭐ |
| Berlin AI Cluster | Apply 2026–2027 | No | €50–500K (grant) | ⭐⭐ |

YC and EF are the priority applications because they are the only two
programs that directly address the co-founder gap. The technical foundation
is complete; the missing execution capacity is in GTM, which requires a
co-founder, not just additional funding.
