# Prior-Art Survey — NIST AI RMF Agentic Profile (OSS implementations)

> **US-70 deliverable** — Apohara PROBANT Fusion Sprint (2026-05-18)
>
> Honesty discipline §6: this doc determines the EXACT wording for our NIST alignment claim. Without it we cannot say "first implementation" anything.

## Survey scope + method

- **Date**: 2026-05-18T20:40Z
- **Tools used**: WebSearch + WebFetch (Microsoft AGT NIST mapping doc + CSA Lab Agentic Profile page)
- **Query**: `"NIST AI RMF Agentic Profile" open source implementation github`
- **Domain**: AI agent governance / SOAR / runtime policy enforcement OSS projects

## Critical finding 1 — There is NO official NIST "Agentic Profile" yet

Per [CSA Lab Space — NIST AI RMF Agentic Profile v1 (March 27, 2026, DRAFT status)](https://labs.cloudsecurityalliance.org/agentic/agentic-nist-ai-rmf-profile-v1/):

> *"This paper is intended to serve as a practitioner-oriented complement to that emerging NIST work, proposing concrete agentic extensions to the existing RMF structure that organizations can begin implementing today. We expect an AI Agent Interoperability Profile is planned for release in the fourth quarter of 2026."*

**Implication**: The document anyone could be implementing "first" today is the **Cloud Security Alliance Labs whitepaper** (CSA-authored, March 2026 draft) — **not an official NIST publication**. NIST's actual Agent Interoperability Profile is planned for Q4 2026.

## Critical finding 2 — Competitor PLAYBOOK SOAR claim is likely overclaim

PLAYBOOK SOAR (github.com/shamuddin/playbook, our direct Veea-category competitor) states throughout their pitch:

> *"PLAYBOOK SOAR is the first implementation of NIST's April 2026 Agentic Incident Response standards"*

There is no publicly identifiable "NIST April 2026 Agentic Incident Response standards" publication. The closest publication in that timeframe is the CSA Lab Agentic Profile (March 2026), which is **NOT** a NIST publication and **NOT** specifically about "Incident Response". PLAYBOOK's claim does not survive prior-art scrutiny.

## Critical finding 3 — Microsoft Agent Governance Toolkit is the most credible prior art

[microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit) — 1.6k stars, 304 forks — claims:

- **"Strong-to-excellent coverage across all four NIST AI RMF 1.0 functions"** (GOVERN / MAP / MEASURE / MANAGE)
- **12 of 19 subcategories fully addressed (63%) + 7 partially addressed (37%)**
- Hybrid enforcement: **PolicyEvaluator + OPA Rego + Cedar backends** (no LLM judge)
- Three enforcement modes: strict / permissive / audit
- Also covers OWASP Agentic Top 10 (10/10) + EU AI Act + OpenSSF Best Practices (100%)

**Important distinction**: Microsoft AGT maps to **NIST AI 100-1 base framework only**. Their NIST alignment doc does NOT reference the CSA "Agentic Profile" specifically. So:
- Microsoft AGT = base NIST AI RMF 1.0 + OWASP Agentic Top 10
- CSA Agentic Profile = March 2026 draft extending NIST AI RMF with agent-specific controls
- Apohara PROBANT (this sprint) = aligning to CSA Agentic Profile + multi-vendor LLM adversarial consensus + INV-15 formal isolation

These are **complementary, not overlapping**.

## Other resources surfaced (non-overlapping)

- [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills) — 754 cybersecurity skills mapped to 5 frameworks including NIST AI RMF. Skills library, not a SOAR/governance platform.
- [Biggertablecloth/ai-risk-management-framework-GPT](https://github.com/Biggertablecloth/ai-risk-management-framework-GPT) — RMF playbook GPT, not an enforcement platform.
- [Rego policy library for AI compliance](https://github.com/topics/nist-ai-rmf) — generic Rego policies covering NIST RMF among 94 frameworks; not agent-specific.

## Defensible claim wording for Apohara PROBANT submission text

**❌ DO NOT claim** (any of these fail prior-art scrutiny):
- "First implementation of NIST AI RMF" — Microsoft AGT preceded us
- "First implementation of NIST AI RMF Agentic Profile" — CSA Agentic Profile is draft (not finalized standard); claim is ambiguous on what is being "first" implemented
- "First implementation of NIST Agentic Incident Response standards" — no such NIST publication exists (PLAYBOOK SOAR's overclaim)

**✅ DEFENSIBLE claim** (all verifiable):
- *"Apohara PROBANT aligns to the Cloud Security Alliance Agentic Profile (March 2026 draft) extensions to NIST AI RMF, combining deterministic rule-based enforcement with 12-vendor LLM adversarial consensus, formal INV-15 KV-cache isolation (Zenodo DOI 10.5281/zenodo.20114594, Z3 SMT proof), and tamper-evident HMAC verdict chain."*

**✅ "First" claim we CAN make** (no prior art found for this specific combination):
- *"Apohara PROBANT is the first open-source implementation combining (a) CSA Agentic Profile alignment, (b) multi-vendor LLM adversarial consensus, (c) formal KV-cache isolation invariant with machine-checked Z3 SMT proof, in a single integrated platform. Microsoft Agent Governance Toolkit covers base NIST AI RMF 1.0 with rule engines (no LLM judges); CSA Agentic Profile is the standard our policy mappings extend; PROBANT operationalizes all three together."*

## Conclusion paragraph for submission long-desc

> *"Apohara PROBANT aligns to the Cloud Security Alliance Agentic Profile (March 2026 draft) extending NIST AI RMF — verified by our `docs/research/nist-mapping.md` cross-reference table. We are the first OSS project to combine this alignment with multi-vendor LLM adversarial consensus AND formal KV-cache isolation (Z3-proven INV-15). Microsoft's Agent Governance Toolkit (1.6k★) is the most prominent adjacent prior art, covering NIST AI RMF 1.0 base with deterministic rule engines; we extend the policy surface to the CSA Agentic Profile and add the semantic-coverage layer of multi-vendor LLM consensus, providing both prompt-injection-immune rule enforcement AND vendor-disagreement-aware semantic catch-all."*

## Update protocol

If new prior art is discovered post-publication:
- Update this doc with citation + date discovered
- Update the submission text + README to match
- Notify Pablo if discovery weakens any claim materially
- `scripts/check_honesty_fusion.sh` Rule 2 enforces this doc must exist before any "first implementation" claim ships
