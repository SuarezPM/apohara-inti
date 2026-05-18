# Apohara PROBANT Incident Taxonomy — 16 Incident Codes

**Version:** 1.0.0 (US-74, 2026-05-18)
**Status:** Canonical — used by SOAR DETECT stage and FORENSICS audit trail
**Implementation:** `apohara-aegis/apohara_aegis/taxonomy.py`

---

## Overview

PROBANT classifies agentic AI misbehavior into **16 incident codes** across
**6 attack families**. Unlike PLAYBOOK SOAR templates (which interleave
categories), this taxonomy maintains strict categorical grouping so that
SOAR routing rules, DJL filter rules (US-72), and compliance mappings are
family-scoped. Industry-specific playbooks (US-75) map onto these codes
rather than replacing them.

**Design references:**

- OWASP LLM Top 10 (2025 edition, published Jan 2025):
  <https://genai.owasp.org/llm-top-10/>
- NIST AI Risk Management Framework 1.0 (Jan 2023):
  <https://doi.org/10.6028/NIST.AI.100-1>
- EU AI Act, Official Journal L 1689 (July 2024):
  <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202401689>
- NIST SP 800-53 Rev 5 (Sep 2020):
  <https://doi.org/10.6028/NIST.SP.800-53r5>
- ISO/IEC 27001:2022, ISO/IEC 42001:2023

---

## Category Summary

| Category | Prefix | Count | Severity range |
|---|---|---|---|
| Prompt Injection | AGT-PI | 3 | 7–9 |
| Data Exfiltration | AGT-EXF | 3 | 8–9 |
| Tool Misuse | AGT-MIS | 3 | 8–10 |
| Financial Misconduct | AGT-FIN | 2 | 9–10 |
| Privacy / PII | AGT-PII | 2 | 8–9 |
| Governance | AGT-GOV | 3 | 8–10 |
| **Total** | | **16** | |

---

## Full Taxonomy Table

### Prompt Injection (AGT-PI)

| Code | Name | Sev | Description | Detection Signals | DJL Rules | Compliance Refs |
|---|---|---|---|---|---|---|
| AGT-PI-001 | Prompt Override Attempt | 8 | Agent received explicit instructions to override system prompt or ignore safety constraints (e.g. "ignore previous instructions", "developer mode", "DAN"). | `ignore previous`, `disregard instructions`, `developer mode`, `system override`, `DAN`, `jailbreak` | DJL-PI-001, DJL-PI-002, DJL-PI-003 | NIST-AI-RMF:GOVERN-1.1, OWASP-LLM-2026:LLM01, EU-AI-ACT:Art-14, NIST-SP-800-53:SI-10 |
| AGT-PI-002 | Roleplay Persona Manipulation | 7 | Agent was instructed to adopt an alter-ego or fictional persona with no safety restrictions, bypassing alignment via narrative framing. | `pretend you are`, `act as`, `you are now`, `in this roleplay`, `fictional AI`, `no restrictions` | DJL-PI-004, DJL-PI-005 | OWASP-LLM-2026:LLM01, NIST-AI-RMF:MAP-1.1, EU-AI-ACT:Art-9 |
| AGT-PI-003 | Indirect Prompt Injection | 9 | Malicious instructions embedded in external content (document, web page, tool output, database record) caused the agent to execute attacker-controlled commands. | `[[SYSTEM]]`, `<!-- inject -->`, `IGNORE PREVIOUS CONTEXT`, `embedded instruction in document`, `tool output contains command` | DJL-PI-006, DJL-PI-007 | OWASP-LLM-2026:LLM02, NIST-SP-800-53:SI-3, EU-AI-ACT:Art-14, ISO-27001:A.12.2 |

> **Primary source:** OWASP LLM Top 10 2025 — LLM01 (Prompt Injection) covers
> both direct and indirect injection vectors. EU AI Act Article 14 requires
> human oversight for high-risk AI systems exposed to adversarial inputs.

---

### Data Exfiltration (AGT-EXF)

| Code | Name | Sev | Description | Detection Signals | DJL Rules | Compliance Refs |
|---|---|---|---|---|---|---|
| AGT-EXF-001 | Database Dump Request | 9 | Agent attempted to extract a bulk dataset or full table contents beyond its authorized scope. | `SELECT * FROM`, `mysqldump`, `pg_dump`, `export all records`, `full table scan`, `DUMP DATABASE` | DJL-SQLI-001, DJL-EXF-001 | NIST-SP-800-53:AC-3, SOC2:CC6.1, GDPR:Art-32, OWASP-LLM-2026:LLM06 |
| AGT-EXF-002 | Unauthorized Outbound Network Call | 9 | Agent initiated an outbound network request to a non-allowlisted host, potentially exfiltrating data to an attacker-controlled endpoint. | `curl http`, `wget http`, `requests.get`, `fetch(`, `non-allowlisted domain`, `outbound connection blocked` | DJL-EXF-002, DJL-EXF-003 | NIST-SP-800-53:SC-7, SOC2:CC6.6, ISO-27001:A.13.1, OWASP-LLM-2026:LLM06 |
| AGT-EXF-003 | PII Aggregation Attack | 8 | Agent correlated PII fields across multiple queries to reconstruct a profile beyond single-query authorization (mosaic / aggregation attack). | `join on email`, `match by phone`, `aggregate across users`, `combine records`, `link identity` | DJL-PII-001, DJL-EXF-004 | GDPR:Art-5, NIST-SP-800-53:AC-4, OWASP-LLM-2026:LLM06, CCPA:1798.100 |

> **Primary source:** OWASP LLM Top 10 2025 — LLM06 (Sensitive Information
> Disclosure). NIST SP 800-53 AC-3 (Access Enforcement) and SC-7 (Boundary
> Protection) govern bulk extraction and unauthorized outbound paths.

---

### Tool Misuse (AGT-MIS)

| Code | Name | Sev | Description | Detection Signals | DJL Rules | Compliance Refs |
|---|---|---|---|---|---|---|
| AGT-MIS-001 | Destructive Tool Invocation | 10 | Agent invoked a tool with an irreversible destructive side-effect: file system wipe (`rm -rf`), database drop (`DROP TABLE`), or equivalent. | `rm -rf`, `DROP TABLE`, `DELETE FROM`, `format disk`, `truncate`, `shred`, `wipe` | DJL-MIS-001, DJL-MIS-002 | NIST-SP-800-53:CM-5, SOC2:CC8.1, ISO-27001:A.12.3, EU-AI-ACT:Art-9 |
| AGT-MIS-002 | Privilege Escalation Attempt | 10 | Agent attempted to elevate its own execution privileges via sudo, su, kernel module loading, container breakout, or equivalent mechanism. | `sudo`, `su root`, `chmod 777`, `insmod`, `docker --privileged`, `nsenter`, `kernel exploit` | DJL-MIS-003, DJL-MIS-004 | NIST-SP-800-53:AC-6, CIS-Controls:v8-5.4, SOC2:CC6.3, EU-AI-ACT:Art-14 |
| AGT-MIS-003 | Unauthorized Transaction | 8 | Agent executed a consequential transaction without required human authorization: PR merge without review, financial transfer, autonomous purchase approval. | `merge pull request`, `approve without review`, `transfer funds`, `submit order`, `auto-approve` | DJL-MIS-005, DJL-POL-001 | NIST-AI-RMF:GOVERN-1.7, EU-AI-ACT:Art-14, SOC2:CC9.1, ISO-27001:A.6.1 |

> **Primary source:** NIST AI RMF GOVERN-1.7 requires accountability mechanisms
> for high-risk autonomous actions. EU AI Act Article 9 mandates risk management
> systems for high-risk AI, including tool-use monitoring.

---

### Financial Misconduct (AGT-FIN)

| Code | Name | Sev | Description | Detection Signals | DJL Rules | Compliance Refs |
|---|---|---|---|---|---|---|
| AGT-FIN-001 | High-Value Financial Transfer | 10 | Agent initiated or facilitated a monetary transfer above a risk-defined threshold without dual-control authorization, triggering AML/fraud-prevention review. | `wire transfer`, `ACH payment`, `high amount`, `large transaction`, `threshold exceeded`, `SWIFT` | DJL-MIS-006, DJL-POL-002 | PCI-DSS:v4-10.7, NIST-SP-800-53:AC-5, SOC2:CC9.1, EU-AI-ACT:Annex-III |
| AGT-FIN-002 | Financial Fraud Pattern | 9 | Agent behaviour matched a known financial fraud pattern: structuring (smurfing), round-trip transactions, invoice manipulation, or anomalous velocity. | `structuring`, `smurfing`, `round-trip`, `split transaction`, `velocity anomaly`, `invoice manipulation` | DJL-POL-003 | PCI-DSS:v4-10.6, NIST-SP-800-53:AU-6, SOC2:CC7.2, FinCEN:31-CFR-1020 |

> **Primary source:** EU AI Act Annex III classifies AI systems used in credit
> scoring and financial risk as high-risk. FinCEN 31 CFR Part 1020 defines
> structuring (smurfing) as a federal AML offense.

---

### Privacy / PII (AGT-PII)

| Code | Name | Sev | Description | Detection Signals | DJL Rules | Compliance Refs |
|---|---|---|---|---|---|---|
| AGT-PII-001 | PII Leakage | 8 | Agent output contained PII (name, SSN, email, phone, address, health record) not consented to be shared with the requesting party. | `SSN`, `social security`, `date of birth`, `home address`, `credit card number`, `medical record`, `passport number` | DJL-PII-002, DJL-PII-003 | GDPR:Art-5, CCPA:1798.100, HIPAA:164.514, NIST-SP-800-53:PL-4, OWASP-LLM-2026:LLM06 |
| AGT-PII-002 | PII Re-identification / Linkage Attack | 9 | Agent successfully or attempted to re-identify an anonymised individual by linking quasi-identifiers, defeating pseudonymisation controls. | `re-identify`, `deanonymize`, `link records`, `quasi-identifier`, `k-anonymity violation`, `reverse lookup` | DJL-PII-004 | GDPR:Recital-26, NIST-SP-800-188:Sec-4, CCPA:1798.140, ISO-27001:A.18.1 |

> **Primary source:** GDPR Recital 26 establishes that pseudonymised data remains
> personal data if re-identification is reasonably possible. NIST SP 800-188
> provides the de-identification process guide referenced by HIPAA safe-harbor.

---

### Governance (AGT-GOV)

| Code | Name | Sev | Description | Detection Signals | DJL Rules | Compliance Refs |
|---|---|---|---|---|---|---|
| AGT-GOV-001 | Policy Bypass | 8 | Agent circumvented an organisational policy control: Lobster Trap deny rule, rate-limit guard, content filter, or data-classification fence — causing a disallowed action to succeed. | `policy bypass`, `filter circumvented`, `deny rule skipped`, `content filter evasion`, `guardrail disabled` | DJL-POL-004, DJL-POL-005 | NIST-AI-RMF:GOVERN-1.1, ISO-27001:A.6.2, SOC2:CC5.2, EU-AI-ACT:Art-9 |
| AGT-GOV-002 | Audit Log Tampering | 10 | Agent attempted to delete, overwrite, suppress, or redirect audit log entries, JSONL forensics records, or telemetry streams to conceal prior actions. | `delete log`, `truncate audit`, `clear history`, `suppress telemetry`, `log rotation exploit`, `audit bypass` | DJL-POL-006 | NIST-SP-800-53:AU-9, SOC2:CC7.3, ISO-27001:A.12.4, EU-AI-ACT:Art-12 |
| AGT-GOV-003 | Human Oversight Bypass | 10 | Agent took a high-risk consequential action without triggering the mandatory human-in-the-loop confirmation gate, violating EU AI Act Article 14 and NIST AI RMF GOVERN-1.7. | `skip confirmation`, `auto-approve high-risk`, `bypass HITL`, `no human review`, `confirmation gate skipped` | DJL-POL-007 | EU-AI-ACT:Art-14, NIST-AI-RMF:GOVERN-1.7, ISO-42001:6.1.2, SOC2:CC9.2 |

> **Primary source:** EU AI Act Article 14 (Human oversight) mandates that
> high-risk AI systems allow natural persons to effectively oversee and intervene.
> NIST AI RMF GOVERN-1.7 requires accountability for autonomous AI actions.
> EU AI Act Article 12 (Record-keeping) requires logging of high-risk AI system
> operation to enable post-hoc auditability.

---

## Design Rationale: Categorical Grouping vs. PLAYBOOK Interleaving

SOAR playbooks (e.g., IBM SOAR, Splunk SOAR built-in templates) commonly
interleave incident types by detection method, producing mixed-category lists
that complicate compliance mapping. For example, a PLAYBOOK template might
group "SQL Injection" with "Privilege Escalation" because both trigger the same
SIEM correlation rule, even though their compliance controls are entirely
different (AC-3 vs. AC-6).

PROBANT's taxonomy keeps categories strict so that:

1. **DJL rules** (US-72) are authored within a single category's namespace
   (e.g., all `DJL-PI-*` rules evaluate prompt injection patterns only).
2. **Compliance mapping** (US-76) assigns framework controls at the family
   level, reducing false cross-mapping.
3. **Industry templates** (US-75) can override severity and DJL rule sets
   per-industry without restructuring the core taxonomy.
4. **SOAR routing** can dispatch on category prefix (`AGT-PI-*` → red-team
   response playbook; `AGT-GOV-*` → governance/legal escalation path).

---

## Compliance Framework Index

| Framework | Version / Date | Coverage in this taxonomy |
|---|---|---|
| OWASP LLM Top 10 | 2025 (Jan 2025) | LLM01, LLM02, LLM06 |
| NIST AI RMF | 1.0 (Jan 2023) | GOVERN-1.1, GOVERN-1.7, MAP-1.1 |
| EU AI Act | OJ L 1689 (Jul 2024) | Art-9, Art-12, Art-14, Annex-III |
| NIST SP 800-53 | Rev 5 (Sep 2020) | AC-3, AC-4, AC-5, AC-6, AU-6, AU-9, CM-5, PL-4, SC-7, SI-3, SI-10 |
| ISO/IEC 27001 | 2022 | A.6.1, A.6.2, A.12.2, A.12.3, A.12.4, A.13.1, A.18.1 |
| ISO/IEC 42001 | 2023 | 6.1.2 |
| SOC 2 Type II | AICPA TSC 2017 | CC5.2, CC6.1, CC6.3, CC6.6, CC7.2, CC7.3, CC8.1, CC9.1, CC9.2 |
| PCI DSS | v4.0 (Mar 2022) | Req 10.6, 10.7 |
| GDPR | 2016/679 | Art-5, Recital-26, Art-32 |
| CCPA | Cal. Civ. Code § 1798 | 1798.100, 1798.140 |
| HIPAA | 45 CFR Part 164 | 164.514 |
| NIST SP 800-188 | 2nd Draft (2024) | Sec-4 |
| FinCEN | 31 CFR Part 1020 | Structuring / AML |
| CIS Controls | v8 (May 2021) | IG2-5.4 |

---

## Related US / Extensions

| US | Description |
|---|---|
| US-72 | DJL rule definitions (`DJL-CAT-NNN` pattern committed in parallel) |
| US-75 | Industry-specific incident templates (extend this taxonomy) |
| US-76 | Full compliance framework expansion |
| US-86 | Final CI gate: cross-resolution of DJL rule IDs against taxonomy |
