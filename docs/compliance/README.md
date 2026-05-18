# docs/compliance — Audit-Readiness Planning

**Status**: Planning artifact. Apohara PROBANT is NOT SOC 2 certified and NOT ISO 27001 certified. These documents are self-assessments prepared by the development team to understand the gap between current controls and certification readiness.

---

## What Is in This Folder

| File | What It Contains | When to Read It |
|---|---|---|
| `soc2-control-mapping-2026.md` | Maps each AICPA SOC 2 Trust Services Criterion to existing Apohara controls, with evidence file paths and an explicit gap list | Before a SOC 2 readiness conversation with an auditor or a security-conscious enterprise customer |
| `iso27001-control-mapping-2026.md` | Maps ISO/IEC 27001:2022 Annex A controls (selected 40 of 93) to existing Apohara controls, with a Statement of Applicability summary | Before engaging an ISO 27001 certification body or responding to a vendor security questionnaire |
| `README.md` | This file — index and certification roadmap | Start here |

---

## What This Is Not

These documents are a self-assessment, not a certification. A SOC 2 or ISO 27001 certification requires:

1. An independent accredited auditor (SOC 2: a licensed CPA firm; ISO 27001: an accredited certification body such as BSI, Bureau Veritas, or SGS).
2. A defined observation period for Type 2 assessments (SOC 2 Type 2: minimum 6 months; ISO 27001 surveillance: annual).
3. Evidence collected and managed throughout the observation period, not just at audit time.

A self-assessment that identifies gaps is the correct starting point. Closing those gaps before engaging an auditor reduces audit cost and the likelihood of findings.

---

## Certification Roadmap

### Phase A — Close Self-Identified Gaps (Target: Q3 2026, 8-12 weeks)

The two mapping documents identify 17 total gaps across SOC 2 and ISO 27001. Most are documentation gaps rather than engineering gaps. Priority order:

1. **Write a SECURITY.md** at the repo root with a responsible disclosure address and response SLA. (1 hour)
2. **Write an Information Security Policy** (2 pages covering purpose, scope, roles, review cycle). (4 hours)
3. **Write an incident response plan** covering detection, containment, notification, remediation, and post-mortem. (4 hours)
4. **Implement API key authentication** on `/v1/verify`. The per-org HMAC key infrastructure in `billing/tenant_model.py` is already built; wire it to the endpoint. (1-2 days)
5. **Define data retention and disposal policies** for the verdict ledger and tenant database. (2 hours)
6. **Document HMAC key rotation procedures** with explicit handling of historical ledger entries. (2 hours)
7. **Write a privacy policy** and vendor data processing agreements with Google (Gemini API) and OpenRouter. (1 day)
8. **Add Dependabot or Snyk** for dependency vulnerability scanning. (1 hour to configure)
9. **Integrate AST linter into GitHub Actions CI** so it blocks merges rather than running manually. (2 hours)

Total estimated effort for Phase A: 6-8 person-weeks for a 1-person team, assuming 50% of working time allocated. External legal review of DPAs and privacy policy adds cost (estimate $2,000-5,000 USD for a startup-focused legal service).

### Phase B — Engage Type 1 Auditor (Target: Q4 2026)

A SOC 2 Type 1 audit assesses whether controls are designed appropriately at a point in time. It does not require an observation period.

**Estimated cost ranges** (sources: Vanta pricing guide 2025, Drata blog "How Much Does SOC 2 Cost" 2024):

- SOC 2 Type 1 (Security TSC only): $15,000-30,000 USD for a small software company
- SOC 2 Type 1 (Security + Availability + Confidentiality): $20,000-40,000 USD
- ISO 27001 certification (initial): $25,000-60,000 USD
- Combined SOC 2 Type 1 + ISO 27001: $40,000-80,000 USD

These ranges assume the auditee does preparatory work (i.e., closes Phase A gaps). Auditors charge more when they discover gaps during the audit itself.

Compliance automation platforms (Vanta, Drata, Sprinto) reduce auditor time by automating evidence collection. Pricing is typically $8,000-20,000/year for a startup tier. This is worth evaluating if the team grows beyond 3 people and the evidence collection burden becomes significant.

### Phase C — SOC 2 Type 2 Observation Period (Target: Q1-Q3 2027)

A SOC 2 Type 2 audit covers 6-12 months of operating history. Controls must be operating continuously during this period, not just at the audit date.

A 1-2 person founding team cannot sustain a SOC 2 Type 2 observation period without dedicated headcount or tooling. The minimum realistic staffing for a clean Type 2 is:

- One person responsible for monitoring, evidence collection, and vendor reviews (50% time during observation period)
- A compliance automation platform handling continuous evidence collection

This is an honest constraint. Enterprise customers who require SOC 2 Type 2 as a procurement prerequisite should be managed with a "planned certification by [date]" commitment and a signed roadmap, not a premature Type 2 claim.

---

## Evidence Sources

The existing control evidence referenced in the mapping documents is located at:

| Evidence Type | Path |
|---|---|
| LobsterTrap block-rate logs | `logs/lobstertrap_block_rate_*.json` |
| LobsterTrap latency logs | `logs/lobstertrap_e2e_latency_*.json` |
| DPI policy | `configs/lobstertrap-policy.example.yaml` |
| Verdict vault (HMAC chain) | `packages/backend/verdict_vault.py` |
| Prompt envelope (Spotlighting) | `packages/backend/envelope.py` |
| AST linter CI gate | `packages/backend/scripts/prompt_envelope_audit.py` |
| Multi-tenant HMAC isolation | `packages/backend/billing/tenant_model.py` |
| Architectural decision records | `docs/decisions/` |
| Public accountability log | `AUDIT.md` |
| License and attribution | `LICENSE`, `THIRD_PARTY_NOTICES.md` |
