# NexusLEO Discovery & Export Doctrine (v0.1)

**Status:** Authoritative  
**Applies to:** All NexusLEO cases, exports, and externally shared artifacts  
**Effective:** v0.1  
**Last Updated:** 2025-03-XX  

---

## 1. Purpose

This doctrine defines how NexusLEO produces exports that may be used for:

- internal investigative review
- supervisory review
- prosecutorial preparation
- discovery production (when required)
- court exhibits (when applicable)

The primary goals are:

- transparency: “show your work”
- reproducibility: same inputs → same outputs (under same versions)
- completeness: exports include evidence pointers and audit provenance
- non-decisional posture: no recommendations, no legal conclusions

---

## 2. Discovery-Friendly by Design

NexusLEO is designed so that analytical outputs are not “black box” conclusions.

Every exported analytical item must be traceable to:
- source document(s)
- immutable evidence spans
- recorded extraction and confidence method versions
- audit events showing process and actors

NexusLEO does not attempt to hide uncertainty, contradictions, or ambiguity.

---

## 3. Export Classes

NexusLEO supports three export classes, each with explicit constraints.

### 3.1 Class A — Source Export (Raw Materials)

**Contents:**
- original ingested documents (or references)
- document metadata
- source hashes

**Rules:**
- source exports preserve the original content as ingested
- no rewriting, summarization, or transformation
- hash values are included for integrity verification

---

### 3.2 Class B — Analytical Export (Claims + Evidence + Confidence)

**Contents:**
- claims (atomic analytic assertions)
- evidence links (exact source spans)
- confidence assessments with rubric version
- ambiguity flags and alternative hypotheses (if present)
- audit pointers

**Rules:**
- every claim includes evidence pointers
- every confidence rating includes rationale factors and rubric version
- contradictory claims are preserved (if both exist)
- no enforcement recommendations or legal conclusions are included

---

### 3.3 Class C — Governance Export (Certified Snapshot Package)

**Contents:**
- a locked case snapshot (point-in-time)
- the export manifest
- audit trail for all included objects
- dual-control certification metadata (if applicable)

**Rules:**
- Class C exports may only be generated from a locked snapshot
- Class C certification requires symmetric dual-control (per Supervisor Review Mode)
- certification governs completeness of the package, not truth of the content

---

## 4. Export Preconditions

### 4.1 Default Preconditions

For any export beyond Class A:
- the case must have a known case identifier
- included objects must have stable IDs
- all included objects must have audit provenance

### 4.2 Certified Export Preconditions (Class C)

Class C exports require:
- a locked snapshot identifier
- two independent supervisory approvals (symmetric dual-control)
- an export manifest recording included object IDs and hashes (where applicable)

---

## 5. Export Manifest

Every export includes a machine-readable manifest describing:

- export ID
- case ID
- export class (A/B/C)
- timestamp
- actor identity (and dual approvers if Class C)
- tool and version identifiers
- included object lists:
  - document IDs (+ hashes)
  - claim IDs
  - mention IDs
  - entity IDs
  - confidence assessment IDs
  - resolution hypothesis IDs
  - audit event IDs

The manifest is the authoritative index of “what was produced.”

---

## 6. Reproducibility and Versioning

Every export records:

- tool name(s) and version(s)
- confidence rubric version
- extraction method version
- database schema/migration version (where applicable)

Reproducibility means:

> Given the same source inputs and the same tool/rubric versions, NexusLEO can regenerate the same analytical export content.

If the toolchain changes, NexusLEO does not overwrite historical exports.
Instead it produces new exports under the new version, with clear labeling.

---

## 7. Redactions and Sensitive Data Handling

NexusLEO may support redaction workflows, but in v0.1:

- NexusLEO itself does not “decide” what must be redacted
- redaction decisions belong to authorized personnel and legal process
- if redactions are applied, the export must record:
  - who applied them
  - when
  - under what authority or policy reference
  - what was altered (without destroying provenance)

Redaction must not silently remove audit history.

---

## 8. What NexusLEO Will Not Export

NexusLEO exports shall not include:

- suspect rankings
- risk scores
- predictions or forecasts
- recommendations to arrest, charge, search, seize, or surveil
- determinations of probable cause
- conclusions of guilt, intent, or culpability

NexusLEO is an analytical support platform and remains non-decisional.

---

## 9. Plain-Language Court Explanation

If asked to explain exports in court:

> “NexusLEO exports are structured packages of what was already entered and what the system derived from it. Every derived statement is linked to specific source text, and the system leads reviewers back to the original evidence. When a package is certified, two supervisors independently approve that the export is complete and properly packaged. Certification does not claim the information is true—only that it is correctly collected and traceable.”

---

## 10. Change Control

Any changes to export behavior require:
- doctrine version bump
- mapping update (Doctrine → Code Mapping)
- explicit rationale in changelog

Historical exports retain the rules and versions used at time of creation.

---
