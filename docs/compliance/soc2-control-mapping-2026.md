# SOC 2 Trust Services Criteria — Apohara PROBANT Control Mapping

**Version**: 1.0  
**Date**: 2026-05-18  
**Status**: Audit-readiness planning artifact. This is NOT a SOC 2 certification and has NOT been reviewed by an accredited auditor.  
**Prepared by**: Pablo M. Suarez (sole maintainer)  
**Scope**: Apohara PROBANT backend service (`packages/backend/`) and its supporting infrastructure

---

## How to Read This Document

Each row maps one AICPA Trust Services Criterion (TSC) to the Apohara control that addresses it, the evidence file you would show an auditor, and an honest assessment of whether the control is fully implemented, partial, or absent.

**Gap taxonomy**:

- **No** — control fully implemented; evidence present
- **Partial** — control exists but lacks formal documentation, monitoring, or completeness
- **Gap** — control absent; remediation action required before a Type 1 audit

---

## CC1 — Control Environment

| Criterion | Description | Apohara Control | Evidence | Gap? | Remediation |
|---|---|---|---|---|---|
| CC1.1 | Entity demonstrates commitment to integrity and ethical values | AUDIT.md is the public accountability layer with file:line evidence for every claim; ADR-001 documents architectural decisions transparently | `AUDIT.md`, `docs/decisions/ADR-001-rebrand-inti-to-probant.md` | Partial | Formalize a written Code of Conduct and an internal security policy document. A solo founder cannot self-certify ethical oversight — a SOC 2 auditor will require a named officer or board. |
| CC1.2 | Board exercises oversight responsibility | N/A — no board exists (1-person founder team) | — | Gap | Designate a formal advisory board with at least one independent member with security or legal background before a Type 1 audit. Alternatively, engage a virtual CISO service. |
| CC1.3 | Management establishes structure, reporting lines, and authorities | README + AUDIT.md document that Pablo M. Suarez is sole operator | `AUDIT.md` | Partial | Write a formal org chart (even as a single-person document) with defined decision authorities and an incident response chain. |
| CC1.4 | Commitment to competence | System uses 9-vendor adversarial ensemble for cross-AI verification, with hard-coded hedge detection to prevent unconfident verdicts | `packages/backend/judge_gates.py` (HARD_HEDGE list), `packages/backend/verdict_vault.py` | Partial | Document the criteria for adding/removing vendors from the ensemble and the competency review process for each integrated model. |
| CC1.5 | Enforces accountability | HMAC-signed verdict chain creates non-repudiable audit trail; per-org HMAC key isolation prevents cross-tenant forgery | `packages/backend/verdict_vault.py:append()`, `packages/backend/billing/tenant_model.py:create_tenant()` | Partial | Implement a process for reviewing and acting on chain-of-custody alerts. Logging alone is not accountability — a human response process must be documented. |

---

## CC2 — Communication and Information

| Criterion | Description | Apohara Control | Evidence | Gap? | Remediation |
|---|---|---|---|---|---|
| CC2.1 | Obtain and use quality information to support internal control | AUDIT.md tracks control gaps with file:line evidence; LobsterTrap block-rate logs capture DPI signal | `AUDIT.md`, `logs/lobstertrap_block_rate_*.json`, `logs/latency_profile_*.json` | Partial | Define a review cadence for the AUDIT.md entries and block-rate logs. Without a scheduled review, information collection does not become control improvement. |
| CC2.2 | Internally communicate information to support function | No formal internal communication process (1-person team) | — | Gap | Document a minimum: a weekly review checklist of security log files. This satisfies "internal communication" for a small-team entity. |
| CC2.3 | Communicate with external parties about security commitments | No public security policy or responsible disclosure page | — | Gap | Publish a `SECURITY.md` at the repo root with a responsible disclosure address and response SLA. This is a 1-hour task and a hard prerequisite for any enterprise customer security review. |

---

## CC3 — Risk Assessment

| Criterion | Description | Apohara Control | Evidence | Gap? | Remediation |
|---|---|---|---|---|---|
| CC3.1 | Specify objectives with sufficient clarity | `docs/decisions/ADR-001` documents product scope; README specifies what PROBANT does and does not claim | `docs/decisions/ADR-001-rebrand-inti-to-probant.md`, `README.md` | Partial | Write a formal risk appetite statement and a list of in-scope and out-of-scope security objectives. This does not need to be long — one page suffices for a Type 1 audit. |
| CC3.2 | Identify and analyze risks | LobsterTrap DPI blocks prompt injection, SQL injection, and obfuscated payloads; capability fingerprinting classifies high-risk code prompts for escalation | `configs/lobstertrap-policy.example.yaml` (ingress_rules), `packages/backend/capability_fingerprint.py:classify_code()` | Partial | Produce a formal risk register. Even a spreadsheet enumerating OWASP Top 10 mapped to current controls satisfies this criterion for a small entity. |
| CC3.3 | Assess fraud risk | NO-HEDGING gate prevents judges from submitting evasive or uncertain verdicts; HMAC chain prevents verdict tampering | `packages/backend/judge_gates.py:detect_hedging()`, `packages/backend/verdict_vault.py:verify_chain()` | Partial | Document fraud scenarios explicitly (e.g., judge collusion, verdict replay, key compromise) and map each to a control. |
| CC3.4 | Identify and assess changes that could significantly affect internal control | ADR-001 exists; however, there is no change-risk review process | `docs/decisions/ADR-001-rebrand-inti-to-probant.md` | Gap | Establish a change-management checklist run before any backend change is pushed. Minimum: does this change affect the verdict vault, the DPI policy, or the HMAC key management? |

---

## CC4 — Monitoring Activities

| Criterion | Description | Apohara Control | Evidence | Gap? | Remediation |
|---|---|---|---|---|---|
| CC4.1 | Evaluate the design and operating effectiveness of controls as part of ongoing monitoring | Block-rate logs and latency profiles are committed to the repo as evidence; `VerdictVault.verify_chain()` can be called on-demand | `logs/lobstertrap_block_rate_*.json`, `packages/backend/verdict_vault.py:verify_chain()` | Partial | Run `verify_chain()` on a scheduled basis (e.g., nightly cron) and alert on errors. Monitoring needs to be automated, not ad hoc. |
| CC4.2 | Evaluate and communicate deficiencies to responsible parties | AUDIT.md tracks deficiencies publicly | `AUDIT.md` | Partial | Define a process for what happens after a deficiency is identified: who is notified (even if that's just a personal email), when, and what the escalation path is. |

---

## CC5 — Control Activities

| Criterion | Description | Apohara Control | Evidence | Gap? | Remediation |
|---|---|---|---|---|---|
| CC5.1 | Select and develop control activities to mitigate risks | Defense-in-depth: LobsterTrap DPI (network boundary) + prompt envelope with nonces (input isolation) + HMAC chain (output integrity) + NO-HEDGING gate (verdict quality) + Rule-of-Two (agentic safety) | `packages/backend/lobstertrap_client.py`, `packages/backend/envelope.py`, `packages/backend/verdict_vault.py`, `packages/backend/judge_gates.py`, `packages/backend/rule_of_two.py` | No | — |
| CC5.2 | Select and develop general controls over technology | AST linter CI gate prevents unsafe f-string interpolation of untrusted variables; runs at commit time | `packages/backend/scripts/prompt_envelope_audit.py` | Partial | Integrate the linter into a formal CI pipeline (GitHub Actions) so it blocks merges rather than running only manually. |
| CC5.3 | Deploy controls through policies and procedures | LobsterTrap policy file defines ALLOW/DENY/LOG rules declaratively; rate limits configured | `configs/lobstertrap-policy.example.yaml` (ingress_rules, egress_rules, rate_limits) | Partial | The policy file is an `.example.yaml` — document the procedure for promoting it to production and auditing the production version against the example. |

---

## CC6 — Logical and Physical Access Controls

| Criterion | Description | Apohara Control | Evidence | Gap? | Remediation |
|---|---|---|---|---|---|
| CC6.1 | Implement logical access security to protect against unauthorized access | HMAC-signed verdict chain (SHA-256 + HMAC-SHA256) prevents unauthorized modification; per-org HMAC key isolation means one tenant cannot forge another's verdicts | `packages/backend/verdict_vault.py:_sign()`, `packages/backend/billing/tenant_model.py:create_tenant()` (secrets.token_hex(32) per tenant) | No | — |
| CC6.2 | Manage authentication of internal and external users | `APOHARA_LEDGER_HMAC_KEY` env var controls ledger signing; ephemeral key warning is logged when unset | `packages/backend/verdict_vault.py:__init__()` (key_source property and RuntimeWarning) | Partial | Implement API key authentication on the `/v1/verify` endpoint. Currently any caller can submit requests without authentication. This is a critical gap for a production multi-tenant service. |
| CC6.3 | Manage user role-based access to prevent unauthorized access | Multi-tenant model isolates org data; per-org HMAC keys enforce cryptographic tenant separation | `packages/backend/billing/tenant_model.py` (org_id UUID + per-tenant hmac_key column) | Partial | Role-based access control (RBAC) within a tenant is absent. Admin vs. read-only vs. billing roles need definition before an enterprise customer will accept the service. |
| CC6.4 | Manage access to sensitive physical environments | N/A — cloud-hosted; no physical environment owned | — | Partial | Document the cloud provider (Vercel + hosting provider for backend) and confirm their SOC 2 Type 2 coverage covers physical access. Carry forward their certifications by reference. |
| CC6.5 | Manage transmission and disposal of information | LobsterTrap egress rules block credential and exfiltration patterns from model output | `configs/lobstertrap-policy.example.yaml:block_credential_leak`, `block_exfiltration_patterns` | Partial | Define and document a data retention and disposal policy. How long are verdict ledger files retained? When are they deleted? |
| CC6.6 | Implement controls to prevent and detect security threats | LobsterTrap DPI blocks SQL injection, prompt injection, and obfuscated payloads at ingress; capability fingerprinting routes high-risk prompts to aggressive policy | `packages/backend/lobstertrap_client.py:check_prompt_with_lobstertrap()`, `packages/backend/capability_fingerprint.py` | No | — |
| CC6.7 | Manage transmission of confidential information | Network egress allowlist in LobsterTrap policy restricts outbound connections to `api.apohara.dev`, `generativelanguage.googleapis.com`, `openrouter.ai` | `configs/lobstertrap-policy.example.yaml:network.allowed_domains` | No | — |
| CC6.8 | Manage software changes to prevent unauthorized access | AST linter CI gate; Rule-of-Two blocks CI-only agents from pushing without human authorization | `packages/backend/scripts/prompt_envelope_audit.py`, `packages/backend/rule_of_two.py:assert_human_in_loop()` | Partial | Add branch protection rules on the GitHub repo main branch: require PR review and CI pass before merge. |

---

## CC7 — System Operations

| Criterion | Description | Apohara Control | Evidence | Gap? | Remediation |
|---|---|---|---|---|---|
| CC7.1 | Detect and monitor for vulnerabilities | LobsterTrap DPI + prompt envelope nonce system + capability fingerprinting classify and block known attack categories at runtime | `packages/backend/lobstertrap_client.py`, `packages/backend/envelope.py:_make_nonce()`, `packages/backend/capability_fingerprint.py` | Partial | Add scheduled dependency vulnerability scanning (Dependabot or Snyk). Runtime DPI does not replace static dependency audits. |
| CC7.2 | Monitor system components for anomalous behavior | Block-rate and latency logs are committed; LobsterTrap LOG action creates audit trail for PII and credential detection events | `logs/lobstertrap_block_rate_*.json`, `logs/lobstertrap_e2e_latency_*.json`, `configs/lobstertrap-policy.example.yaml:log_pii_request`, `log_credentials` | Partial | Route LOG events to an alerting channel (email, PagerDuty, or Slack webhook). Logs that are never read do not satisfy anomaly monitoring. |
| CC7.3 | Implement procedures to detect and respond to security incidents | No formal incident response plan | — | Gap | Write a minimum-viable incident response plan: 5 bullet points covering detection, containment, notification, remediation, and post-mortem. Post it as `docs/compliance/incident-response-plan.md`. |
| CC7.4 | Respond to identified security incidents and recover from them | No documented process | — | Gap | Same as CC7.3. The plan must exist before the observation period for SOC 2 Type 2. |
| CC7.5 | Identify and develop recovery from disruption | LobsterTrap fails-open to preserve availability when unreachable; the 9-vendor ensemble degrades gracefully if individual vendors are unavailable | `packages/backend/lobstertrap_client.py:check_prompt_with_lobstertrap()` (fail-open path), `packages/backend/main.py` (ensemble fallback) | Partial | Document a formal recovery time objective (RTO) and recovery point objective (RPO) even if they are aspirational (e.g., RTO 4 hours, RPO 24 hours). |

---

## CC8 — Change Management

| Criterion | Description | Apohara Control | Evidence | Gap? | Remediation |
|---|---|---|---|---|---|
| CC8.1 | Authorize, design, develop, configure, document, test, approve, and implement changes | ADR-001 shows architectural decision documentation; AUDIT.md tracks all material changes; AST linter gates code changes | `docs/decisions/ADR-001-rebrand-inti-to-probant.md`, `AUDIT.md`, `packages/backend/scripts/prompt_envelope_audit.py` | Partial | Formalize a change-management checklist. At minimum: every change to `verdict_vault.py`, `envelope.py`, `lobstertrap_client.py`, or the LobsterTrap policy must update AUDIT.md and pass the linter before deployment. |

---

## CC9 — Risk Mitigation

| Criterion | Description | Apohara Control | Evidence | Gap? | Remediation |
|---|---|---|---|---|---|
| CC9.1 | Identify, select, and develop risk mitigation | Defense-in-depth layering (DPI + envelope + HMAC + hedge gate + Rule-of-Two) represents a deliberate risk mitigation strategy | All backend controls collectively | No | — |
| CC9.2 | Assess and manage risks associated with vendors | 9-vendor adversarial ensemble design means no single vendor failure compromises the verdict; THIRD_PARTY_NOTICES.md inventories all dependencies | `packages/backend/main.py` (ensemble), `THIRD_PARTY_NOTICES.md`, `LICENSE` | Partial | Write a vendor risk register. For each of the 9 model vendors (Google Gemini, OpenRouter vendors, etc.), document: what data is sent, under what terms, and what the fallback is if that vendor is unavailable or breached. |

---

## Availability (A1)

| Criterion | Description | Apohara Control | Evidence | Gap? | Remediation |
|---|---|---|---|---|---|
| A1.1 | Maintain, monitor, and evaluate system availability | Rate limits on LobsterTrap policy prevent abuse that would affect availability; fail-open design for DPI maintains service when LT is unreachable | `configs/lobstertrap-policy.example.yaml:rate_limits` (120 req/min, 2000/hr, burst 30), `packages/backend/lobstertrap_client.py` | Partial | Implement uptime monitoring (e.g., UptimeRobot free tier). Document a target availability SLA in the README or a service-level document. |
| A1.2 | Ensure environmental protections are in place | Hosted on cloud infrastructure (Vercel + backend hosting) | — | Partial | Carry forward host provider's availability certifications by reference. Document which cloud regions are used and what the failover strategy is. |
| A1.3 | Implement recovery procedures | LobsterTrap fails-open; no formal disaster recovery plan | — | Gap | See CC7.5. Write an RTO/RPO document. |

---

## Confidentiality (C1)

| Criterion | Description | Apohara Control | Evidence | Gap? | Remediation |
|---|---|---|---|---|---|
| C1.1 | Identify and maintain confidential information | Per-org HMAC key isolation in SQLite tenant model ensures org data is not commingled; LobsterTrap LOG action tags PII | `packages/backend/billing/tenant_model.py` (per-row hmac_key), `configs/lobstertrap-policy.example.yaml:log_pii_request` | Partial | Write a data classification policy. What data is confidential (verdict ledger contents, org HMAC keys)? What is public (block rates)? |
| C1.2 | Dispose of confidential information | No documented disposal policy | — | Gap | Define retention periods and deletion procedures for verdict ledger files and tenant database records. |

---

## Processing Integrity (PI1)

| Criterion | Description | Apohara Control | Evidence | Gap? | Remediation |
|---|---|---|---|---|---|
| PI1.1 | Process data completely, accurately, timely, and authorized | SHA-256 hash chain ensures verdict entries cannot be silently dropped or reordered | `packages/backend/verdict_vault.py:verify_chain()` | No | — |
| PI1.2 | Inputs are complete, accurate, and authorized | Prompt envelope with per-request nonces isolates untrusted input; LobsterTrap blocks malformed or malicious input before it reaches the ensemble | `packages/backend/envelope.py:build_envelope()`, `packages/backend/lobstertrap_client.py` | No | — |
| PI1.3 | Errors are identified and communicated | LobsterTrap and verdict vault both surface error states in API responses; chain verification returns error list | `packages/backend/verdict_vault.py:verify_chain()` (returns `(bool, list[str])`), `packages/backend/lobstertrap_client.py` (reason field) | Partial | Implement structured error logging with log levels (ERROR, WARNING, INFO) routed to a persistent log store. |
| PI1.4 | Outputs are complete, accurate, and delivered to authorized parties | HMAC-signed verdicts with SHA-256 chain allow recipients to independently verify output authenticity | `packages/backend/verdict_vault.py:append()` (returns prev_hash, signed_hash, signature) | No | — |
| PI1.5 | Store and retain system input and output | Verdict ledger is append-only and persisted to disk; chain verification enables forensic audit | `packages/backend/verdict_vault.py` (append-only JSONL ledger) | Partial | Define the ledger retention policy. How long is the JSONL file kept? Is it backed up? |

---

## Privacy (P1–P8)

The Privacy TSC applies when a service collects and processes personal data. Apohara PROBANT's primary input is code snippets submitted for adversarial verification. The following assessment applies to the current production scope.

| Criterion | Description | Apohara Control | Evidence | Gap? | Remediation |
|---|---|---|---|---|---|
| P1.1 | Communicate privacy practices in a privacy notice | No privacy policy published | — | Gap | Publish a privacy policy. If code snippets may contain PII (e.g., variable names, comments with personal data), the service must disclose what is collected, retained, and shared with third-party model vendors. |
| P2.1 | Communicate choices for collection, use, and disclosure | No consent mechanism | — | Gap | For a B2B SaaS, a Data Processing Agreement (DPA) with each customer satisfies this criterion. Write a standard DPA template. |
| P3.1 | Collect personal information only for identified purposes | LobsterTrap LOG action tags PII when detected but does not prevent collection | `configs/lobstertrap-policy.example.yaml:log_pii_request` | Gap | Define whether PII in code inputs is in scope. If so, add a DENY rule or a data minimization step that strips PII before forwarding to model vendors. |
| P4.1 | Limit use of personal information | Code input is forwarded to 9 external model vendors | `packages/backend/main.py` (ensemble dispatch) | Gap | Obtain data processing agreements with each model vendor (Google, OpenRouter). Document what each vendor does with input data. |
| P5.1 | Provide access to correct personal information | No self-service data access mechanism | — | Gap | For GDPR/CCPA compliance, implement a data subject access request process. Even a manual email-based process satisfies this for a small entity. |
| P6.1 | Implement security for disposing of personal information | No disposal process | — | Gap | Add to the data retention policy (see C1.2): verdict ledger entries and code inputs are deleted after N days. |
| P7.1 | Collect and maintain accurate information | N/A — primary inputs are code snippets, not user profile data | — | Partial | If tenant records in the SQLite database constitute personal data (org_name, created_at), define an accuracy maintenance process. |
| P8.1 | Monitor and enforce privacy commitments | No privacy monitoring | — | Gap | Designate a privacy point of contact and document the monitoring process (e.g., quarterly review of what data flows to each vendor). |

---

## Summary: Gap Count

| Category | No Gap | Partial | Gap |
|---|---|---|---|
| Common Criteria (CC1–CC9) | 7 | 22 | 5 |
| Availability (A1) | 0 | 2 | 1 |
| Confidentiality (C1) | 0 | 1 | 1 |
| Processing Integrity (PI1) | 3 | 2 | 0 |
| Privacy (P1–P8) | 0 | 1 | 7 |
| **Total** | **10** | **28** | **14** |

The 14 gaps must be closed before a SOC 2 Type 1 audit can yield a clean opinion. The 28 partial controls require evidence collection (logs, documented procedures, CI pipeline artifacts) before the Type 2 observation period. See `docs/compliance/README.md` for the remediation roadmap and phase timeline.
