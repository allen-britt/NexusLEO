# NexusLEO Doctrine → Code Mapping (v0.1)

**Document Type:** Doctrine-to-Implementation Mapping  
**System:** NexusLEO  
**Version:** v0.1  
**Status:** Frozen  
**Last Updated:** 2025-09-12  

> ⚠️ This document is authoritative.  
> If implementation behavior conflicts with this mapping, **the mapping prevails**.  
> Any behavior not explicitly mapped **does not exist** in NexusLEO.

---

## 1. Purpose

This document binds NexusLEO **Platform Doctrine v0.1** and all v0.1 appendices to concrete backend responsibilities.

It exists to:
- prevent doctrinal drift
- enforce non-decisional behavior
- ensure prosecutorial and judicial survivability
- constrain future development

---

## 2. Doctrine §§1–2: Purpose, Scope, Non-Goals

### Doctrine Requirements
- Analytical assistance only
- No decision-making
- No enforcement recommendations
- No intelligence-community framing
- No suspect ranking, scoring, or prediction

### Code Enforcement
- No API response may include:
  - recommendations
  - next steps
  - risk scores
  - suspect prioritization
  - probability of guilt
- No services may implement decision logic

**Enforced in:**
- `backend/app/api/routes/*`
- `backend/app/services/*`

Absence of such logic is a hard constraint.

---

## 3. Doctrine §3: Human Authority & Responsibility

### Doctrine Requirements
- Humans own data validity
- Humans own decisions
- System records attribution, not judgment

### Code Alignment
- `SourceDocument`
  - `raw_text`
  - `sha256`
  - `metadata_json`
- `AuditEvent`
  - `actor`
  - `action`
  - `created_at`

Every ingest, extraction, assessment, and governance action is attributed and logged.

---

## 4. Doctrine §4: Evidence Handling & Chain of Custody

### Doctrine Requirements
- Immutable source material
- Hashing at ingest
- Full provenance from claim → source

### Code Alignment
- `SourceDocument.sha256`
- `Mention.document_id`
- `EvidenceLink.mention_id`
- `Claim.case_id`

Canonical chain:

**Claim → EvidenceLink → Mention → SourceDocument**

No mutation of ingested source text is permitted.

---

## 5. Doctrine §5: Claims-First Analytical Model

### Doctrine Requirements
- No claims without evidence
- Claims are atomic analytical assertions

### Code Alignment
- `Claim`
- `EvidenceLink`

**Hard rule:**  
A `Claim` must have ≥1 `EvidenceLink`.  
Claims cannot exist independently.

---

## 6. Doctrine §6: Entity Representation & Resolution

### Doctrine Requirements
- Conservative resolution
- Ambiguity preserved
- No silent merges

### Code Alignment
- `Entity`
- `ResolutionHypothesis`
  - `status = UNREVIEWED | ACCEPTED | REJECTED`
  - `score`
  - `features_json`

Multiple candidate entities may coexist.  
Resolution is explicit and reviewable.

---

## 7. Doctrine §7 + Confidence Rubric Appendix v0.1

### Doctrine Requirements
- Confidence reflects evidentiary support, not probability
- Deterministic rubric
- Transparent rationale
- Visual semantics allowed (non-functional)

### Code Alignment
- `ConfidenceAssessment`
  - `level = HIGH | MODERATE | LOW`
  - `rubric_version`
  - `factors_json`
  - `rationale_text`

### Enforcement Rules
- Confidence cannot be manually edited
- Confidence recalculation only via rubric logic
- No probabilistic scoring

### UI Semantics (Presentation Only)
- HIGH → Green
- MODERATE → Yellow
- LOW → Red
- UNDETERMINED → Grey

Color has **no analytical meaning**.

---

## 8. Doctrine §8: AI Behavior Constraints

### Doctrine Requirements
- No asserted facts
- No stochastic inference
- Reproducible outputs

### Code Alignment
- Deterministic extraction rules only
- No ML / LLM inference in v0.1
- Tool + version identifiers recorded in `AuditEvent`

Given identical inputs and versions, outputs must be identical.

---

## 9. Doctrine §9: Auditability

### Doctrine Requirements
- Every analytical step logged
- Audit trail is immutable and discoverable

### Code Alignment
- `AuditEvent` with actions:
  - `ingest_started`
  - `extraction_completed`
  - `confidence_assessed`
  - `ingest_completed`
  - `governance_action` (Tier 2)
  - `export_certified`

Audit records:
- cannot be edited
- cannot be deleted
- are exportable

---

## 10. Supervisor Review Mode v0.1 → Code Mapping

### Authority Tiers
- Tier 1: Soft Governance (single reviewer)
- Tier 2: Hard Governance (dual-control)

### Code Responsibilities
- Tier 1:
  - annotations
  - flags
  - review markers
- Tier 2:
  - snapshot locking
  - export certification

### Dual-Control Enforcement
- Two distinct authenticated users
- Symmetric approval (order independent)
- Time-bounded concurrence window
- Separate audit entries per approver

No Tier 2 action completes with a single actor.

---

## 11. Discovery & Export Doctrine v0.1 → Code Mapping

### Export Classes
- **Class A:** Source Export
- **Class B:** Analytical Export
- **Class C:** Certified Snapshot Export

### Export Manifest (Required)
Each export must generate a manifest containing:
- export_id
- case_id
- export_class
- timestamp
- tool + version identifiers
- included object IDs
- audit event IDs
- approver identities (Class C only)

### Enforcement
- Class C exports require:
  - locked snapshot
  - symmetric dual-control
- Historical exports are immutable
- New versions generate new exports

---

## 12. Visibility & Operator Awareness

### Doctrine Requirements
- No hidden analysis
- Operators understand process

### Code Alignment
- Doctrine and rubric intended to be embedded in UI
- Audit events queryable by operators
- Confidence rationale always visible

---

## 13. Explicit Non-Existence Rules

The following **must not exist** in NexusLEO v0.1:

- suspect rankings
- risk or threat scores
- predictive analytics
- enforcement recommendations
- probable cause indicators
- guilt or intent assertions

Any PR introducing these violates doctrine.

---

## 14. Enforcement Rule (Binding)

Any future feature, PR, or refactor must:

1. Cite the doctrine section it satisfies
2. Update this mapping if behavior changes
3. Bump doctrine version if intent changes

Unmapped behavior is invalid by definition.

---

**End of NexusLEO Doctrine → Code Mapping v0.1**
