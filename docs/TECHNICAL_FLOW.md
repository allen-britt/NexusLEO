# NexusCore UI → Backend Technical Walkthrough

This reference explains what happens after common UI interactions, tab by tab, and how the APEX backend, AggreGator KG, and LLM services cooperate behind the scenes.

---

## 1. Mission workspace boot sequence

```
Mission page load
   │
   ├─▶ Next.js server component fetches mission bundle via `fetch*` helpers
   │     (mission, documents, agent runs, datasets, gap analysis)
   │     └─ backend routes on /missions, /documents, /agent_runs, /gap-analysis
   │
   └─▶ <MissionTabs/> renders and provides tabbed navigation
```

- `app/missions/[id]/page.tsx` loads the mission, documents, runs, datasets, and gap analysis concurrently via `fetchMission*` helpers so every tab has data ready on first paint @core/APEX/frontend/app/missions/[id]/page.tsx#25-52.
- `<MissionTabs/>` hosts the five main tabs (Overview, Data, Sources, Analysis, Reports) and keeps local tab state @core/APEX/frontend/components/MissionTabs.tsx#41-195.

---

## 2. Tab-by-tab surface

| Tab | Frontend components | Backend dependencies | Notes |
| --- | --- | --- | --- |
| **Overview** | `<MissionDetail/>`, `<RunAnalysisButton/>`, `<AgentSummary/>`, `<GuardrailBadge/>` @core/APEX/frontend/components/MissionTabs.tsx#96-124 | `/missions/{id}` for mission + latest run, `/missions/{id}/agent_runs` for summaries | Provides mission metadata, guardrail posture, and the Run Analysis CTA. |
| **Data** | `<DocumentForm/>`, `<DocumentList/>`, `<MissionDatasetList/>`, `<MissionDatasetForm/>` @core/APEX/frontend/components/MissionTabs.tsx#125-166 | `/missions/{id}/documents`, `/missions/{id}/datasets` | Text documents injected here feed the agent pipeline; datasets track structured uploads. |
| **Sources** | `<MissionSourcesTab/>` handles file/URL uploads, INT tagging, delete actions via SWR @core/APEX/frontend/components/MissionSourcesTab.tsx#116-164 | `/missions/{id}/documents/upload`, `/missions/{id}/source_docs` | Uses background ingest jobs to push files into AggreGator. |
| **Analysis** | Custom layout showing KG namespace, metrics, `<GapsPriorities/>`, `<GapAnalysisPanel/>`, `<EntitiesEventsView/>`, `<AIAnalysisPanel/>`, `<HumintAnalysisPanel/>` @core/APEX/frontend/components/MissionTabs.tsx#198-334 | `/missions/{id}/analysis`, `/kg/*` proxy endpoints, recent agent runs | Displays telemetry (gap counts, datasets, run log) and embeds the AI/HUMINT panels. |
| **Reports** | `<TemplateReportPanel/>`, `<TemplateReportGenerator/>` @core/APEX/frontend/components/MissionTabs.tsx#175-191 | `/missions/{id}/reports`, `/template-report/*` | Launches templated report generation with guardrail context. |

---

## 3. Flow catalog of common user actions

### 3.1 Creating a mission ("Add Mission" button)
1. UI posts to `POST /missions` with authority + INT metadata.
2. FastAPI `create_mission` validates INT lanes, persists `Mission`, locks `original_authority`, and commits @core/APEX/backend/app/api/missions.py#38-85.
3. `ensure_mission_namespace` initializes the AggreGator project namespace so KG ingests have a target.
4. Response payload already includes `latest_agent_run` (if any) via `_mission_with_latest_run`.

### 3.2 Adding a mission document (Data tab → "Add document")
1. UI calls `POST /missions/{id}/documents` with title/content @core/APEX/backend/app/api/documents.py#62-78.
2. Backend creates a `Document` record tied to the mission; `include_in_analysis` defaults true @core/APEX/backend/app/models/__init__.py#85-93.
3. During the next agent cycle, `_build_mission_context` pulls every `include_in_analysis` document to construct the prompt corpus @core/APEX/backend/app/services/agent_service.py#186-211.

### 3.3 Uploading source files (Sources tab → file picker)
1. `<MissionSourcesTab/>` posts file + metadata to `POST /missions/{id}/documents/upload` @core/APEX/frontend/components/MissionSourcesTab.tsx#118-164.
2. `MissionDocumentService.ingest_file` writes the binary under `/data/mission_{id}/`, decodes text, and enqueues a `MissionIngestJob` @core/APEX/backend/app/services/mission_document_service.py#31-148.
3. Background job drains convert the text into an AggreGator document by calling `AggregatorClient.ingest_document(namespace, title, text, metadata)` @core/APEX/backend/app/services/aggregator_client.py#18-76.
4. AggreGator updates KG node/edge counts; those deltas flow back into mission gap analytics and the Analysis tab metrics.

### 3.4 Clicking **Run Analysis** (Overview tab)
```
<Button/> click
   │
   ├─▶ `RunAnalysisButton` calls `analyzeMission(missionId)`
   │     (frontend API helper)
   │
   └─▶ FastAPI `/missions/{id}/analyze` awaits `run_agent_cycle`
           │
           ├─ Load mission + docs, ensure KG namespace
           ├─ Extract raw facts, entities, events via LLM
           ├─ Ingest structured payloads into AggreGator
           ├─ Detect gaps, run cross-doc analysis, estimates,
           │   summary, next steps, self-verify, delta summary
           └─ Persist AgentRun with raw_facts/gaps/delta summary
```

- `<RunAnalysisButton/>` guards double-clicks, shows loading state, and updates context via `onCompleted` @core/APEX/frontend/components/RunAnalysisButton.tsx#7-44 and @core/APEX/frontend/components/RunAnalysisButtonWrapper.tsx#3-14.
- Backend entrypoint `POST /missions/{id}/analyze` simply validates the mission and dispatches `run_agent_cycle` @core/APEX/backend/app/api/agent.py#21-48.
- `run_agent_cycle` orchestrates every analytic step: builds prompts, calls `llm_client` helpers for facts/gaps/summary, ingests entities/events into AggreGator, applies guardrails, and stores results on `AgentRun` (including `raw_facts`, `gaps`, `delta_summary`) @core/APEX/backend/app/services/agent_service.py#1-400.
- AggreGator interactions (namespace init, KG summary, structured JSON ingest) use `AggregatorClient` @core/APEX/backend/app/services/aggregator_client.py#18-147.

### 3.5 Viewing gap telemetry (Analysis tab)
1. `<MissionTabs/>` computes gap counts from `gapAnalysis` prop (output of `/missions/{id}/gap-analysis`) and renders them in the hero metrics + `GapsPriorities` tiles @core/APEX/frontend/components/MissionTabs.tsx#198-305.
2. Backend gap analysis service (not clicked directly) reads KG snapshots and mission datasets to populate `missing_data`, `conflicts`, `quality_findings`, etc., which remain cached per mission until recomputed.

### 3.6 Generating template reports (Reports tab)
1. User picks a template in `<TemplateReportPanel/>` or `<TemplateReportGenerator/>` @core/APEX/frontend/components/MissionTabs.tsx#175-191.
2. Frontend calls `/template-report/generate` with mission ID + template ID. Backend `TemplateReportService` gathers mission context, latest runs, guardrails, and LLM outputs to render Markdown/HTML.
3. Completed reports are stored and later surfaced in the same panel for download.

---

## 4. End-to-end data journey summary

```
[Mission UI]
   │ create mission / upload docs / click Run Analysis
   ▼
[FastAPI routes]
   │ persist Mission + docs, trigger ingest jobs, call agent service
   ▼
[Agent Service]
   │ builds prompts → LLM → structured outputs
   │
   ├─▶ AggreGator (namespace, KG ingests, metrics)
   │
   └─▶ AgentRun persistence (facts, gaps, delta, guardrails)
        ▼
      Postgres/SQLite + KG snapshots
        ▼
[Frontend refresh]
   │ fetch latest mission bundle + gap analysis + runs
   ▼
[Analyst sees updated tabs, can export reports]
```

With this guide you can narrate, step-by-step, what backend work occurs every time a user clicks through the mission workspace. Adjust or extend the ASCII flows as new tabs or services ship.
