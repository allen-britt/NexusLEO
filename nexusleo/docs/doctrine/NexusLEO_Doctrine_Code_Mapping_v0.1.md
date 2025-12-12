# NexusLEO Doctrine → Code Mapping v0.1

**Document Type:** Doctrine-to-Implementation Mapping  
**System:** NexusLEO  
**Version:** v0.1  
**Status:** Frozen  
**Last Updated:** 2025-09-12  

> ⚠️ This document binds doctrine to implementation.  
> If code behavior conflicts with this mapping, the mapping prevails.

---

## 1. Purpose

This document maps **NexusLEO Platform Doctrine v0.1** to concrete backend artifacts.  
Any behavior not explicitly mapped here **does not exist** in the system.

---

## 2. Doctrine §§1–2: Purpose, Scope, Non-Goals

### Doctrine Requirements
- Assistive, not decision-making
- No enforcement recommendations
- No intelligence analysis framing

### Code Enforcement
- No endpoints return actions, recommendations, or suspect rankings
- Absence of decision logic in:
  - `backend/app/services/*`
  - `backend/app/api/routes/*`

---

## 3. Doctrine §3: Human Authority and Responsibility

### Doctrine Requirements
- Humans own decisions and input validity
- System records attribution

### Code Alignment
- `SourceDocument`
  - `sha256`
  - `raw_text`
  - `metadata_json`
- `AuditEvent`
  - `actor`
  - `action`
  - `created_at`

All ingest and analytic steps are logged with authenticated context.

---

## 4. Doctrine §4: Evidence Handling & Chain of Custody

### Doctrine Requirements
- Immutable sources
- Hashing at ingest
- Full provenance

### Code Alignment
- `SourceDocument.sha256`
- `EvidenceLink.mention_id`
- `Mention.document_id`
- `Claim.case_id`

Chain: **Claim → EvidenceLink → Mention → SourceDocument**

---

## 5. Doctrine §5: Claims-First Model

### Doctrine Requirements
- No claims without evidence

### Code Alignment
- `Claim`
- `EvidenceLink`

Claims cannot exist without at least one evidence link.

---

## 6. Doctrine §6: Entity Representation

### Doctrine Requirements
- Conservative resolution
- Ambiguity preserved

### Code Alignment
- `Entity`
- `ResolutionHypothesis`
  - `status = UNREVIEWED | ACCEPTED | REJECTED`

No fuzzy matching or silent merges.

---

## 7. Doctrine §7: Confidence Standard

### Doctrine Requirements
- Evidence quality, not probability
- Deterministic rubric
- Color semantics

### Code Alignment
- `ConfidenceAssessment`
  - `level = HIGH | MODERATE | LOW`
  - `rubric_version`
  - `factors_json`
  - `rationale_text`

Color mapping applied at UI layer:
- HIGH → Green
- MODERATE → Yellow
- LOW → Red
- UNDETERMINED → Grey

---

## 8. Doctrine §8: AI Behavior Constraints

### Doctrine Requirements
- No asserted facts
- Reproducible outputs

### Code Alignment
- Deterministic rule-based extraction
- No stochastic processes
- Versioned tool identifiers in `AuditEvent`

---

## 9. Doctrine §9: Auditability

### Doctrine Requirements
- Every analytic step logged

### Code Alignment
- `AuditEvent` records:
  - ingest_started
  - extraction_completed
  - confidence_assessed
  - ingest_completed

Audit events are queryable and exportable.

---

## 10. Doctrine §§10–12: Discovery, Governance, Visibility

### Code Alignment
- Full export via API
- Versioned methods and rubrics
- Doctrine intended to be embedded in operator interface

---

## 11. Enforcement Rule

Any future feature or PR must:

1. Cite the doctrine section it satisfies
2. Update this mapping if behavior changes
3. Bump doctrine version if intent changes

---

**End of NexusLEO Doctrine → Code Mapping v0.1**
