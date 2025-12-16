# NexusLEO DMV Product Map v0.1

**Scope:** Maryland + DC + Virginia (DMV) initial target  
**Goal:** Make daily police work faster and more consistent by reducing paperwork + missed connections, while keeping the officer as the decision-maker.

---

## 0. What NexusLEO is (plain language)

NexusLEO is an **AI-enhanced investigation and reporting workspace** that helps officers:

1) Capture information fast (voice or typing)  
2) Organize it into a structured case timeline + entities  
3) Surface connections and “what relates to what” (with evidence pointers)  
4) Produce consistent outputs (report drafts, summaries, exports)

NexusLEO is **not** an enforcement decision-maker:
- No arrest recommendations
- No suspect ranking
- No predictive policing / risk scoring

---

## 1. Users and operating context (DMV-first)

### Primary users
- Patrol officers (shift-based reporting, routine incidents)
- Detectives (multi-document case building, cross-incident linkage)
- Supervisors (review + QA, workload visibility)
- Analysts (optional; later phase)

### What “DMV-first” means
- Start with common incident/report patterns and terminology used across MD/DC/VA agencies.
- Treat local variability as configuration (templates, required fields), not bespoke code paths.

---

## 2. Core workflow (end-to-end)

### 2.1 Shift start → activity capture

Officer logs in, starts a shift, and captures activity with minimal friction:
- “Start shift”
- “New incident / call”
- “Traffic stop”
- “Field interview”
- “Evidence collected”
- “Action taken” (non-prescriptive logging)
- “Close incident”
- “End shift”

Inputs supported:
- Text entry (structured + freeform)
- Voice dictation (transcribe to text; attach audio file hash)
- Attachments (photos, PDFs, CAD printouts, citations) as immutable source docs

### 2.2 Case workspace

A “Case” (or incident) is a container for:
- Source documents (interviews, notes, attachments)
- Extracted mentions/entities/claims
- Timeline of events
- Audit trail of transformations

### 2.3 Knowledge graph (KG) + timeline synthesis

The system continuously builds:
- Entities: people, places, vehicles, phones, organizations, items
- Mentions: span pointers into source documents
- Claims: normalized statements tied to evidence links
- Relationships: entity↔entity and entity↔event linkages

Key behavior:
- Split unless strong evidence to merge
- Preserve ambiguity (multiple candidates, needs review flags)
- Every surfaced connection shows evidence pointers

### 2.4 Analyst assist (non-decision support)

The system can:
- Summarize what the data contains (with citations to sources)
- Highlight inconsistencies/contradictions (without “who is lying” conclusions)
- Produce structured drafts (reports, timelines, interview summaries)

### 2.5 Outputs

- Draft report narrative + structured fields (agency template-driven)
- Case summary with “show your work” evidence pointers
- Export bundle for downstream systems (RMS, case mgmt, discovery later)

---

## 3. Platform components (what exists as modules)

### 3.1 Capture layer (front-end + API)

- Shift session
- Incident creation
- Fast note logging (one-line “I observed…” style)
- Voice dictation ingestion (audio stored + transcript as source doc)
- Attachments ingestion (hash + metadata)

### 3.2 Ingestion + extraction layer (backend)

- Convert source docs → mentions/entities/claims/evidence links
- Deterministic pipeline for baseline reliability
- Optional LLM-assisted extraction later (with strict provenance + confidence)

### 3.3 Entity resolution layer (backend)

- Conservative resolution: split unless strong
- Track hypotheses, not silent merges
- Human review workflow later (approve/reject links)

### 3.4 KG + timeline layer (backend)

- Event timeline generated from claims (time/place/person)
- Query interfaces:
  - “Show me everything about this person”
  - “Show events near this address within timeframe”
  - “Show all mentions of this plate/phone”

### 3.5 Reporting layer (backend + UI)

- Template-driven drafting
- Structured report outputs
- Export bundles (case + docs + claims + audit)

### 3.6 Integrations layer (future)

- External feeds: CAD, RMS, ALPR, CCTV index, etc.
- Controlled connectors, with per-source provenance and timestamps

---

## 4. What makes an officer’s life better (day 1 value)

1) **Less typing:** voice → transcript → structured report fields
2) **Automatic organization:** timeline + entities built continuously
3) **Better recall:** “what did I already have?” across multiple notes/interviews
4) **Consistency:** templates + required fields reduce report rework
5) **Fewer missed links:** system surfaces “this matches that” *with evidence pointers*

---

## 5. On-device / offline feasibility (Jetson-class)

A practical “edge” setup is feasible if we keep expectations grounded:
- Run a **small local model** for transcription + extraction assist
- Keep the authoritative store local (Postgres/SQLite) with periodic sync
- Use RAG over local policy/doctrine/templates for drafting consistency
- Prefer deterministic extraction for baseline, add LLM as “assistant” layer

---

## 6. Non-goals (explicit)

- Predictive policing or risk scoring
- Automated suspect ranking
- Probable cause conclusions
- “Do X next” enforcement recommendations

---

## 7. Success criteria (DMV MVP)

- Officer can log a shift and incidents quickly
- Interview notes become structured entities/claims automatically
- Reports draft in minutes, not hours
- Every key statement can be traced back to a source snippet
- Works offline in a vehicle (degraded mode) and syncs later
