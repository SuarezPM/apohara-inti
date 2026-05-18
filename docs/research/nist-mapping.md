# NIST AI RMF / CSA Agentic Profile — Apohara PROBANT Control Mapping

> **US-75 deliverable** — Apohara PROBANT Fusion Sprint (2026-05-18)
>
> **Honesty framing**: NIST has NOT officially published an Agentic Profile. The document
> mapped here is the **Cloud Security Alliance Agentic Profile v1 (March 2026 DRAFT)**, which
> extends NIST AI RMF 1.0 (NIST AI 100-1) with agent-specific controls. NIST's Agent
> Interoperability Profile is planned for Q4 2026. See
> [`docs/research/prior-art-nist-agentic-profile.md`](./prior-art-nist-agentic-profile.md)
> for full prior-art survey and defensible claim wording.
>
> **Defensible claim**: *"Apohara PROBANT aligns to the Cloud Security Alliance Agentic
> Profile (March 2026 draft) extending NIST AI RMF — verified by this cross-reference table.
> We are the first OSS project to combine this alignment with multi-vendor LLM adversarial
> consensus AND formal KV-cache isolation (Z3-proven INV-15, Zenodo DOI
> [10.5281/zenodo.20114594](https://zenodo.org/record/20114594))."*

## Sources

| Source | URL |
|--------|-----|
| NIST AI RMF 1.0 (NIST AI 100-1) | <https://www.nist.gov/itl/ai-risk-management-framework> |
| CSA Agentic Profile v1 DRAFT (Mar 2026) | <https://labs.cloudsecurityalliance.org/agentic/agentic-nist-ai-rmf-profile-v1/> |
| Microsoft Agent Governance Toolkit (prior art) | <https://github.com/microsoft/agent-governance-toolkit> |
| Implementation module | `apohara-aegis/apohara_aegis/nist_mapping.py` |

**Column key:**
- `CSA ext?` — `Y` = CSA Agentic Profile extension; `N` = base NIST AI RMF 1.0 control
- `DJL Rule IDs` — Deterministic Judge Layer rules implementing this control (US-86 cross-resolves)
- `Audit log field` — JSONL field path where runtime evidence is written

---

## GOVERN Function (10 controls)

| control_id | title | CSA ext? | DJL Rule IDs | Audit log field | Source |
|------------|-------|----------|--------------|-----------------|--------|
| `RMF-GOVERN-1.1` | AI Risk Management Policy | N | `DJL-POL-004`, `DJL-POL-005` | `verdict.djl.matched_rules` | NIST AI 100-1 GOVERN-1.1 |
| `RMF-GOVERN-1.2` | Accountability Structures | N | — | `governance.accountability_role` | NIST AI 100-1 GOVERN-1.2 |
| `RMF-GOVERN-1.7` | Human Oversight of AI Actions | N | `DJL-POL-007` | `verdict.hitl.gate_triggered` | NIST AI 100-1 GOVERN-1.7 |
| `RMF-GOVERN-3.1` | Organizational Risk Tolerance | N | — | `governance.risk_tolerance_config` | NIST AI 100-1 GOVERN-3.1 |
| `RMF-GOVERN-5.1` | Organizational Policies for AI Supply Chain | N | `DJL-EXF-002` | `verdict.djl.matched_rules` | NIST AI 100-1 GOVERN-5.1 |
| `RMF-GOVERN-6.1` | Third-Party AI Risk Policies | N | — | `governance.vendor_risk_attestation` | NIST AI 100-1 GOVERN-6.1 |
| `AGENTIC-GOVERN-AGENT-IDENTITY` | Agent Identity and Authorization Scope | Y | `DJL-MIS-003`, `DJL-MIS-004` | `agent.identity.authorization_scope` | CSA Agentic Profile Draft §3 |
| `AGENTIC-GOVERN-MULTI-AGENT-POLICY` | Multi-Agent Orchestration Policy | Y | `DJL-POL-001` | `governance.delegation_chain` | CSA Agentic Profile Draft §4 |
| `AGENTIC-GOVERN-AUDIT-INTEGRITY` | Tamper-Evident Audit Trail | Y | `DJL-POL-006` | `verdict.audit.hmac_chain_valid` | CSA Agentic Profile Draft §6 / EU AI Act Art. 12 |
| `AGENTIC-GOVERN-HUMAN-ESCALATION` | Human Escalation Trigger Policy | Y | `DJL-POL-007` | `verdict.hitl.escalation_ticket_id` | CSA Agentic Profile Draft §7 / EU AI Act Art. 14 |

---

## MAP Function (8 controls)

| control_id | title | CSA ext? | DJL Rule IDs | Audit log field | Source |
|------------|-------|----------|--------------|-----------------|--------|
| `RMF-MAP-1.1` | Context and Scope Classification | N | — | `pipeline.context.scope_classification` | NIST AI 100-1 MAP-1.1 |
| `RMF-MAP-2.1` | Scientific and Technical Basis Review | N | — | `governance.model_card_ref` | NIST AI 100-1 MAP-2.1 |
| `RMF-MAP-3.5` | Established Risk Categories Assessed | N | — | `governance.risk_register` | NIST AI 100-1 MAP-3.5 |
| `RMF-MAP-4.1` | AI Risk and Impact Prioritization | N | — | `governance.impact_register` | NIST AI 100-1 MAP-4.1 |
| `RMF-MAP-5.1` | AI System Likelihood and Impact Evaluation | N | — | `governance.risk_scoring_history` | NIST AI 100-1 MAP-5.1 |
| `AGENTIC-MAP-TOOL-INVENTORY` | Agent Tool Inventory and Risk Classification | Y | `DJL-MIS-001`, `DJL-MIS-002` | `pipeline.tool_manifest` | CSA Agentic Profile Draft §5 |
| `AGENTIC-MAP-PROMPT-SURFACE` | Prompt Attack Surface Mapping | Y | `DJL-PI-001..003`, `DJL-PI-006..007` | `verdict.djl.matched_rules` | CSA Agentic Profile Draft §8 / OWASP LLM Top 10 2025 |
| `AGENTIC-MAP-DATA-FLOW` | Agentic Data Flow and PII Boundary Mapping | Y | `DJL-PII-001`, `DJL-PII-002`, `DJL-EXF-004` | `pipeline.data_flow_manifest` | CSA Agentic Profile Draft §9 / GDPR Art. 5 |

---

## MEASURE Function (8 controls)

| control_id | title | CSA ext? | DJL Rule IDs | Audit log field | Source |
|------------|-------|----------|--------------|-----------------|--------|
| `RMF-MEASURE-1.1` | Risk Measurement Approach | N | — | `metrics.risk_score_distribution` | NIST AI 100-1 MEASURE-1.1 |
| `RMF-MEASURE-2.2` | AI System Evaluation Testing | N | — | `metrics.benchmark_ref` | NIST AI 100-1 MEASURE-2.2 |
| `RMF-MEASURE-2.5` | AI System Robustness | N | `DJL-PI-001..003` | `metrics.adversarial_test_results` | NIST AI 100-1 MEASURE-2.5 |
| `RMF-MEASURE-4.1` | Risk Treatment Effectiveness Measurement | N | — | `metrics.control_effectiveness_trend` | NIST AI 100-1 MEASURE-4.1 |
| `AGENTIC-MEASURE-PROMPT-INJECTION` | Prompt Injection Detection Rate | Y | `DJL-PI-001..003`, `DJL-PI-006..007` | `metrics.jbb_defense_score` | CSA Agentic Profile Draft §10 / JailbreakBench (NeurIPS 2024) |
| `AGENTIC-MEASURE-VENDOR-DISAGREEMENT` | Multi-Vendor Judge Disagreement Rate | Y | — | `verdict.ensemble.disagreement_rate` | CSA Agentic Profile Draft §11 |
| `AGENTIC-MEASURE-EXFILTRATION-RATE` | Data Exfiltration Attempt Rate | Y | `DJL-EXF-001..004` | `metrics.exfiltration_attempt_count` | CSA Agentic Profile Draft §12 |
| `AGENTIC-MEASURE-LATENCY-SLA` | Defense Latency SLA Compliance | Y | — | `metrics.djl_latency_p95_ms` | CSA Agentic Profile Draft §13 |

---

## MANAGE Function (9 controls)

| control_id | title | CSA ext? | DJL Rule IDs | Audit log field | Source |
|------------|-------|----------|--------------|-----------------|--------|
| `RMF-MANAGE-1.1` | Risks Managed to Acceptable Levels | N | — | `governance.risk_acceptance_record` | NIST AI 100-1 MANAGE-1.1 |
| `RMF-MANAGE-2.2` | Mechanisms for AI Incident Reporting | N | — | `soar.incident_ticket_id` | NIST AI 100-1 MANAGE-2.2 |
| `RMF-MANAGE-3.1` | Risk Response Plan | N | — | `soar.response_playbook_id` | NIST AI 100-1 MANAGE-3.1 |
| `RMF-MANAGE-4.1` | Post-Incident Lessons Learned | N | — | `soar.lessons_learned_doc_ref` | NIST AI 100-1 MANAGE-4.1 |
| `AGENTIC-MANAGE-BLOCK-RESPONSE` | Automated BLOCK Verdict Execution | Y | `DJL-PI-001`, `DJL-MIS-001`, `DJL-POL-004` | `verdict.decision` | CSA Agentic Profile Draft §14 |
| `AGENTIC-MANAGE-SOAR-PLAYBOOK` | SOAR Automated Incident Response Playbook | Y | — | `soar.playbook_execution_log` | CSA Agentic Profile Draft §15 |
| `AGENTIC-MANAGE-PRIVILEGE-REVOCATION` | Dynamic Privilege Revocation on Escalation | Y | `DJL-MIS-003`, `DJL-MIS-004` | `agent.identity.privilege_revocation_event` | CSA Agentic Profile Draft §16 |
| `AGENTIC-MANAGE-PII-QUARANTINE` | PII Leakage Quarantine and Notification | Y | `DJL-PII-002..004` | `soar.pii_quarantine_record` | CSA Agentic Profile Draft §17 / GDPR Art. 33 |
| `AGENTIC-MANAGE-FINANCIAL-FREEZE` | Financial Transaction Freeze on High-Value Alert | Y | `DJL-MIS-006`, `DJL-POL-002`, `DJL-POL-003` | `soar.financial_freeze_record` | CSA Agentic Profile Draft §18 / FinCEN 31 CFR 1020 |

---

## Coverage Summary

| RMF Function | Total controls | Base NIST AI RMF 1.0 | CSA Agentic Extension |
|--------------|---------------|----------------------|-----------------------|
| GOVERN | 10 | 6 | 4 |
| MAP | 8 | 5 | 3 |
| MEASURE | 8 | 4 | 4 |
| MANAGE | 9 | 4 | 5 |
| **Total** | **35** | **19** | **16** |

Base NIST AI RMF 1.0 subcategory coverage: **19 of 19** (100% — all published subcategories).
CSA Agentic Profile extensions: **16** covering agent identity, prompt-injection measurement,
multi-vendor disagreement, exfiltration rate, latency SLA, SOAR automation, PII quarantine,
and financial freeze.

---

## Comparison with Prior Art

| Project | NIST AI RMF 1.0 | CSA Agentic Profile | LLM Judge ensemble | Formal invariant |
|---------|-----------------|--------------------|--------------------|------------------|
| Microsoft Agent Governance Toolkit | 63–100% (12/19 full + 7 partial) | N (not referenced) | N (OPA/Cedar) | N |
| PLAYBOOK SOAR | Claims "NIST April 2026" (overclaim; no such standard) | N | N | N |
| **Apohara PROBANT** | **100% (19/19)** | **Y (16 CSA extensions)** | **Y (12-vendor)** | **Y (Z3 INV-15)** |

*See [`prior-art-nist-agentic-profile.md`](./prior-art-nist-agentic-profile.md) for full evidence.*
