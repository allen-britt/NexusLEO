# NexusCore Roadmap

(APEX + AggreGator + Local LLM + Templates + Decision Intelligence)

This roadmap is organized by **priority tier** rather than fixed dates so it stays useful over time.

---

## Phase 0 – Demo & Integration Priority (Short-Term)

Goal: Make NexusCore feel intelligent, integrated, and mission-ready for demos and early users.

### 0.1 Mission-Centric Intelligence Templates

- OSINT report template (picker + preview).
- HUMINT template.
- GEOINT template.
- SIGINT template.
- LEO case template (“Case Pack”).
- Commander decision sheet with blind-spot/policy context.
- Auto-filled sections surfaced via the “Generate intel product” flow, with prose-styled HTML preview and optional TemplateReport debug panel.

Backlog polish:

- Tighten prompts and add a `_clean_markdown` helper in `template_report_service` to keep outputs concise and professional.

### 0.2 Semantic Profiling + Dataset Annotations

- Ensure the mission decision context sidebar clearly exposes:
  - Column semantics
  - Confidence
  - Notes
  - “Regenerate semantics” control
- Make semantic annotations directly support commander-readable insights.

### 0.3 Gap Detection (Initial Version)

- Detect:
  - Missing INTs.
  - Missing time windows.
  - Entities with no supporting data.
- Present a **Gaps Panel** with suggested tasks.

### 0.4 System Status Widget

- Small green/red indicators for:
  - Backend
  - Local LLM
  - AggreGator
- Backed by `/status` health checks.

### 0.5 Docker One-Click Boot

- `docker compose up -d` should:
  - Start all services.
  - Expose the local LLM.
  - Pass backend health checks.
  - Seed demo data where appropriate.

---

## Phase 1 – Near-Term Engineering

Goal: Turn NexusCore from a “cool demo” into a viable product.

### 1.1 First-Class Entities (People, Orgs, Locations)

- Promote core entities into the DB:
  - Person
  - Organization
  - Location (with lat/long normalization)
- Add:
  - Entity dictionaries.
  - Cross-mission linking (“This person appears in 3 missions”).

**Why:** Unlocks mapping, LEO workflows, threat grouping, and link analysis.

### 1.2 Mapping Engine (Basic Version)

Backend:

- Normalize locations (geocoder or LLM).
- Publish mission geo entities via `/missions/{id}/geo`.

Frontend:

- Map panel on mission page.
- Pins for events, entities, sightings.
- Timeline slider to filter events.

### 1.3 Advanced Gap Analysis Engine

- For each INT template, define expected coverage:
  - Time, space, entities.
- Track gap types:
  - Missing INT channels, entities, spatial coverage, time windows.
  - Inconsistent or conflicting data between INTs.
- Persist structured `IntelGaps` in the backend.
- Render gap cards with severity + recommended actions.

### 1.4 Mission “Case Pack” Generator (All INTs Combined)

- Combine OSINT + HUMINT + SIGINT + GEOINT into a single product:
  - Summary sheet
  - Timeline
  - Key entities
  - Threat score
  - Recommended actions
  - Gaps
  - Appendices

### 1.5 Local LLM Model Store & Management

- Implement basic model management endpoints:
  - `/models/install`, `/models/delete`, `/models/set-active`, `/models/list`.
- Support:
  - Ollama model installs.
  - Custom fine-tuned models.
  - Auto-detect running models.

---

## Phase 2 – Mid-Term Expansion

Goal: Add operational depth for LEO + federal use.

### 2.1 LEO-Specific Case Workflow

- “Cases” mode:
  - Case → Persons → Vehicles → Locations.
  - Leads management + prioritization engine (LLM + rules).
  - “Next investigative steps” recommendations.
  - Evidence timeline.
  - Legal gates (warrants, policy constraints).

### 2.2 Policy & Authority Reasoning

Backend:

- Policy knowledge graph.
- Structured rules (“LEO cannot do X without Y”).
- Authority tags per mission.

LLM usage:

- “Is this recommended action compliant with policy?”
- “What alternative action remains legal?”

### 2.3 Realtime Feeds + Sensor Fusion (First Steps)

Support ingestion of:

- Camera metadata.
- ALPR.
- Acoustic/shot-detection sensors.
- Local RMS/CAD exports.
- OSINT streams (RSS, X, Telegram, etc.).

### 2.4 Multi-Agent Reasoning Layer

Agents:

- Extraction agent.
- Gaps agent.
- Collection planning agent.
- COA generator agent.
- Cross-source consistency checker.
- Intel-chief agent (“assemble the final report”).

---

## Phase 3 – Long-Term Vision

Goal: NexusCore becomes a full-blown Intelligence OS.

### 3.1 Knowledge Graph 2.0

- Cross-mission reasoning.
- Risk scoring per entity.
- Relationship strengths.
- Anomaly detection.
- Temporal embedding (“behavior over time”).

### 3.2 Federation Layer

- Query across:
  - Multiple NexusCore nodes.
  - Air-gapped deployments.
  - Field laptops vs HQ servers vs cloud clusters.

### 3.3 Predictive Modeling

- Based on accumulated INTs:
  - Predict locations of future events.
  - Predict behaviors of entities.
  - Suggest pattern-of-life summaries.
  - Provide early warning alerts.

---

## Priority Summary

**Short-term focus**

- Templates for all INTs.
- Gap detection (simple version).
- Semantic profiling UI polish.
- System status indicators.
- Docker one-click deployment.

**Near-term**

- First-class entities.
- Mapping.
- Advanced gap engine.
- Case Pack generator.
- Model management.

**Mid/long-term**

- LEO workflow.
- Policy reasoning.
- Realtime connectors.
- Multi-agent reasoning.
- Cross-mission KG + predictive analytics.
