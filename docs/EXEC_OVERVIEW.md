# NexusCore Mission Workspace (Executive / Operator View)

This guide explains, in plain language, what happens when someone uses the mission workspace. Use it to brief leaders or new operators on how the platform behaves end-to-end.

---

## 1. The Workspace at a Glance

```
Mission Home
 ├─ Overview    → quick mission status + "Run Analysis" button
 ├─ Data        → text documents analysts type or paste in
 ├─ Sources     → uploaded files / links that feed the KG
 ├─ Analysis    → live insights, gap alerts, entities, events
 └─ Reports     → one-click intel products
```

- Every page load pulls the latest mission record, documents, agent runs, datasets, and gap analysis in one round-trip so tabs populate instantly.
- Analysts never leave the mission view to trigger analysis, upload docs, or generate reports.

---

## 2. What Each Tab Really Does

| Tab | What the user sees | What the platform does quietly |
| --- | --- | --- |
| **Overview** | Mission summary, guardrail badge, last run, Run Analysis button. | Shows current guardrail posture and wires the button that kicks off the full agent pipeline. |
| **Data** | Form to paste HUMINT IIRs and a library of mission docs. | Saves documents straight into the mission DB so the next analysis cycle reads them automatically. |
| **Sources** | File/URL uploader with INT tagging and ingest status. | Stores the file, queues a background job, pushes text into AggreGator so KG metrics stay fresh. |
| **Analysis** | Mission banner (namespace, INT tags), gap cards, entity/event explorer, AI/HUMINT panels. | Streams KG stats, latest agent run outputs, and gap telemetry so operators can judge coverage at a glance. |
| **Reports** | Template catalog (LEO summary, delta update, etc.) with guardrail warnings. | Sends the latest run data into the report generator and stores finished reports for download. |

---

## 3. Key Button Journeys

### 3.1 "Add Mission"
1. User fills in mission name, authority lane, and INT set.
2. Backend validates the authority rules, creates the mission, and registers a dedicated KG namespace (e.g., `mission-42`).
3. Mission appears immediately in the UI with an empty analysis history.

### 3.2 "Add Document" (Data tab)
1. Analyst pastes an IIR or debrief.
2. Backend saves it into the mission’s document table (default "include in analysis").
3. Future agent runs automatically ingest it—no extra action required.

### 3.3 "Upload Source" (Sources tab)
1. Analyst drags a PDF or pastes a URL.
2. Platform stores the file, tags it with INT metadata, and schedules an ingest job.
3. Background worker pipes the plain text to AggreGator, boosting KG nodes/edges (reflected later in Analysis tab metrics).

### 3.4 "Run Analysis" (Overview tab)
```
Button click
   ├─► Backend loads mission + docs
   ├─► LLM extracts raw facts, entities, events
   ├─► Structured payload goes into AggreGator
   ├─► LLM produces gaps, summary, next steps, delta
   └─► Results saved as a new AgentRun (facts + gaps + delta)
```
- The UI auto-refreshes the latest run so guardrail badges, gap counts, and report templates use the fresh data.

### 3.5 "Generate Report" (Reports tab)
1. User selects a template (e.g., Full INTREP).
2. Service composes context + latest AgentRun, asks the LLM for the report body, renders Markdown → HTML.
3. Finished product is stored and listed under Mission Reports for future review.

---

## 4. Data Journey Cheat Sheet

```
User input (mission, docs, uploads, buttons)
      ↓
APEX API (FastAPI) saves records + triggers jobs
      ↓
Agent Service + LLMs run analysis, enforce guardrails
      ↓
AggreGator KG mirrors the mission namespace + metrics
      ↓
AgentRun + KG data feed the UI tabs and report generator
```

- If anything fails (e.g., LLM JSON), enhanced logging plus a fallback stub keep the UI responsive while surfacing the error.
- Because every mission has its own namespace, operators can safely run multiple scenarios in parallel without cross-contamination.

Use this sheet when briefing leadership on what the platform is doing for them every time they click through a mission. 
