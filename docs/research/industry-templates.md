# Apohara PROBANT — Industry Deployment Templates

> **US-75 deliverable** — Apohara PROBANT Fusion Sprint (2026-05-18)
>
> Six pre-configured deployment templates reduce time-to-compliance for regulated verticals.
> Each template wires the SOAR pipeline, DJL rule subset, and compliance report sections
> to the mandatory standards for that industry.
>
> Implementation: `apohara-aegis/apohara_aegis/templates.py`
> Tests: `apohara-aegis/tests/test_industry_templates.py`

---

## Template overview

| Template | Regulatory refs (count) | Mandatory incident codes | DJL rules | Report sections |
|----------|------------------------|--------------------------|-----------|-----------------|
| `finance` | 6 | 5 | 13 | 5 |
| `healthcare` | 6 | 5 | 13 | 5 |
| `government` | 6 | 5 | 14 | 5 |
| `retail` | 5 | 4 | 11 | 4 |
| `manufacturing` | 5 | 5 | 12 | 5 |
| `energy` | 5 | 5 | 14 | 5 |

---

## Finance

**Verticals**: Banks, broker-dealers, payment processors, and fintech platforms.

### Regulatory Refs
`PCI-DSS-4.0` · `SOX` · `GLBA` · `EU-MIFID-II` · `FinCEN-31-CFR-1020` · `NIST-SP-800-53`

### Mandatory Incident Codes
| Code | Name |
|------|------|
| `AGT-FIN-001` | High-Value Financial Transfer |
| `AGT-FIN-002` | Financial Fraud Pattern |
| `AGT-GOV-002` | Audit Log Tampering |
| `AGT-PII-001` | PII Leakage |
| `AGT-EXF-002` | Unauthorized Outbound Network Call |

### Default DJL Rule Subset
`DJL-PI-001` `DJL-PI-002` `DJL-PI-003` `DJL-FIN-001` `DJL-FIN-002` `DJL-FIN-003`
`DJL-EXF-002` `DJL-EXF-003` `DJL-PII-002` `DJL-PII-003` `DJL-POL-002` `DJL-POL-003` `DJL-POL-006`

### Compliance Report Sections
1. PCI-DSS cardholder data flow audit
2. SOX financial reporting controls (Section 404)
3. AML transaction monitoring (FinCEN structuring detection)
4. GLBA data-sharing consent evidence
5. High-value transfer dual-control log

### Use Case Scenario
A bank deploys Apohara PROBANT as a guardrail for its AI-powered treasury agent. The agent
can autonomously reconcile accounts but must request human approval for any wire transfer
above $50,000. PROBANT detects structuring patterns (smurfing: multiple sub-threshold
transfers summing above the limit) via `DJL-POL-003` and fires `AGT-FIN-002`, triggering
an automatic SOAR playbook that freezes the transaction, opens a FinCEN SAR workflow, and
notifies the compliance officer. All actions are written to a SOX 404-compliant HMAC-chained
audit log, satisfying the audit-tamper resistance requirement (`AGT-GOV-002`).

---

## Healthcare

**Verticals**: Hospitals, health insurers, clinical decision-support tools, medical device software.

### Regulatory Refs
`HIPAA-Privacy-Rule` · `HIPAA-Security-Rule` · `HITECH` · `21-CFR-Part-11` · `NIST-SP-800-66` · `EU-MDR-2017-745`

### Mandatory Incident Codes
| Code | Name |
|------|------|
| `AGT-PII-001` | PII Leakage |
| `AGT-PII-002` | PII Re-identification / Linkage Attack |
| `AGT-EXF-003` | PII Aggregation Attack |
| `AGT-GOV-003` | Human Oversight Bypass |
| `AGT-MIS-001` | Destructive Tool Invocation |

### Default DJL Rule Subset
`DJL-PI-001` `DJL-PI-002` `DJL-PI-006` `DJL-PII-001` `DJL-PII-002` `DJL-PII-003`
`DJL-PII-004` `DJL-EXF-001` `DJL-EXF-004` `DJL-MIS-001` `DJL-POL-004` `DJL-POL-006` `DJL-POL-007`

### Compliance Report Sections
1. HIPAA PHI access and disclosure log
2. Breach notification assessment (HITECH §13402)
3. 21-CFR-Part-11 electronic records audit trail
4. De-identification validation (Safe Harbor vs. Expert Determination)
5. Human-in-the-loop gate evidence for clinical decision support

### Use Case Scenario
A healthcare AI assistant answers clinician queries by reading patient records. PROBANT
monitors every cross-patient query for PII aggregation (`AGT-EXF-003`) — if the agent
correlates zip code + age + diagnosis across more than a configurable threshold of records,
a BLOCK verdict fires and a HITECH breach-notification workflow is initiated. The agent
cannot delete EHR entries (`AGT-MIS-001` mandatory) and cannot skip the pharmacist
approval gate for high-risk medication orders (`AGT-GOV-003` mandatory), satisfying EU MDR
software-as-medical-device human oversight requirements.

---

## Government

**Verticals**: Federal agencies, defence contractors, critical infrastructure operators.

### Regulatory Refs
`FedRAMP-Moderate` · `FISMA` · `NIST-SP-800-53-Rev5` · `NIST-SP-800-171` · `CISA-Zero-Trust-Maturity` · `EO-14028`

### Mandatory Incident Codes
| Code | Name |
|------|------|
| `AGT-PI-003` | Indirect Prompt Injection |
| `AGT-MIS-002` | Privilege Escalation Attempt |
| `AGT-GOV-001` | Policy Bypass |
| `AGT-GOV-002` | Audit Log Tampering |
| `AGT-GOV-003` | Human Oversight Bypass |

### Default DJL Rule Subset
`DJL-PI-001` `DJL-PI-002` `DJL-PI-003` `DJL-PI-006` `DJL-PI-007` `DJL-EXF-001`
`DJL-EXF-002` `DJL-EXF-003` `DJL-MIS-003` `DJL-MIS-004` `DJL-POL-004` `DJL-POL-005`
`DJL-POL-006` `DJL-POL-007`

### Compliance Report Sections
1. FedRAMP continuous monitoring evidence
2. FISMA annual security assessment artifacts
3. NIST SP 800-53 Rev5 control satisfaction matrix
4. Privilege escalation attempt log (AC-6)
5. Audit log integrity chain (AU-9 tamper-evidence)

### Use Case Scenario
A federal agency deploys an AI analyst that processes classified documents. PROBANT detects
indirect prompt injection (`AGT-PI-003` mandatory) — an adversary embeds a malicious
instruction in an uploaded PDF that would cause the agent to exfiltrate a summary to an
external URL. PROBANT intercepts the outbound request (`DJL-EXF-002`), issues a BLOCK
verdict, and writes a tamper-evident incident record satisfying NIST SP 800-53 AU-9. Any
attempt by the agent to acquire sudo-level access (`AGT-MIS-002` mandatory) triggers
immediate privilege revocation and an automated CISA-style Zero Trust policy reassessment.

---

## Retail

**Verticals**: E-commerce, brick-and-mortar chains, marketplace platforms.

### Regulatory Refs
`PCI-DSS-4.0` · `CCPA` · `GDPR` · `CAN-SPAM` · `FTC-Act-Section-5`

### Mandatory Incident Codes
| Code | Name |
|------|------|
| `AGT-PII-001` | PII Leakage |
| `AGT-EXF-003` | PII Aggregation Attack |
| `AGT-FIN-002` | Financial Fraud Pattern |
| `AGT-MIS-003` | Unauthorized Transaction |

### Default DJL Rule Subset
`DJL-PI-001` `DJL-PI-002` `DJL-SQLI-001` `DJL-PII-001` `DJL-PII-002` `DJL-PII-003`
`DJL-EXF-002` `DJL-EXF-004` `DJL-MIS-005` `DJL-POL-003` `DJL-POL-004`

### Compliance Report Sections
1. PCI-DSS cardholder data environment scope
2. CCPA consumer rights request log
3. GDPR data subject access request evidence
4. Fraud pattern and velocity anomaly summary

### Use Case Scenario
A retail AI agent personalises promotions and processes returns. PROBANT monitors every
customer data query for PII aggregation (`AGT-EXF-003` mandatory) — if the agent profiles
more customers than a session threshold allows, a REVIEW verdict triggers a CCPA/GDPR data
minimisation check. Fraud pattern detection (`AGT-FIN-002` mandatory) catches promotion
abuse: an attacker scripting hundreds of coupon requests is identified by velocity anomaly
(`DJL-POL-003`) before any refund is issued. Any autonomous order approval above a
configurable cart total fires `AGT-MIS-003`, requiring an extra human-confirmation step
per PCI-DSS 4.0 dual-control requirements.

---

## Manufacturing

**Verticals**: Discrete and process manufacturers, smart factory OT/IT convergence, defence supply chain.

### Regulatory Refs
`NIST-CSF-2.0` · `IEC-62443-3-3` · `ISO-27001-2022` · `CMMC-2.0-Level2` · `EU-CRA-2024`

### Mandatory Incident Codes
| Code | Name |
|------|------|
| `AGT-MIS-001` | Destructive Tool Invocation |
| `AGT-MIS-002` | Privilege Escalation Attempt |
| `AGT-MIS-003` | Unauthorized Transaction |
| `AGT-PI-003` | Indirect Prompt Injection |
| `AGT-EXF-002` | Unauthorized Outbound Network Call |

### Default DJL Rule Subset
`DJL-PI-001` `DJL-PI-003` `DJL-PI-006` `DJL-MIS-001` `DJL-MIS-002` `DJL-MIS-003`
`DJL-MIS-004` `DJL-EXF-002` `DJL-EXF-003` `DJL-POL-001` `DJL-POL-005` `DJL-POL-006`

### Compliance Report Sections
1. IEC 62443-3-3 OT network segmentation evidence
2. NIST CSF 2.0 Respond function incident timeline
3. CMMC Level 2 access control attestation
4. Destructive command invocation log
5. OT/IT boundary crossing anomalies

### Use Case Scenario
A smart factory deploys an AI maintenance agent that can remotely reconfigure CNC machines.
PROBANT guards the OT/IT boundary: any attempt to push firmware across an IEC 62443
security zone (`AGT-MIS-001` mandatory) fires a BLOCK verdict and triggers an automated
NIST CSF 2.0 Respond playbook. Indirect prompt injection (`AGT-PI-003` mandatory) is
critical because malicious G-code comments in supplier files could encode commands;
PROBANT's DJL scans all tool-call responses for embedded instruction patterns before
forwarding them to the machine controller. CMMC Level 2 attestation exports map each
blocked incident to the relevant NIST SP 800-171 control.

---

## Energy

**Verticals**: Electric utilities, oil & gas pipelines, renewable energy operators.

### Regulatory Refs
`NERC-CIP-013-2` · `IEC-62443-2-1` · `NIST-SP-800-82-Rev3` · `EU-NIS2-2022` · `TSA-Security-Directive-2B`

### Mandatory Incident Codes
| Code | Name |
|------|------|
| `AGT-MIS-001` | Destructive Tool Invocation |
| `AGT-MIS-002` | Privilege Escalation Attempt |
| `AGT-GOV-001` | Policy Bypass |
| `AGT-GOV-002` | Audit Log Tampering |
| `AGT-PI-003` | Indirect Prompt Injection |

### Default DJL Rule Subset
`DJL-PI-001` `DJL-PI-003` `DJL-PI-006` `DJL-PI-007` `DJL-MIS-001` `DJL-MIS-002`
`DJL-MIS-003` `DJL-MIS-004` `DJL-EXF-002` `DJL-EXF-003` `DJL-POL-004` `DJL-POL-005`
`DJL-POL-006` `DJL-POL-007`

### Compliance Report Sections
1. NERC CIP-013 supply-chain risk management evidence
2. IEC 62443-2-1 ICS security management evidence
3. NIST SP 800-82 ICS asset inventory and patch status
4. EU NIS2 incident report (72-hour notification timeline)
5. TSA Security Directive 2B cybersecurity architecture assessment

### Use Case Scenario
A utility company deploys an AI operations agent that monitors grid telemetry and can
dispatch automated switching commands. PROBANT enforces NERC CIP-013 supply chain controls:
any firmware update originating from an unapproved supplier triggers `AGT-GOV-001` (policy
bypass), halting the update and opening a TSA Security Directive 2B audit record.
Destructive commands (`AGT-MIS-001` mandatory) — such as tripping a breaker without a
signed work order — are blocked at the DJL layer before reaching the SCADA interface.
When a BLOCK verdict fires on any mandatory incident code, the EU NIS2 72-hour notification
countdown starts automatically and is tracked in the SOAR timeline.
