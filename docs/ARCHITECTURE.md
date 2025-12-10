# NexusCore / APEX / AggreGator – Architecture

This document explains how the UI, backend, knowledge graph, and LLM runtime fit together and what happens when an analyst works a mission.

---

## 1. High-Level Architecture

```
                   ┌─────────────────────────────────────┐
                   │            Operator Browser         │
                   │      http://localhost:3000          │
                   └─────────────────────────────────────┘
                                   │  HTTP (JSON)
                                   ▼
                   ┌─────────────────────────────────────┐
                   │          APEX Frontend (Next.js)    │
                   │  - Next.js 14, React, TS, Tailwind  │
                   │  - Routes: /missions, /reports, …   │
                   └─────────────────────────────────────┘
                                   │  HTTP (REST / JSON)
                                   ▼
                   ┌─────────────────────────────────────┐
                   │          APEX Backend (FastAPI)     │
                   │  - Missions, documents, datasets    │
                   │  - Agent runs, gap analysis,       │
                   │    templated reports, status        │
                   └─────────────────────────────────────┘
                        │               │              │
                        │               │              │
                        │ HTTP          │ HTTP         │ HTTP
                        ▼               ▼              ▼
            ┌──────────────────┐  ┌────────────────┐  ┌────────────────────┐
            │  Mission Storage │  │ AggreGator KG  │  │    Ollama LLMs     │
            │  (SQLite/Postgres)│ │  (DuckDB/parquet)│ │  (mistral, phi3…) │
            └──────────────────┘  └────────────────┘  └────────────────────┘
```

- **APEX Frontend** – Mission-centric React UI (tabs: Overview, Data, Sources, Analysis, Reports).
- **APEX Backend** – FastAPI app that:
  - Persists missions, documents, datasets, and agent runs.
  - Orchestrates the LLM / KG workflows (“agent cycle”).
  - Generates templated mission reports with guardrail + KG context.
- **AggreGator** – Data fabric + knowledge graph using DuckDB/parquet.
- **LLM Runtime** – Ollama models that return structured JSON; outputs run through normalization + repair before being accepted.
- **Mission Storage** – SQLite/Postgres for APEX data; DuckDB/parquet for KG.

---

## 2. Tech Stack

| Layer | Technologies / Details |
| --- | --- |
| **Frontend (APEX)** | Next.js 14 (App Router), React 18, TypeScript, Tailwind, Node 18; fetch-based API client (`lib/api.ts`). |
| **Backend (APEX)** | FastAPI, SQLAlchemy, Pydantic v2, httpx, pytest / pytest-asyncio. |
| **Data Fabric** | AggreGator – FastAPI, DuckDB, Pandas, PyArrow, YAML source registry; profiling + KG endpoints. |
| **LLM Runtime** | Ollama (mistral, phi3, others) via HTTP chat API. |
| **Storage** | SQLite (demo) or PostgreSQL (missions/docs/runs); DuckDB/parquet for KG. |
| **Orchestration** | Docker Compose for local demo; optional external services for bulk ingestion. |
| **Tooling** | pnpm/npm, uvicorn, pytest, Python logging. |

---

## 3. Runtime Topology (Docker Demo)

Default ports and env wiring:

| Service | Port | Key env variables |
| --- | --- | --- |
| Ollama | 11434 | `LLM_MISTRAL_URL`, `LLM_PHI3_URL` (backend) |
| AggreGator | 8100 | `AGGREGATOR_BASE_URL` (backend) |
| APEX Backend | 8000 | `APEX_INTERNAL_API_BASE_URL`, `NEXT_PUBLIC_APEX_API_BASE_URL` (frontend) |
| APEX Frontend | 3000 | Browser entrypoint |

Internal contracts:

- Frontend SSR → Backend: `APEX_INTERNAL_API_BASE_URL=http://apex-backend:8000`
- Browser → Backend: `NEXT_PUBLIC_APEX_API_BASE_URL=http://localhost:8000`
- Backend → AggreGator: `AGGREGATOR_BASE_URL=http://aggregator:8100`
- Backend → LLM: `LLM_MISTRAL_URL`, `LLM_PHI3_URL=http://ollama:11434`

Health checks ensure the frontend waits for Ollama + AggreGator + backend readiness.

---

## 4. Mission Workspace Flow

The mission workspace at `/missions/[id]` uses five tabs that all share the same data bundle (mission, documents, datasets, agent runs, gap analysis).

| Tab | Primary components | Backend endpoints |
| --- | --- | --- |
| Overview | `MissionDetail`, `RunAnalysisButton`, `AgentSummary`, `GuardrailBadge` | `/missions/{id}`, `/missions/{id}/agent_runs`, `/missions/{id}/analyze` |
| Data | `DocumentForm`, `DocumentList`, `MissionDatasetList`, `MissionDatasetForm` | `/missions/{id}/documents`, `/missions/{id}/datasets` |
| Sources | `MissionSourcesTab` | `/missions/{id}/documents/upload`, `/missions/{id}/source_docs` |
| Analysis | `GapsPriorities`, `GapAnalysisPanel`, `EntitiesEventsView`, `AIAnalysisPanel`, `HumintAnalysisPanel` | `/missions/{id}/analysis`, KG proxy routes |
| Reports | `TemplateReportPanel`, `TemplateReportGenerator` | `/missions/{id}/reports`, `/template-report/*` |

### Mission Lifecycle

1. **Create mission** – `POST /missions` saves metadata and initializes a unique KG namespace (`mission-{id}`) in AggreGator.
2. **Add documents** – `POST /missions/{id}/documents` stores analyst-entered text. `include_in_analysis` defaults to true, so no extra toggles are needed.
3. **Upload sources** – File/URL uploads use MissionDocumentService to persist blobs, enqueue ingest jobs, and send text to AggreGator (updating KG metrics).
4. **Run analysis** – `POST /missions/{id}/analyze` triggers `run_agent_cycle`:
   - Load mission + documents + KG snapshot.
   - Extract facts, entities, events via LLM with strict guardrails.
   - Ingest structured payloads into AggreGator.
   - Generate gaps, summary, next steps, delta.
   - Persist a new `AgentRun` with `raw_facts`, `gaps`, `delta_summary`, guardrail posture.
5. **Review insights** – Analysis tab shows KG stats, recent runs, HUMINT/AI outputs. Reports tab uses the latest AgentRun for templated products.

---

## 5. Data Model Highlights

### Mission & Documents

- **Mission**: `id`, `name`, `description`, `primary_authority`, `int_types`, `kg_namespace`, timestamps.
- **Document**: `id`, `mission_id`, `title`, `content`, `include_in_analysis`, metadata.

### AgentRun

Each agent cycle persists:

- **status** – `queued`, `running`, `completed`, or `error`.
- **summary** – narrative for the Analysis tab and reports.
- **next_steps** – follow-on actions.
- **guardrail_status / guardrail_issues** – policy posture.
- **raw_facts** – structured list of factual statements.
- **gaps** – structured gap items with recommended questions.
- **delta_summary** – narrative comparison vs. previous run (or baseline).

These objects feed the mission Analysis tab, TemplateReportService, and downstream APIs.

---

## 6. Health & Status

`GET /status` returns:

```json
{
  "overall": "ok",
  "backend": "ok",
  "aggregator": "ok",
  "llm": "ok"
}
```

- Backend: request itself.
- AggreGator: `/health` ping.
- LLM: a light chat ping.

The frontend surfaces this in the `SystemStatusBar` so operators can see dependency health.

---

## 7. LLM JSON Handling & Guardrails

- Structured analytic calls forbid markdown fences and chatter, require a single JSON object/array, and clamp temperature to 0.0.
- `_normalize_and_parse_json` strips fences + preamble and slices from the first brace.
- `_repair_json_with_utility` uses a smaller LLM to fix malformed JSON before falling back to deterministic stubs.
- Prompts include authority-aware guardrails built via `build_analysis_guardrail_rules` so outputs respect Title 10 / Title 50 / LEO lanes.
- Guardrail violations are persisted on the `AgentRun` and rendered in the UI (badge + issues list).

For a click-by-click walkthrough of the UI pipeline, see `docs/TECHNICAL_FLOW.md`.
