"""
Orchestrator node for the workflow system.
Plans initial tasks and sets up the workflow state.
"""

import uuid
from datetime import datetime
from ..state import WorkflowState
from ..storage import get_crm


def orchestrator_node(state: WorkflowState) -> WorkflowState:
    """
    Orchestrator node that plans initial tasks for the workflow.
    Takes WorkflowState as input and returns updated WorkflowState with hardcoded tasks.
    """
    
    # Generate workflow_id using uuid4
    workflow_id = str(uuid.uuid4())
    
    # Set status to "in_progress"
    status = "in_progress"
    
    # Set timestamps
    now = datetime.now().isoformat()
    created_at = now
    updated_at = now
    
    # Load client context from CRM
    client_id = state["request"]["client_id"]
    crm = get_crm()
    client = crm.get_client(client_id)
    
    if client:
        context = {
            "client_age": client["age"],
            "existing_accounts": client["existing_accounts"],
            "available_documents": ["drivers_license", "tax_return_2023", "ira_application"]
        }
        # Update client_name in request
        state["request"]["client_name"] = client["name"]
    else:
        context = {
            "client_age": 0,
            "existing_accounts": [],
            "available_documents": []
        }
    
    # Create hardcoded task list for "Open Roth IRA"
    tasks = [
        {
            "id": "task_1",
            "description": "Verify Roth IRA income eligibility",
            "owner": "operations_agent",
            "status": "pending",
            "dependencies": [],
            "result": None
        },
        {
            "id": "task_2",
            "description": "Send IRA application form to client",
            "owner": "advisor_agent",
            "status": "pending",
            "dependencies": ["task_1"],
            "result": None
        },
        {
            "id": "task_3",
            "description": "Review and validate submitted IRA application",
            "owner": "operations_agent",
            "status": "pending",
            "dependencies": ["task_2"],
            "result": None
        },
        {
            "id": "task_4",
            "description": "Open Roth IRA account in system",
            "owner": "operations_agent",
            "status": "pending",
            "dependencies": ["task_3"],
            "result": None
        },
        {
            "id": "task_5",
            "description": "Notify client of account opening",
            "owner": "advisor_agent",
            "status": "pending",
            "dependencies": ["task_4"],
            "result": None
        }
    ]
    
    # Set next_actions to start with operations_agent
    next_actions = [{"agent": "operations_agent", "action": "verify_eligibility", "priority": "high"}]
    
    # Update state with all the new information
    state.update({
        "workflow_id": workflow_id,
        "status": status,
        "created_at": created_at,
        "updated_at": updated_at,
        "context": context,
        "tasks": tasks,
        "next_actions": next_actions
    })
    
    return state
