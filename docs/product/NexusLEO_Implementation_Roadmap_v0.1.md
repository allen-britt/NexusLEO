# NexusLEO Implementation Roadmap v0.1 (DMV-first)

This roadmap assumes the current NexusLEO skeleton exists (FastAPI + Postgres + ingest/extract + claims + audit + export).

---

## Phase 0 (Keep): Current baseline
- Cases
- Documents
- Ingest → mentions/entities/claims/evidence/confidence/audit
- Claims list + export bundle
- Minimal UI

---

## Phase 1 (Next): Officer-first capture (shift + activity logging)

### Purpose
Make the tool useful before any fancy integrations.

### Add (new concepts)
- User (minimal, local-only auth is fine for now)
- ShiftSession (start/end, device id)
- ActivityLogEntry (timestamped log line; links to case optionally)
- Incident/Case creation tied to activity entries
- SourceDocument types expanded: NOTE, AUDIO_TRANSCRIPT, PHOTO_REF, CAD_SNAPSHOT (metadata-only allowed)

### Outputs
- “Shift timeline” view
- “Incident timeline” view
- Faster report drafting inputs

---

## Phase 2: Report drafting (template-driven)

### Purpose
Cut report-writing time without pretending to “solve” cases.

### Add
- ReportTemplate (agency-configurable)
- ReportDraft (generated text + structured fields + citations)
- Draft provenance: which docs/claims used
- Export format(s): JSON now; PDF later

---

## Phase 3: Entity review + resolution workflow

### Purpose
Make ambiguity manageable.

### Add
- Review queue: unresolved hypotheses
- Approve/reject resolution hypotheses
- Immutable history (don’t delete; supersede)

---

## Phase 4: External feeds (DMV starter set)

### Purpose
Bring in “live” signals without boiling the ocean.

### Candidates
- CAD event ingest (as SourceDocuments)
- ALPR hit ingest (as SourceDocuments)
- Simple “be-on-the-lookout” bulletin ingest

Each feed must:
- Store raw payload (or a hashed reference)
- Have timestamps, source id, and provenance metadata

---

## Phase 5: Edge deployment (Jetson / vehicle kit)

### Purpose
Operate offline and sync later.

### Add
- Local DB mode + sync queue
- Local transcription + small model extraction assist
- Admin tooling for model/version management
