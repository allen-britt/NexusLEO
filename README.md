# NexusCore

NexusCore is a mission-centric intelligence workspace that connects:

- **APEX** – the analyst UI + FastAPI backend (missions, documents, agent runs, reports)
- **AggreGator** – the data fabric + knowledge graph (DuckDB/parquet)
- **Local LLMs via Ollama** – structured extraction, gap analysis, and templated reporting

The result is a single browser-based workspace where analysts can paste HUMINT, upload sources, run an agentic analysis cycle, and generate commander-ready reports against a live knowledge graph.

---

## Key Capabilities

- **Mission workspace with guardrails**
  - Missions tagged by **authority** (Title 10, Title 50, LEO, etc.) and **INT mix** (HUMINT, OSINT, SIGINT, GEOINT…)
  - Guardrail badges and tooltips make lane boundaries explicit.

- **Agentic analysis runs**
  - LLM-backed pipeline extracts **facts, entities, events**, and **gaps** from mission documents and KG snapshots.
  - Each run persists a full `AgentRun` record, including `raw_facts`, `gaps`, and `delta_summary` for downstream products.

- **Knowledge-graph context**
  - AggreGator maintains a per-mission namespace in DuckDB/parquet.
  - APEX pulls KG snapshots and metrics into the Analysis tab for coverage and health.

- **Templated mission reports**
  - One-click generation of tailored products (e.g., HUMINT summary, LEO case pack, commander decision sheet).
  - Reports are guardrail- and KG-aware and rendered as prose-styled HTML for export.

- **Decision intelligence sidebar**
  - Mission decisions, COAs, blind spots, and policy checks appear with severity dots and risk/policy badges.

- **Debug/testing utilities**
  - Set `NEXT_PUBLIC_SHOW_REPORT_DEBUG=true` to show the TemplateReport debug panel (raw payloads + responses).

---

## Architecture at a Glance

```text
 Browser        HTTP          Next.js UI          HTTP           FastAPI API
───────────◀────────────▶ APEX Frontend ◀──────────────▶  APEX Backend
 (localhost:3000)        (core/APEX/frontend)          (core/APEX/backend)
                               │
                               │ HTTP
                               ▼
                       AggreGator (KG + data)
                       DuckDB / parquet storage
                               │
                               │ HTTP
                               ▼
                          Ollama LLMs
```

- **APEX Frontend** – Next.js 14, React, TypeScript, Tailwind.
- **APEX Backend** – FastAPI, SQLAlchemy, Pydantic v2; persists missions, docs, datasets, agent runs.
- **AggreGator** – FastAPI + DuckDB; manages data profiling and the mission knowledge graph.
- **LLM Runtime** – Ollama (e.g., mistral, phi3) with JSON-structured outputs and repair/fallback logic.
- **Storage** – SQLite `app.db` for APEX + DuckDB `aggregator.duckdb` for the KG (Postgres recommended for production).

For a deeper technical breakdown, see `docs/ARCHITECTURE.md`.

---

## Getting Started (Docker)

```bash
# Clone the repo
git clone <your-repo-url> nexuscore
cd nexuscore

# Ensure Docker & docker compose are running

# Start the stack
docker compose up --build -d
```

This launches:

| Service | Port |
| --- | --- |
| Ollama | 11434 |
| AggreGator | 8100 |
| APEX backend | 8000 |
| APEX frontend | 3000 |

Open http://localhost:3000 and:

1. Create a mission (authority + INT set).
2. Paste HUMINT into the Data tab; upload files/URLs in Sources.
3. Click **Run Analysis** in Overview to execute the agent cycle.
4. Use the Reports tab for templated products.

Health checks block the UI until backend, AggreGator, and LLM dependencies are ready.

For detailed stack wiring and mission lifecycle examples, see `docs/STACK_SETUP.md`.

---

## Local Development

You can run the frontend/backends outside Docker for rapid iteration.

### Backend

```bash
cd core/APEX/backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# set env vars for AGGREGATOR_BASE_URL, LLM_MISTRAL_URL, LLM_PHI3_URL, etc.
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd core/APEX/frontend
pnpm install   # or npm install

# ensure NEXT_PUBLIC_APEX_API_BASE_URL points at backend (e.g. http://localhost:8000)
pnpm dev       # or npm run dev
```

---

## Documentation Map

- `docs/EXEC_OVERVIEW.md` – Executive / operator view of the mission workspace.
- `docs/ARCHITECTURE.md` – Detailed stack diagram, services, ports, env vars.
- `docs/STACK_SETUP.md` – Stack wiring + mission lifecycle walkthrough.
- `docs/TECHNICAL_FLOW.md` – UI → backend technical walkthrough.
- `docs/DEMO_PLAYBOOK.md` – Demo scripts for different mission types.
- `docs/ROADMAP.md` – Current roadmap (priority-based).
- `docs/TODO.md` – Engineering checklist / work queue.

---

## License

[Your License Here]
