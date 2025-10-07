# Nexhelm Agentic Workflow - Data Flow Diagram

## 📊 Complete Data Flow Architecture

### 1. Input Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT DATA FLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   CLIENT    │    │   REQUEST   │    │   CONTEXT   │         │
│  │   REQUEST   │    │   PARSER    │    │   LOADER    │         │
│  │             │    │             │    │             │         │
│  │ • "Open IRA │───►│ • Extract   │───►│ • Load      │         │
│  │   for John" │    │   intent    │    │   client    │         │
│  │ • Client ID │    │ • Parse     │    │   data      │         │
│  │ • Context   │    │   params    │    │ • Get       │         │
│  └─────────────┘    └─────────────┘    │   history   │         │
│                                         └─────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Workflow State Data Structure

```json
{
  "request": {
    "type": "open_roth_ira",
    "client_id": "john_smith_123",
    "client_name": "John Smith",
    "initiator": "sarah_advisor"
  },
  "workflow_id": "uuid-generated-id",
  "status": "in_progress",
  "created_at": "2025-10-06T22:07:26.318279",
  "updated_at": "2025-10-06T22:07:26.318279",
  "context": {
    "client_age": 45,
    "existing_accounts": ["checking", "brokerage"],
    "available_documents": ["drivers_license", "tax_return_2023"],
    "client_income": 145000
  },
  "tasks": [
    {
      "id": "task_1",
      "description": "Verify client's eligibility for Roth IRA",
      "owner": "operations_agent",
      "status": "completed",
      "dependencies": [],
      "result": "Account ROTH IRA-1000 created successfully",
      "priority": "high",
      "estimated_duration": "1 hour"
    }
  ],
  "messages": [
    {
      "from_agent": "orchestrator_agent",
      "to_agent": "workflow_system",
      "timestamp": "2025-10-06T22:07:26.318279",
      "content": "Created comprehensive workflow plan",
      "type": "workflow_planning"
    }
  ],
  "decisions": [
    {
      "agent": "orchestrator_agent",
      "timestamp": "2025-10-06T22:07:26.318282",
      "decision": "Created comprehensive workflow plan",
      "reasoning": "The client has requested to open a Roth IRA..."
    }
  ],
  "blockers": [],
  "next_actions": [
    {
      "agent": "operations_agent",
      "action": "Verify client's eligibility for Roth IRA",
      "priority": "high"
    }
  ],
  "outcome": {
    "account_number": "ROTH IRA-1000",
    "account_type": "roth_ira",
    "status": "active",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### 3. Agent Communication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT COMMUNICATION FLOW                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ORCHESTRATOR │    │   ADVISOR   │    │ OPERATIONS  │         │
│  │   AGENT     │    │   AGENT     │    │   AGENT     │         │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘         │
│         │                  │                  │                │
│         │ 1. Workflow Plan │                  │                │
│         ├─────────────────►│                  │                │
│         │                  │                  │                │
│         │ 2. Task Assignment│                 │                │
│         ├─────────────────►│                  │                │
│         │                  │                  │                │
│         │                  │ 3. Client Comm   │                │
│         │                  ├─────────────────►│                │
│         │                  │                  │                │
│         │                  │ 4. Status Update │                │
│         │                  │◄─────────────────┤                │
│         │                  │                  │                │
│         │ 5. Final Result  │                  │                │
│         │◄─────────────────┤                  │                │
│         │                  │                  │                │
└─────────┴──────────────────┴──────────────────┴────────────────┘
```

### 4. LLM Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        LLM DATA FLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   AGENT     │    │   PROMPT    │    │   LLM API   │         │
│  │   CONTEXT   │    │   BUILDER   │    │             │         │
│  │             │    │             │    │             │         │
│  │ • Workflow  │───►│ • System    │───►│ • GPT-3.5   │         │
│  │   State     │    │   Prompt    │    │ • Caching   │         │
│  │ • Client    │    │ • Context   │    │ • Response  │         │
│  │   Info      │    │ • Task      │    │ • Error     │         │
│  │ • History   │    │   Details   │    │   Handling  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                         │                      │
│                                         ▼                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   RESPONSE  │    │   PARSER    │    │   CACHE     │         │
│  │   HANDLER   │◄───│             │◄───│             │         │
│  │             │    │ • JSON      │    │ • Store     │         │
│  │ • Validate  │    │   Parse     │    │   Response  │         │
│  │ • Extract   │    │ • Extract   │    │ • Check     │         │
│  │ • Execute   │    │   Actions   │    │   Cache     │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5. Tool Execution Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      TOOL EXECUTION FLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   AGENT     │    │   TOOL      │    │   STORAGE   │         │
│  │   REQUEST   │    │   ROUTER    │    │   SYSTEM    │         │
│  │             │    │             │    │             │         │
│  │ • Tool Name │───►│ • Route to  │───►│ • CRM       │         │
│  │ • Params    │    │   Handler   │    │ • Documents │         │
│  │ • Context   │    │ • Validate  │    │ • Accounts  │         │
│  └─────────────┘    │   Params    │    │ • Notify    │         │
│                     └─────────────┘    └─────────────┘         │
│                             │                  │               │
│                             ▼                  ▼               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   RESULT    │    │   ERROR     │    │   SUCCESS   │         │
│  │   HANDLER   │◄───│   HANDLER   │    │   HANDLER   │         │
│  │             │    │             │    │             │         │
│  │ • Process   │    │ • Log Error │    │ • Update    │         │
│  │   Result    │    │ • Return    │    │   State     │         │
│  │ • Update    │    │   Error     │    │ • Continue  │         │
│  │   State     │    │ • Fallback  │    │   Workflow  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6. State Management Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     STATE MANAGEMENT FLOW                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   WORKFLOW  │    │   STATE     │    │   PERSIST   │         │
│  │   EXECUTION │    │   UPDATER   │    │   LAYER     │         │
│  │             │    │             │    │             │         │
│  │ • Agent     │───►│ • Update    │───►│ • Redis     │         │
│  │   Actions   │    │   Tasks     │    │ • Database  │         │
│  │ • Tool      │    │ • Update    │    │ • File      │         │
│  │   Results   │    │   Messages  │    │   System    │         │
│  │ • LLM       │    │ • Update    │    │             │         │
│  │   Responses │    │   Status    │    │             │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                             │                  │               │
│                             ▼                  ▼               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   ROUTING   │    │   AUDIT     │    │   RECOVERY  │         │
│  │   SYSTEM    │◄───│   LOGGER    │    │   SYSTEM    │         │
│  │             │    │             │    │             │         │
│  │ • Check     │    │ • Log All   │    │ • Restore   │         │
│  │   Dependencies│   │   Changes   │    │   State     │         │
│  │ • Determine │    │ • Track     │    │ • Resume    │         │
│  │   Next      │    │   History   │    │   Workflow  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7. Error Handling Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      ERROR HANDLING FLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   ERROR     │    │   ERROR     │    │   FALLBACK  │         │
│  │   DETECTION │    │   CLASSIFIER│    │   SYSTEM    │         │
│  │             │    │             │    │             │         │
│  │ • LLM       │───►│ • API       │───►│ • Hardcoded │         │
│  │   Timeout   │    │   Error     │    │   Logic     │         │
│  │ • Tool      │    │ • Network   │    │ • Continue  │         │
│  │   Failure   │    │   Error     │    │   Workflow  │         │
│  │ • Network   │    │ • System    │    │ • Log       │         │
│  │   Issue     │    │   Error     │    │   Error     │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                             │                  │               │
│                             ▼                  ▼               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   RETRY     │    │   ESCALATE  │    │   COMPLETE  │         │
│  │   MECHANISM │    │   TO HUMAN  │    │   WORKFLOW  │         │
│  │             │    │             │    │             │         │
│  │ • Retry     │    │ • Notify    │    │ • Return    │         │
│  │   Logic     │    │   Admin     │    │   Result    │         │
│  │ • Backoff   │    │ • Create    │    │ • Update    │         │
│  │   Strategy  │    │   Ticket    │    │   Status    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 8. Performance Monitoring Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   PERFORMANCE MONITORING FLOW                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   METRICS   │    │   ANALYTICS │    │   DASHBOARD │         │
│  │   COLLECTOR │    │   ENGINE    │    │             │         │
│  │             │    │             │    │             │         │
│  │ • Execution │───►│ • Process   │───►│ • Real-time │         │
│  │   Time      │    │   Metrics   │    │   View      │         │
│  │ • LLM       │    │ • Generate  │    │ • Historical│         │
│  │   Costs     │    │   Reports   │    │   Data      │         │
│  │ • Success   │    │ • Identify  │    │ • Alerts    │         │
│  │   Rate      │    │   Trends    │    │ • KPIs      │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                             │                  │               │
│                             ▼                  ▼               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   ALERTING  │    │   OPTIMIZE  │    │   REPORTING │         │
│  │   SYSTEM    │    │   SYSTEM    │    │   SYSTEM    │         │
│  │             │    │             │    │             │         │
│  │ • Threshold │    │ • Auto-tune │    │ • Generate  │         │
│  │   Alerts    │    │   Params    │    │   Reports   │         │
│  │ • Notify    │    │ • Improve   │    │ • Export    │         │
│  │   Admins    │    │   Performance│   │   Data      │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Data Types and Structures

### Core Data Types

1. **WorkflowState**: Main state container
2. **Task**: Individual workflow task
3. **Message**: Agent communication
4. **Decision**: Agent decision record
5. **Blocker**: Workflow blocker
6. **Outcome**: Final workflow result

### Data Validation

```python
# Example data validation
def validate_workflow_state(state: WorkflowState) -> bool:
    required_fields = ['request', 'workflow_id', 'status', 'tasks']
    return all(field in state for field in required_fields)

def validate_task(task: dict) -> bool:
    required_fields = ['id', 'description', 'owner', 'status']
    return all(field in task for field in required_fields)
```

### Data Persistence

```python
# Example persistence layer
class WorkflowPersistence:
    def save_state(self, state: WorkflowState) -> bool:
        # Save to Redis/Database
        pass
    
    def load_state(self, workflow_id: str) -> WorkflowState:
        # Load from Redis/Database
        pass
    
    def update_state(self, workflow_id: str, updates: dict) -> bool:
        # Update specific fields
        pass
```

## 🔄 Data Flow Summary

1. **Input**: Client request → Request parser → Context loader
2. **Planning**: Orchestrator agent → LLM call → Workflow plan
3. **Execution**: Routing system → Agent selection → Tool execution
4. **State Management**: State updater → Persistence layer → Audit logger
5. **Completion**: Final result → Outcome generation → Workflow termination

This comprehensive data flow ensures that all information is properly tracked, validated, and persisted throughout the workflow execution.
