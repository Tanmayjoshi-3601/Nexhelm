"""
Advisor Agent node for client-facing tasks.
Handles client communication, form sending, and notifications.
"""

from datetime import datetime
from ..state import WorkflowState


def advisor_agent_node(state: WorkflowState) -> WorkflowState:
    """
    Advisor Agent node that handles client-facing tasks.
    Finds pending tasks assigned to advisor and completes them.
    """
    
    # Find first task where owner == "advisor_agent" and status == "pending" and dependencies are met
    current_task = None
    for task in state["tasks"]:
        if (task["owner"] == "advisor_agent" and 
            task["status"] == "pending" and
            _check_task_dependencies(task, state["tasks"])):
            current_task = task
            break
    
    # If no task found, set next_actions to empty and return state
    if not current_task:
        state["next_actions"] = []
        return state
    
    # Get client name for printing
    client_name = state["request"]["client_name"]
    
    # Process task based on description
    if "Send IRA application form to client" in current_task["description"]:
        # Task: "Send IRA application form to client"
        print(f"Advisor Agent: Sending IRA application form to {client_name}")
        
        # Update task status to "completed"
        current_task["status"] = "completed"
        current_task["result"] = "Form sent via email"
        
        # Add message to state
        message = {
            "from_agent": "advisor_agent",
            "to_agent": "operations_agent",
            "timestamp": datetime.now().isoformat(),
            "content": "IRA application form sent to client. Awaiting submission.",
            "type": "update"
        }
        state["messages"].append(message)
        
        # Add decision to state
        decision = {
            "agent": "advisor_agent",
            "timestamp": datetime.now().isoformat(),
            "decision": "Sent personalized IRA application to client",
            "reasoning": "Client is existing customer, pre-filled form with known details"
        }
        state["decisions"].append(decision)
        
        # Set next_actions to operations_agent for next task
        state["next_actions"] = [{"agent": "operations_agent", "action": "wait_for_form", "priority": "medium"}]
        
    elif "Notify client of account opening" in current_task["description"]:
        # Task: "Notify client of account opening"
        print(f"Advisor Agent: Notifying {client_name} of successful account opening")
        
        # Update task status to "completed"
        current_task["status"] = "completed"
        current_task["result"] = "Client notified"
        
        # Add message
        message = {
            "from_agent": "advisor_agent",
            "to_agent": "operations_agent",
            "timestamp": datetime.now().isoformat(),
            "content": f"Client {client_name} has been notified of successful account opening.",
            "type": "update"
        }
        state["messages"].append(message)
        
        # Add decision
        decision = {
            "agent": "advisor_agent",
            "timestamp": datetime.now().isoformat(),
            "decision": "Sent account opening notification to client",
            "reasoning": "Account successfully opened, client should be informed immediately"
        }
        state["decisions"].append(decision)
        
        # Set status to "completed" (this is the last task)
        state["status"] = "completed"
        state["next_actions"] = []
    
    # Update state["updated_at"]
    state["updated_at"] = datetime.now().isoformat()
    
    return state


def _check_task_dependencies(task: dict, all_tasks: list) -> bool:
    """
    Helper function to check if a task's dependencies are met.
    Returns True if all dependencies are completed.
    """
    if not task.get("dependencies"):
        return True
    
    # Create a map of task IDs to their status
    task_status_map = {t["id"]: t["status"] for t in all_tasks}
    
    # Check if all dependencies are completed
    for dep_id in task["dependencies"]:
        if task_status_map.get(dep_id) != "completed":
            return False
    
    return True
