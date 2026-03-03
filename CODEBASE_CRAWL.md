# Nexhelm Repository Crawl & Codebase Map

This document summarizes the repository after a full source crawl, with special focus on how the implementation compares to the root `README.md`.

## 1) What this repository is

Nexhelm is a two-part application:
- **Backend**: FastAPI service for:
  - WebSocket meeting sessions
  - AI opportunity detection from transcript snippets
  - Demo transcript playback
  - LangGraph-based multi-agent workflow APIs (SSE + REST)
- **Frontend**: React + TypeScript UI with 3 pages:
  - Opportunity Detection
  - Agentic Workflow
  - Backend Systems dashboard

## 2) Repository structure (actual files)

- `README.md`: Product overview, setup, architecture description.
- `backend/`
  - `app/main.py`: FastAPI app entrypoint, WebSocket APIs, meeting/demo routes, includes workflow router.
  - `app/workflow_api.py`: Workflow API router (`/api/workflow/*`) including SSE streaming.
  - `app/opportunity_detector.py`: Hybrid keyword + optional LLM opportunity detector.
  - `app/redis_client.py`: Redis persistence for meeting messages/opportunities.
  - `app/dummy_transcript.py`: Simulated transcript scenarios and timed playback.
  - `app/workflow/`
    - `graph.py`: LangGraph assembly.
    - `routing.py`: Next-node selection based on task/dependency state.
    - `state.py`: `WorkflowState` schema.
    - `main.py`: CLI-style workflow runner.
    - `storage.py`: In-memory CRM/account/doc stores + CSV logging.
    - `tools/agent_tools.py`: Agent tool facade around storage systems.
    - `agents/`: `base_agent.py`, `orchestrator_agent.py`, `operations_agent.py`, `advisor_agent.py`.
    - `tests/test_workflow.py`: unit/integration-style workflow tests.
- `frontend/`
  - `src/App.tsx`: routing shell.
  - `src/pages/OpportunityDetectionPage.tsx`: WebSocket conversation and opportunity UI.
  - `src/pages/WorkflowPage.tsx`: SSE workflow UI + task/event stream.
  - `src/pages/SystemsPage.tsx`: polling dashboard for backend system state.

## 3) Runtime architecture (implemented)

### Opportunity Detection runtime path
1. Frontend creates meeting: `POST /api/meeting/create`.
2. Frontend opens WebSocket: `/ws/{meeting_id}`.
3. Incoming messages are saved via `redis_client`.
4. Last N messages are assembled as context and analyzed by `OpportunityDetector.detect_opportunities(...)`.
5. Opportunities are persisted to Redis and broadcast over the same WebSocket.

### Workflow runtime path
1. Frontend starts SSE stream at `GET /api/workflow/stream?...`.
2. `workflow_api.py` initializes a `WorkflowState` and starts execution in the background.
3. `workflow.graph` routes among orchestrator/operations/advisor agents using `route_next_node`.
4. Console output is parsed into typed events (agent message, tool execution, routing, success/error).
5. Events are emitted to frontend over SSE; final state updates tasks/outcome/status.
6. Supporting systems are exposed through `/api/workflow/systems/*` and account CSV download endpoint.

## 4) Key implementation details

- **LLM usage pattern**:
  - Opportunity detection can run with pattern-only logic if no API key is present.
  - Workflow agents call OpenAI Chat Completions via raw `requests` in `BaseAgent.call_llm`.
- **Storage model**:
  - Meeting data and opportunities: Redis.
  - Workflow business systems (CRM/accounts/docs): in-memory objects in `workflow/storage.py`.
  - Audit export: CSV from account creation operations.
- **Real-time mechanisms**:
  - WebSocket for meeting transcript + opportunities.
  - SSE for workflow event stream.

## 5) README alignment check (important)

The root README is largely directionally correct, but there are several implementation mismatches:

1. **Workflow endpoint names differ**
   - README lists: `/api/workflow/start`, `/api/workflow/events`, `/api/workflow/download-log`.
   - Actual backend exposes: `/api/workflow/stream`, `/api/workflow/execute`, `/api/workflow/accounts-log`.

2. **Systems endpoint prefix differs**
   - README lists `/api/systems/*` endpoints.
   - Actual backend uses `/api/workflow/systems/*`.

3. **Architecture tree mentions missing node files**
   - README references `backend/app/workflow/nodes/orchestrator.py`, etc.
   - Current implementation wires agent class methods directly in `graph.py`; those node files do not exist.

4. **Port references are inconsistent**
   - Main setup and frontend use backend at `:8002`.
   - `backend/app/main.py` root/test text and embedded HTML test page still reference `:8001` in some places.

5. **Testing command likely stale**
   - README suggests `python -m pytest test_*.py` from `backend/`.
   - Existing tests are located under `backend/app/workflow/tests/test_workflow.py`.

## 6) Overall health snapshot

- **Strengths**
  - Clear separation between transcript-opportunity flow and workflow automation flow.
  - Real-time UX support is robust (WebSocket + SSE).
  - Good demoability (scenario transcripts, systems dashboard, CSV logs).

- **Risks / cleanup opportunities**
  - Documentation drift (README vs implemented endpoints/files).
  - Some fallback import patterns and duplicated port assumptions suggest quick-iteration code paths.
  - Workflow tests appear to assume local LLM availability and mutable shared stores; may be flaky without controlled fixtures/mocks.

## 7) Suggested next actions

1. Update root README endpoint sections and architecture tree to match current code.
2. Standardize backend port references (`8002` vs `8001`) in `backend/app/main.py` text/test client.
3. Add a short `backend/README.md` and `frontend/README.md` with current run/test commands.
4. Add deterministic test mode for workflow agents (mock LLM responses) to make CI reliable.
