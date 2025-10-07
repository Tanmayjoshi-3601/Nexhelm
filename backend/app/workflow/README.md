# Nexhelm Multi-Agent Workflow System

## Overview

This module implements a multi-agent workflow system using LangGraph for automating financial advisor tasks. Two specialized agents (Advisor Agent and Operations Agent) collaborate to complete workflows like opening IRA accounts.

## Architecture

- **Orchestrator**: Plans initial tasks
- **Supervisor**: Routes to appropriate agent
- **Advisor Agent**: Handles client communication
- **Operations Agent**: Handles backend operations
- **Shared State**: All nodes read/write to common state

## Workflow Flow

1. User submits request
2. Orchestrator creates task plan
3. Supervisor routes to agent
4. Agent executes task
5. Returns to supervisor
6. Repeats until complete

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run workflow:
```bash
python -m backend.app.workflow.main
```

3. Run tests:
```bash
python -m backend.app.workflow.tests.test_workflow
```

## Current Status

✅ Hardcoded workflow for "Open IRA"
✅ Two agents (Advisor, Operations)
✅ State management
✅ Blocker detection
⏳ LLM integration (next phase)
⏳ Dynamic task generation (next phase)

## Example Usage

```python
from backend.app.workflow.main import run_workflow

# Run a complete IRA opening workflow
result = run_workflow(
    client_id="john_smith_123",
    request_type="open_roth_ira"
)

print(f"Status: {result['status']}")
print(f"Account: {result['outcome']['account_number']}")
```

## Expected Output

When running the workflow, you should see:

```
============================================================
Starting workflow: open_roth_ira
Client: john_smith_123
============================================================

Operations Agent: Verifying eligibility - Income: $145000
Advisor Agent: Sending IRA application form to John Smith
Operations Agent: Validating IRA application form
Operations Agent: Opening account - IRA-1000
Advisor Agent: Notifying John Smith of successful account opening

============================================================
WORKFLOW COMPLETED
============================================================
Status: completed
Workflow ID: [uuid]

Tasks Completed: 5/5

Messages Exchanged: 5

Decisions Made: 5

Outcome: {'account_number': 'IRA-1000'}

============================================================
```
