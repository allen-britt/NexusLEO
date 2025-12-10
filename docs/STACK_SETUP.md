# NexusCore Stack + Mission Workflow Guide

This document fuses a technical stack overview with a practical “how-to” so operators and engineers share the same mental model of what happens when they work a mission.

---

## 1. Stack Snapshot

```
┌────────────┐    HTTP    ┌─────────────┐    gRPC/HTTP    ┌─────────────┐
│ Next.js UI │◄──────────►│ FastAPI API │◄──────────────►│ AggreGator  │
└────────────┘            └─────────────┘                └─────────────┘
        ▲                        ▲  ▲                            ▲
        │                        │  │                            │
        │                        │  │                            │
        │                        │  │                            │
        ▼                Ollama LLMs │                            │
┌────────────┐   docker net   ┌─────┴──────┐                 ┌────┴─────┐
│ Browser    │◄──────────────►│ apex stack │◄───────────────►│ DuckDB KG│
└────────────┘                └────────────┘                 └──────────┘
```

| Component | Tech | Why it matters |
| --- | --- | --- |
| **Frontend** | Next.js / React @ `core/APEX/frontend` | Single mission workspace: tabs, uploads, run button, reports. |
| **Backend API** | FastAPI @ `core/APEX/backend` | Persists missions/docs, orchestrates agent runs, exposes `/missions`, `/documents`, `/agent_runs`, `/template-report`. |
| **Agent Service** | Python service inside backend | Builds prompts, calls LLMs, ingests KG payloads, stores `AgentRun` artifacts. |
| **LLM runtime** | Ollama models (phi-3, mistral) | Provides deterministic structured JSON for facts, gaps, summaries with repair-and-fallback logic. |
| **Knowledge Graph** | AggreGator (FastAPI + DuckDB) | Holds mission namespaces, KG snapshots, node/edge metrics powering gap telemetry. |
| **Storage** | SQLite (`app.db`) for APEX + DuckDB (`aggregator.duckdb`) for KG | Keeps mission state and graph data per namespace; both resettable for clean runs. |

Docker Compose wires these services with health checks so the UI never loads until Ollama + KG + API are ready.

---

## 2. Mission Lifecycle (What + Why)

| Stage | What the user does | What the stack does behind the scenes |
| --- | --- | --- |
| **Create mission** | Fill name, authority lane, INT mix. | `/missions` validates policy, saves mission, and registers a dedicated KG namespace (e.g., `mission-42`). |
| **Load workspace** | Open mission view. | UI fetches mission+docs+runs+datasets+gap analysis in parallel so every tab is hydrated immediately. |
| **Add data** | *Data tab:* paste IIRs. | Stored as `Document` rows; flagged for inclusion so prompts automatically use them next cycle. |
| **Upload sources** | *Sources tab:* drag PDFs / URLs. | File stored, ingest job queued, AggreGator ingests text + metadata, updating KG counts shown in Analysis tab metrics. |
| **Run analysis** | Click Run Analysis on Overview. | FastAPI triggers `run_agent_cycle`: LLM extracts facts/entities/events, pushes structured payloads to KG, generates gaps/summary/next steps/delta, writes `AgentRun` with raw artifacts. |
| **Review insights** | Switch to Analysis / Reports tabs. | UI displays live KG stats, latest gaps, and enables templated report generation using the newest `AgentRun`. |
| **Generate report** | Choose template, click Generate. | Template service composes mission context + latest run, calls LLM for prose, renders HTML/Markdown, stores output for reuse. |

---

## 3. Tab-by-Tab How-To (with backend tie-ins)

1. **Overview tab**
   - *Use it for:* Quick health check (guardrail badge, last run timestamp) and launching fresh analysis.
   - *Stack link:* `<RunAnalysisButton>` → `POST /missions/{id}/analyze` → `run_agent_cycle` (LLM + KG ingest).

2. **Data tab**
   - *Use it for:* Typing/pasting HUMINT snippets or manually managing datasets.
   - *Stack link:* `POST /missions/{id}/documents` writes SQLite rows, automatically included in prompt context (`_build_mission_context`).

3. **Sources tab**
   - *Use it for:* Uploading files/URLs with INT tags.
   - *Stack link:* MissionDocumentService stores the blob, enqueues ingest jobs, and AggreGator ingests JSON -> KG nodes/edges.

4. **Analysis tab**
   - *Use it for:* Watching gap alerts, entity/event explorer, AI/HUMINT panel outputs.
   - *Stack link:* Gap service fetches KG snapshot; `EntitiesEventsView` pulls `/entities` + `/events`; metrics reflect `MissionDataset` and KG counts.

5. **Reports tab**
   - *Use it for:* One-click LEO summary, delta updates, commander sheets.
   - *Stack link:* TemplateReportService composes prompts with guardrails + latest AgentRun and renders final HTML.

---

## 4. Click-Level Trace (Example)

### Scenario: Upload PDF → Run Analysis → Generate Report

1. **Upload PDF**
   - UI → `POST /missions/{id}/documents/upload` (multipart).
   - Backend → saves file, enqueues job, AggreGator ingests text with metadata.
   - Analysis tab soon shows higher KG node/edge counts.

2. **Run Analysis**
   - UI button → `analyzeMission()`.
   - Backend pipeline:
     1. Load mission + `include_in_analysis` docs.
     2. Call LLM (temp=0) for facts; JSON normalized and repaired if needed.
     3. Extract entities/events, ingest to AggreGator (`ingest_json_payload`).
     4. Run gap detection, cross-doc synthesis, summary, next steps, delta.
     5. Persist `AgentRun` (status, guardrail posture, raw_facts, gaps, delta_summary).

3. **Generate Report**
   - UI picks template → `/template-report/generate`.
   - Service pulls mission context, KG snippets, AgentRun outputs; LLM writes Markdown; HTML rendered and stored for download.

---

## 5. Guardrails & Reliability Notes

- **Authority-aware prompts**: `build_analysis_guardrail_rules` tailors instructions (Title 50 vs LEO), ensuring outputs stay inside legal lanes.
- **JSON resilience**: `_normalize_and_parse_json` + `_repair_json_with_utility` strip fences and auto-fix malformed responses before falling back to demo stubs.
- **Namespace isolation**: Every mission gets `mission-{id}` KG namespace, so running multiple missions in parallel never cross-pollinates data.
- **Health monitoring**: Docker health checks keep frontend offline until Ollama, AggreGator, and backend pass `/health` probes.

Use this doc when onboarding new analysts or briefing leadership on both “how to click” and “what systems spring into action” behind each mission workflow.
