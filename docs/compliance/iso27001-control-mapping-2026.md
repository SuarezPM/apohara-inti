# ISO/IEC 27001:2022 Annex A — Apohara PROBANT Control Mapping

**Version**: 1.0  
**Date**: 2026-05-18  
**Status**: Audit-readiness planning artifact. This is NOT an ISO 27001 certification and has NOT been reviewed by an accredited certification body.  
**Prepared by**: Pablo M. Suarez (sole maintainer)  
**Standard reference**: ISO/IEC 27001:2022 Annex A (93 controls across 4 clauses)  
**Scope**: Apohara PROBANT backend service (`packages/backend/`) and its supporting infrastructure

---

## How to Read This Document

ISO/IEC 27001:2022 organizes Annex A into four sections:

- **A.5**: Organizational controls (37 controls)
- **A.6**: People controls (8 controls)
- **A.7**: Physical controls (14 controls)
- **A.8**: Technological controls (34 controls)

This document groups controls by family and highlights those most relevant to Apohara PROBANT. Controls that are not applicable to a 1-person software service (e.g., A.7 physical security for a data center) are noted as N/A with a rationale.

**Gap taxonomy**:

- **Implemented** — control in place with evidence
- **Partial** — control partially in place; evidence or documentation incomplete
- **Gap** — control absent; remediation required before certification audit
- **N/A** — not applicable given current scope; rationale provided

---

## A.5 — Organizational Controls

### A.5.1 Policies for Information Security

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.5.1 | Information security policy defined, approved, communicated, reviewed | `AUDIT.md` functions as a public accountability log and tracks control changes; ADR-001 documents architectural decisions | `AUDIT.md`, `docs/decisions/ADR-001-rebrand-inti-to-probant.md` | Partial | Write a concise Information Security Policy (ISP) document covering: purpose, scope, roles, review cycle, and reference to controls. A 2-page document satisfies this for a small entity. |

### A.5.2 Information Security Roles and Responsibilities

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.5.2 | Roles and responsibilities for information security assigned | Pablo M. Suarez is sole operator; this is documented implicitly in `AUDIT.md` | `AUDIT.md` | Partial | Explicitly document security roles even for a 1-person team: "Owner/CISO: Pablo M. Suarez. Responsible for all controls, incident response, and policy review." |

### A.5.7 Threat Intelligence

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.5.7 | Collect and analyze information about information security threats | LobsterTrap DPI policy enumerates known threat patterns (SQL injection, prompt injection, obfuscation, credential patterns); capability fingerprinting classifies 10 vulnerability buckets | `configs/lobstertrap-policy.example.yaml` (ingress_rules with annotated threat categories), `packages/backend/capability_fingerprint.py` (CAPABILITY_BUCKETS) | Implemented | No action required. The threat taxonomy is encoded in production controls and updated as new attack patterns are identified. |

### A.5.14 Information Transfer

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.5.14 | Rules for transferring information with external parties | LobsterTrap network policy allows only three domains for egress: `api.apohara.dev`, `generativelanguage.googleapis.com`, `openrouter.ai`; credential and exfiltration patterns are blocked at egress | `configs/lobstertrap-policy.example.yaml:network.allowed_domains`, `egress_rules:block_credential_leak`, `block_exfiltration_patterns` | Implemented | No action required on egress controls. Gap: no formal data transfer agreement with Google (Gemini API) or OpenRouter documenting what they do with input data. Write DPAs or reference their standard terms explicitly. |

### A.5.23 Information Security for Use of Cloud Services

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.5.23 | Processes for acquisition, use, management, and exit from cloud services defined | Service runs on Vercel (frontend) and a cloud VM (backend); 9 model vendor APIs consumed | `THIRD_PARTY_NOTICES.md`, `packages/backend/pyproject.toml` | Partial | Document the cloud service exit strategy: if Vercel or a model vendor shuts down, what is the migration plan? Even a 1-page runbook satisfies this control. |

### A.5.25 Assessment and Decision on Information Security Events

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.5.25 | Information security events assessed and classified | LobsterTrap LOG action creates audit events for PII and credential detection; block events are captured in block-rate logs | `logs/lobstertrap_block_rate_*.json`, `configs/lobstertrap-policy.example.yaml:log_pii_request` | Partial | Define event severity levels (INFO, WARNING, CRITICAL) and the response action for each. |

### A.5.26 Response to Information Security Incidents

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.5.26 | Respond to information security incidents according to documented procedures | No formal incident response plan | — | Gap | Write a minimum-viable incident response plan. See SOC 2 CC7.3 remediation — the same document satisfies both controls. |

### A.5.28 Collection of Evidence

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.5.28 | Collect, acquire, and preserve evidence for disciplinary or legal action | HMAC-signed SHA-256 chain-of-custody ledger provides forensically sound evidence of verdict history | `packages/backend/verdict_vault.py:append()` (stores prev_hash, signed_hash, signature), `packages/backend/verdict_vault.py:verify_chain()` | Implemented | No action required. The chain-of-custody design explicitly anticipates forensic use ("publishable artifact for forensic auditors" per module docstring). |

### A.5.29 Information Security During Disruption

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.5.29 | Maintain information security during disruption | LobsterTrap client fails-open to maintain service when DPI is unreachable; 9-vendor ensemble degrades gracefully | `packages/backend/lobstertrap_client.py:check_prompt_with_lobstertrap()` (fail-open return) | Partial | Document that the fail-open decision is intentional and bounded: define what security properties are preserved and which are temporarily degraded when LobsterTrap is unreachable. |

### A.5.36 Compliance with Policies, Rules, and Standards

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.5.36 | Compliance with security policy and standards reviewed regularly | AST linter CI gate enforces the no-unsafe-interpolation policy at commit time; `AUDIT.md` tracks policy compliance history | `packages/backend/scripts/prompt_envelope_audit.py`, `AUDIT.md` | Partial | Schedule a quarterly compliance review and document it. A 1-hour calendar event with an `AUDIT.md` entry is sufficient for a small entity. |

### A.5.37 Documented Operating Procedures

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.5.37 | Documented operating procedures available to all who need them | `AUDIT.md` documents procedures implicitly through change history; LobsterTrap policy file is declarative documentation | `AUDIT.md`, `configs/lobstertrap-policy.example.yaml` | Partial | Write a minimal Operations Runbook: how to deploy, how to rotate HMAC keys, how to roll back a bad deployment. This is a prerequisite for handing off operations to a second person. |

---

## A.6 — People Controls

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.6.1 | Screening of employees and contractors | N/A — 1-person team, no employees or contractors | — | N/A | When the first employee or contractor is hired, implement background checks appropriate for the role. |
| A.6.2 | Terms and conditions of employment include security responsibilities | N/A — 1-person team | — | N/A | Write a security responsibilities addendum for future employment agreements. |
| A.6.3 | Awareness, education, and training on information security | N/A — 1-person team; sole operator has technical security expertise demonstrated by the control set | — | N/A | Document that the sole operator maintains security competency through active development of security controls (RAPTOR ports, DPI integration). |
| A.6.4 | Disciplinary process for policy violations | N/A — 1-person team | — | N/A | Define when this becomes applicable (e.g., at first hire). |
| A.6.5 | Responsibilities after termination or change of employment | N/A — 1-person team | — | N/A | Define HMAC key revocation and account access removal procedures to run if a contractor's engagement ends. |
| A.6.6 | Confidentiality agreements | No NDAs in use | — | Partial | Use a standard NDA template with any contractors or beta customers who receive access to the system. |
| A.6.7 | Remote working | N/A — fully remote by design | — | N/A | — |
| A.6.8 | Information security event reporting | LobsterTrap LOG events and block-rate logs create event records; no human reporting process | `logs/lobstertrap_block_rate_*.json` | Partial | Define who receives security event reports and at what threshold. Even "sole operator reviews block-rate log weekly" satisfies this. |

---

## A.7 — Physical Controls

All A.7 controls relate to physical premises and hardware. Apohara PROBANT is a cloud-hosted service with no owned physical infrastructure. The following table applies the relevant subset.

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.7.1 Physical security perimeters | No physical premises owned | — | N/A | Carry forward cloud provider's physical security certifications (Vercel / hosting provider SOC 2 Type 2 covers this). Document the provider's certifications by reference. |
| A.7.2 Physical entry controls | No physical premises owned | — | N/A | Same as A.7.1. |
| A.7.6 Working in secure areas | Development performed on personal workstation | — | Partial | Document workstation security baseline: full-disk encryption enabled, screen lock configured, no shared access. |
| A.7.8 Equipment siting and protection | N/A — cloud-hosted | — | N/A | — |
| A.7.9 Security of assets off premises | Development laptop is an asset off-premises | — | Partial | Document laptop security policy: full-disk encryption, remote wipe capability, VPN for accessing production systems. |
| A.7.10 Storage media | SQLite tenant database and verdict ledger files are stored on cloud VM | — | Partial | Define backup procedures and storage encryption requirements for the SQLite database containing HMAC keys. |
| A.7.12 Cabling security | N/A — cloud-hosted | — | N/A | — |
| A.7.14 Secure disposal or re-use of equipment | N/A — cloud-hosted; VM termination handled by cloud provider | — | N/A | Document that VM termination (e.g., after a Hot Aisle MI300X session) includes verification that volumes containing secrets are destroyed. |

---

## A.8 — Technological Controls

### A.8.2 Privileged Access Rights

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.2 | Allocate and manage privileged access rights | Rule-of-Two gate blocks unattended agents from taking privileged actions (merge, deploy) in CI environments without human override | `packages/backend/rule_of_two.py:assert_human_in_loop()` (blocks when CI detected + no TTY + no override) | Implemented | No action required on the gate itself. Gap: the `APOHARA_WRITE_AGENT_TRUST=1` override env var is not access-controlled — document who is authorized to set it and under what conditions. |

### A.8.4 Access to Source Code

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.4 | Access to source code managed and controlled | GitHub repository is the sole source of truth; currently public (Apache-2.0) | `LICENSE` | Partial | For sensitive configuration files (LobsterTrap policy, HMAC key rotation procedures), ensure they are not committed to the public repo. The example YAML is correctly labeled `.example.yaml`; confirm the production version is gitignored. |

### A.8.5 Secure Authentication

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.5 | Secure authentication technologies and procedures implemented | Per-org HMAC key (secrets.token_hex(32) = 256-bit entropy) generated at tenant creation; key stored in SQLite with no plaintext exposure in API responses | `packages/backend/billing/tenant_model.py:create_tenant()` (hmac_key column, secrets.token_hex(32)) | Partial | The `/v1/verify` endpoint currently lacks authentication — any caller can submit requests. Implement API key authentication using the per-org HMAC key as a bearer token or derive a separate API key per tenant. |

### A.8.7 Protection Against Malware

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.7 | Protection against malware implemented | LobsterTrap DPI blocks obfuscated payloads at ingress; prompt envelope prevents injected content from escaping the untrusted-block container | `configs/lobstertrap-policy.example.yaml:block_obfuscation_high_risk`, `packages/backend/envelope.py:build_envelope()` | Implemented | No action required. The defense-in-depth approach (DPI before envelope before model) is the appropriate pattern for an AI code verifier. |

### A.8.9 Configuration Management

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.9 | Configuration established, documented, implemented, monitored, and reviewed | LobsterTrap policy defines configuration declaratively in YAML; `AUDIT.md` records configuration changes | `configs/lobstertrap-policy.example.yaml`, `AUDIT.md` | Partial | Implement configuration drift detection: confirm the production LobsterTrap policy matches the committed example after each deployment. A `diff` check in the deployment script satisfies this. |

### A.8.10 Information Deletion

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.10 | Information stored in systems, devices, or media deleted when no longer required | No deletion policy defined | — | Gap | Define retention periods: how long are verdict ledger JSONL files kept? How long are tenant records kept after account closure? Implement a deletion procedure. |

### A.8.12 Data Leakage Prevention

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.12 | Data leakage prevention measures applied | LobsterTrap egress rules block model output containing credentials, exfiltration patterns, and sensitive filesystem paths | `configs/lobstertrap-policy.example.yaml:block_credential_leak`, `block_exfiltration_patterns`, `log_sensitive_paths` | Implemented | No action required. Ingress + egress DPI covers the primary data leakage vectors for an AI code verifier. |

### A.8.15 Logging

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.15 | Logs that record activities, exceptions, faults, and other relevant events produced, stored, protected, and analyzed | LobsterTrap block-rate and latency logs committed to repo; HMAC-signed verdict ledger is an append-only tamper-evident log | `logs/lobstertrap_block_rate_*.json`, `logs/lobstertrap_e2e_latency_*.json`, `packages/backend/verdict_vault.py` | Partial | Centralize logs in a persistent, access-controlled store (e.g., Loki, Papertrail, or CloudWatch). Committing logs to a public GitHub repo satisfies auditability but not confidentiality for sensitive events. |

### A.8.16 Monitoring Activities

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.16 | Networks, systems, and applications monitored to detect anomalous behavior and potential incidents | LobsterTrap LOG action captures PII and credential detection events; block-rate logs capture DPI verdicts with timestamps | `logs/lobstertrap_block_rate_*.json` (timestamped JSON with allowed/denied counts), `configs/lobstertrap-policy.example.yaml:log_credentials` | Partial | Route events to an alerting system. Define thresholds: if the block rate exceeds X% of requests in a 5-minute window, trigger an alert. |

### A.8.20 Network Security

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.20 | Networks and network devices secured to protect information systems and applications | LobsterTrap network egress allowlist restricts outbound connections to three known-good domains | `configs/lobstertrap-policy.example.yaml:network.egress_policy` (allowlist) + `allowed_domains` | Implemented | No action required on egress allowlist. Document ingress network security (TLS enforcement on the FastAPI endpoint, Vercel's DDoS protection for the frontend). |

### A.8.21 Security of Network Services

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.21 | Security mechanisms, service levels, and requirements of network services identified, implemented, and monitored | LobsterTrap rate limits (120 req/min, 2000/hr, burst 30) protect the service from abuse | `configs/lobstertrap-policy.example.yaml:rate_limits` | Partial | Document the rate limits in the API documentation and confirm they are enforced at the network layer (not just in the LT policy, which is optional when LT is disabled). |

### A.8.23 Web Filtering

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.23 | Access to external websites managed to reduce exposure to malicious content | LobsterTrap blocks prompt injection attempts and obfuscated content at ingress before they reach model APIs | `configs/lobstertrap-policy.example.yaml:block_prompt_injection`, `block_obfuscation_high_risk` | Implemented | No action required. The DPI policy functions as the equivalent of web filtering for AI input traffic. |

### A.8.24 Use of Cryptography

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.24 | Rules for effective use of cryptography, including cryptographic key management, defined and implemented | HMAC-SHA256 for verdict signing; SHA-256 for hash chain; `secrets.token_hex(32)` for nonce and key generation throughout; per-org HMAC key (256-bit) isolated per tenant | `packages/backend/verdict_vault.py` (hmac.new + hashlib.sha256), `packages/backend/envelope.py:_make_nonce()` (secrets.token_hex(16)), `packages/backend/billing/tenant_model.py:create_tenant()` (secrets.token_hex(32)) | Implemented | Gap: no documented key rotation procedure. Define how and when the `APOHARA_LEDGER_HMAC_KEY` is rotated, and what happens to historical ledger entries when the key changes (they become unverifiable — this must be communicated clearly). |

### A.8.25 Secure Development Lifecycle

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.25 | Rules for secure development of software and systems established and applied | AST linter CI gate enforces no-unsafe-interpolation rule; Rule-of-Two blocks CI agents from merging without human review | `packages/backend/scripts/prompt_envelope_audit.py`, `packages/backend/rule_of_two.py` | Partial | Document the Secure Development Lifecycle (SDLC) as a policy: what security checks run before merge, who approves security-sensitive changes, and what the escalation path is for a security finding. |

### A.8.26 Application Security Requirements

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.26 | Information security requirements identified, specified, and approved when developing applications | Prompt injection defense (Spotlighting pattern, arXiv 2403.14720) is a documented security requirement; HMAC chain is a documented integrity requirement | `packages/backend/envelope.py` (docstring cites Hines et al. arXiv 2403.14720), `packages/backend/verdict_vault.py` (docstring explains tamper-evidence property) | Implemented | No action required. The module docstrings serve as application security requirements documentation. |

### A.8.27 Secure System Architecture and Engineering Principles

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.27 | Principles for engineering of secure systems established, documented, maintained, and applied | Defense-in-depth: LobsterTrap (boundary) → prompt envelope (input isolation) → 9-vendor ensemble (cross-validation) → HMAC chain (output integrity) → NO-HEDGING gate (verdict quality) | All backend controls collectively | Implemented | No action required. The layered architecture is a deliberate security engineering choice documented in module docstrings and `AUDIT.md`. |

### A.8.28 Secure Coding

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.28 | Secure coding principles applied in software development | AST linter detects unsafe f-string interpolation of untrusted variables; TaintedString marker enables static taint tracking | `packages/backend/scripts/prompt_envelope_audit.py` (UNTRUSTED_ATTRS frozenset + AST walk), `packages/backend/envelope.py:TaintedString` | Implemented | No action required. The combination of taint tracking and AST linting exceeds the typical implementation of this control for a project of this size. |

### A.8.29 Security Testing in Development and Acceptance

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.29 | Security testing processes defined and implemented in the development lifecycle | AST linter runs as a CI gate; smoke tests committed to `logs/`; JailbreakBench measurements in `logs/` | `packages/backend/scripts/prompt_envelope_audit.py`, `logs/smoke_p1_p3_audit_*.json`, `logs/lobstertrap_block_rate_*.json` | Partial | Add automated security tests to the test suite (e.g., `pytest` tests for: LobsterTrap blocks known injection strings, verdict chain verification passes, envelope nonce prevents sentinel injection). |

### A.8.30 Outsourced Development

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.30 | Organization supervises and monitors outsourced development | RAPTOR patterns (MIT-licensed) ported as internal Python; THIRD_PARTY_NOTICES.md tracks all attribution | `packages/backend/rule_of_two.py` (cites gadievron/raptor MIT), `THIRD_PARTY_NOTICES.md` | Implemented | No action required. Porting vs. vendoring is documented; all licenses are tracked. |

### A.8.31 Separation of Development, Test, and Production Environments

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.31 | Development, testing, and operational environments separated and secured | No formal environment separation documented | — | Partial | Document the current environment topology: local dev → Vercel preview (staging) → Vercel production + backend VM (production). Confirm that production secrets (HMAC key, API keys) are not used in dev/test environments. |

### A.8.32 Change Management

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.32 | Changes to information systems subject to change management procedures | `AUDIT.md` tracks all material changes; ADR-001 documents architectural decision process | `AUDIT.md`, `docs/decisions/ADR-001-rebrand-inti-to-probant.md` | Partial | Formalize the change management checklist. See SOC 2 CC8.1 remediation — the same checklist satisfies both controls. |

### A.8.33 Test Information

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.33 | Test information selected, protected, and managed | Smoke test logs in `logs/` contain real API response data; no personal data used in tests | `logs/smoke_p1_p3_*.json` | Partial | Confirm that no production tenant data or real user code is used in test fixtures. If so, document the anonymization procedure. |

### A.8.34 Protection of Information Systems During Audit Testing

| Control | Description | Apohara Control | Evidence | Status | Remediation |
|---|---|---|---|---|---|
| A.8.34 | Audit tests on running systems planned and agreed to minimize disruption | No formal audit testing procedure | — | Gap | When engaging an auditor, define an audit testing scope and schedule that avoids production disruption. This is a pre-audit planning item, not a day-one task. |

---

## Summary: Control Status by Section

| Section | Implemented | Partial | Gap | N/A |
|---|---|---|---|---|
| A.5 Organizational (selected 10) | 3 | 6 | 1 | 0 |
| A.6 People (8 controls) | 0 | 2 | 0 | 6 |
| A.7 Physical (selected 8) | 0 | 2 | 0 | 6 |
| A.8 Technological (selected 20) | 9 | 9 | 2 | 0 |
| **Total** | **12** | **19** | **3** | **12** |

The 3 gaps (A.5.26 incident response, A.8.10 information deletion, A.8.34 audit testing procedure) and the 19 partial controls represent the pre-certification work backlog. Most partials require documentation rather than new engineering. See `docs/compliance/README.md` for the phase roadmap.

---

## Statement of Applicability (SoA) Summary

ISO 27001:2022 requires a Statement of Applicability (SoA) listing all 93 Annex A controls and whether each is applicable, implemented, and the justification for exclusions. This document covers the controls most relevant to Apohara PROBANT. A full SoA covering all 93 controls should be prepared before engaging a certification body; controls excluded due to scope (e.g., all A.7 physical controls for a cloud-only service) must be justified in writing.

The controls in this document that are fully implemented (12 total) represent the strongest starting point for an ISO 27001 audit: A.5.7 (threat intelligence), A.5.14 (information transfer), A.5.28 (evidence collection), A.8.2 (privileged access), A.8.7 (malware protection), A.8.12 (data leakage prevention), A.8.20 (network security), A.8.23 (web filtering), A.8.24 (cryptography — noting key rotation gap), A.8.26 (application security requirements), A.8.27 (secure architecture), A.8.28 (secure coding), A.8.30 (outsourced development).
