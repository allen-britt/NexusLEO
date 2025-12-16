# NexusLEO Platform Doctrine v0.2

**Version:** v0.2  
**Status:** Draft (Implementation-bound)  
**Scope:** DMV MVP Phase 1 (Shift + Activity Logging)

---

## 1. Purpose

NexusLEO is an investigation and reporting workspace that improves capture, organization, and traceability of officer-entered information.

---

## 2. Non-goals (unchanged)

NexusLEO must not:
- recommend arrests or charges
- rank suspects
- produce risk scores or predictive policing outputs
- provide enforcement “next steps”

---

## 3. Officer-first capture (Phase 1)

### Requirements
- Provide fast, timestamped shift logging suitable for daily patrol workflows.
- Preserve human authority: the system records entries and provenance, not judgments.
- Support linking activity entries to cases when provided.

### Data model requirements
- A user represents an operator identity (minimal fields).
- A shift session represents a bounded start/end period for an operator.
- Activity log entries are timestamped records within a shift.

---

## 4. Auditability (delta)

Shift and activity actions must create immutable audit events with:
- stable tool identifier + version
- actor attribution
- deterministic timestamps and ordering

Required actions:
- shift_started
- shift_ended
- activity_logged

---

## 5. Determinism

For identical inputs and versions:
- API ordering must be deterministic
- timelines must be ordered by occurred_at, then created_at, then id

---

**End of NexusLEO Platform Doctrine v0.2**
