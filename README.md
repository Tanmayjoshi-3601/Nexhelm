# Nexhelm — AI Workflow Copilot for Revenue Teams

Nexhelm is a production-oriented AI application that combines **real-time opportunity detection** with **multi-agent workflow automation**.

It is designed to show how AI can turn customer conversations into measurable business outcomes:
- detect high-value intent in live calls,
- trigger compliant operational workflows,
- update business systems automatically,
- and give teams an auditable execution trail.

This repository is intentionally practical: it demonstrates the exact skills companies like Kana care about—AI-assisted development, system integration thinking, and judgment about production readiness.

---

## Why this project matters (business-first)

### Core business problem
Most revenue teams lose value in the handoff between:
1. what customers say,
2. what actions should happen,
3. what systems actually get updated.

That creates missed opportunities, slow follow-up, and inconsistent customer experience.

### Nexhelm value proposition
Nexhelm closes that gap by:
- capturing intent from live conversations,
- routing tasks to specialized AI agents,
- executing operational steps against backend systems,
- logging every action for audit/compliance.

### Expected business impact
| Outcome | How Nexhelm drives it | Typical impact direction |
|---|---|---|
| Faster response time | Real-time detection + automated workflow kickoff | ↓ Time-to-action |
| Higher conversion / upsell | Opportunity prompts and structured follow-up | ↑ Revenue per client |
| Lower operational cost | Automated eligibility checks, document flow, account ops | ↓ Manual effort |
| Better compliance posture | Audit logs + deterministic task trail | ↓ Risk exposure |
| Better manager visibility | Live systems dashboard + workflow telemetry | ↑ Operational control |

---

## Use cases this is built for

### 1) Conversation-to-revenue acceleration
**Example:** Advisor hears retirement/education/life-event signals in a meeting.

Nexhelm:
- detects relevant opportunities,
- prioritizes them,
- and surfaces them immediately for action.

**Business value:** Increases the percentage of actionable conversations converted into pipeline/revenue.

### 2) Back-office automation for customer requests
**Example:** Client asks to open a Roth IRA.

Nexhelm:
- creates a task plan,
- validates eligibility and documents,
- opens account records,
- sends customer updates.

**Business value:** Reduces cycle time and delivery cost while improving consistency.

### 3) Enterprise readiness & auditability
**Example:** Team needs traceability for regulated workflows.

Nexhelm:
- records agent decisions,
- preserves task-level status,
- exports CSV logs for operations/compliance review.

**Business value:** Lowers compliance friction and improves trust in automation.

---

## Integration strategy (what makes this production-relevant)

Nexhelm currently uses simulated systems for demo speed, but the architecture is integration-ready.

### High-value integration opportunities

| Integration surface | Target systems | Why it matters |
|---|---|---|
| CRM | Salesforce, HubSpot, Dynamics | Sync opportunities, client records, and follow-up tasks |
| Marketing automation | Marketo, Braze, Customer.io, Iterable | Trigger nurture/journey flows from detected intent |
| Communication | Twilio, SendGrid, Outlook/Gmail APIs | Send compliant notifications and advisor/client updates |
| Data warehouse/BI | Snowflake, BigQuery, Databricks | Centralize events for analytics and performance tracking |
| Identity & auth | Okta, Auth0, Azure AD | Enterprise SSO and role-based access |
| Compliance archiving | S3/Blob + governance tooling | Retention, audit evidence, and policy enforcement |

### Integration blueprint
1. Replace simulated tool methods with provider adapters.
2. Add idempotency keys and retries for external writes.
3. Add webhook/event bus support for downstream subscribers.
4. Add tenant isolation + RBAC + audit retention policy.

---

## ROI model (simple, practical framing)

Use this framework when discussing value with stakeholders.

**Annualized benefit estimate**

`Benefit = (Time saved per workflow × workflows/month × labor cost) + (Incremental conversions × average value) - (Platform + AI run cost)`

### Example lens (illustrative)
- 1,000 workflows/month
- 12 minutes saved/workflow
- $60/hour blended ops cost
- 2% conversion lift on opportunities

Even before conversion lift, time savings alone can justify deployment in high-volume teams.

---

## Product walkthrough

Nexhelm has three user-facing areas:

1. **Opportunity Detection** (default route `/`)
   - Live conversation stream
   - Opportunity scoring and prioritization
   - Demo mode with realistic scenarios

2. **Agentic Workflow** (route `/workflow`)
   - Start workflow scenarios (e.g., Roth IRA opening)
   - Watch agent events in real time via SSE
   - Track task completion and workflow progress

3. **Backend Systems Dashboard** (route `/systems`)
   - Inspect simulated CRM, accounts, and document store
   - Auto-refresh system state
   - Export data/logs for review

---

## Architecture

### Backend (FastAPI + Python + LangGraph)
```
backend/
├── app/
│   ├── main.py                      # FastAPI server with WebSocket endpoints
│   ├── opportunity_detector.py      # Opportunity detection engine
│   ├── dummy_transcript.py          # Demo conversation scenarios
│   ├── redis_client.py              # Redis state management
│   ├── workflow_api.py              # Workflow SSE/REST APIs
│   └── workflow/
│       ├── graph.py                 # LangGraph workflow graph
│       ├── state.py                 # Workflow state schema
│       ├── routing.py               # Next-node routing logic
│       ├── storage.py               # Simulated CRM/accounts/doc systems
│       ├── agents/                  # Orchestrator, Operations, Advisor agents
│       ├── tools/agent_tools.py     # Tools exposed to agents
│       └── tests/test_workflow.py   # Workflow tests
└── requirements.txt
```

### Frontend (React + TypeScript + Tailwind)
```
frontend/
├── src/
│   ├── App.tsx
│   ├── pages/
│   │   ├── OpportunityDetectionPage.tsx
│   │   ├── WorkflowPage.tsx
│   │   └── SystemsPage.tsx
│   └── index.tsx
└── package.json
```

### Runtime communication
- **WebSocket**: real-time meeting messages + detected opportunities
- **SSE**: streaming workflow events during agent execution
- **REST**: setup, scenario lookup, systems data, downloads

---

## API endpoints (current implementation)

### Meeting & transcript
- `POST /api/meeting/create`
- `GET /api/meeting/{meeting_id}/history`
- `WebSocket /ws/{meeting_id}`

### Demo transcripts
- `GET /api/demo/scenarios`
- `POST /api/demo/start/{meeting_id}?scenario=<scenario_id>`
- `POST /api/demo/stop/{meeting_id}`
- `GET /api/demo/status/{meeting_id}`

### Agentic workflow
- `GET /api/workflow/stream` (SSE)
- `POST /api/workflow/execute`
- `GET /api/workflow/scenarios`
- `GET /api/workflow/accounts-log`
- `GET /api/workflow/accounts`

### Backend systems
- `GET /api/workflow/systems/crm`
- `GET /api/workflow/systems/documents`
- `GET /api/workflow/systems/all`

---

## Quick start

### Prerequisites
- Python 3.11+
- Node.js 16+
- Redis
- OpenAI API key

### 1) Install dependencies
```bash
# backend
cd backend
pip install -r requirements.txt

# frontend
cd ../frontend
npm install
```

### 2) Configure environment
Create `backend/.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### 3) Run services
```bash
# terminal 1
redis-server

# terminal 2
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# terminal 3
cd frontend
npm start
```

### 4) Open the app
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8002`
- API docs: `http://localhost:8002/docs`
- Test page: `http://localhost:8002/test`

---

## Enterprise hardening roadmap

To move from demo to production:

1. **Integration hardening**
   - Provider adapters, retries, circuit breakers
2. **Security**
   - SSO/RBAC, secrets vaulting, tenant-level controls
3. **Reliability**
   - Queueing for long-running tasks, dead-letter handling
4. **Observability**
   - Structured logs, traces, workflow-level SLIs/SLOs
5. **Governance**
   - Prompt/version controls, model fallback policy, human-in-the-loop gates

---

## Testing

```bash
# Backend workflow tests
python -m pytest backend/app/workflow/tests/test_workflow.py

# Frontend tests
cd frontend && npm test
```

---

## Why this repo is useful for AI-builder evaluation

This codebase shows:
- full-stack execution with AI-assisted development,
- real-time event handling patterns (WebSocket + SSE),
- practical multi-agent orchestration,
- integration-oriented architecture,
- and explicit attention to business outcomes rather than only model demos.

