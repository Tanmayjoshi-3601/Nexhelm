"""
Operations Agent node for backend operations.
Handles eligibility verification, account opening, and compliance tasks.
"""

from datetime import datetime
from ..state import WorkflowState
from ..storage import get_crm, get_doc_store, get_account_system


def operations_agent_node(state: WorkflowState) -> WorkflowState:
    """
    Operations Agent node that handles backend operations.
    Finds pending tasks assigned to operations and completes them.
    """
    
    # Find first task where owner == "operations_agent" and status == "pending" and dependencies are met
    current_task = None
    for task in state["tasks"]:
        if (task["owner"] == "operations_agent" and 
            task["status"] == "pending" and
            _check_task_dependencies(task, state["tasks"])):
            current_task = task
            break
    
    # If no task found, set next_actions to empty and return state
    if not current_task:
        state["next_actions"] = []
        return state
    
    client_id = state["request"]["client_id"]
    
    # Process task based on description
    if "Verify Roth IRA income eligibility" in current_task["description"]:
        # Task: "Verify Roth IRA income eligibility"
        crm = get_crm()
        doc_store = get_doc_store()
        client = crm.get_client(client_id)
        doc = doc_store.get_document(client_id, "tax_return_2023")
        
        if client and doc:
            income = doc["income"]
            print(f"Operations Agent: Verifying eligibility - Income: ${income}")
            
            # Check if income < 161000 (Roth IRA income limit for 2024)
            if income < 161000:
                # Eligible
                current_task["status"] = "completed"
                current_task["result"] = f"Eligible - Income ${income} under $161k limit"
                
                # Add message to advisor_agent confirming eligibility
                message = {
                    "from_agent": "operations_agent",
                    "to_agent": "advisor_agent",
                    "timestamp": datetime.now().isoformat(),
                    "content": f"Client income verification complete. Income ${income} is eligible for Roth IRA.",
                    "type": "response"
                }
                state["messages"].append(message)
                
                # Add decision
                decision = {
                    "agent": "operations_agent",
                    "timestamp": datetime.now().isoformat(),
                    "decision": "Confirmed Roth IRA eligibility",
                    "reasoning": f"Income ${income} is below $161k limit for Roth IRA contributions"
                }
                state["decisions"].append(decision)
                
                # Set next_actions to advisor_agent for next task
                state["next_actions"] = [{"agent": "advisor_agent", "action": "send_form", "priority": "high"}]
            else:
                # Not eligible - add blocker
                blocker = {
                    "id": "blocker_1",
                    "description": f"Income ${income} exceeds Roth IRA limit of $161k",
                    "identified_by": "operations_agent",
                    "assigned_to": "advisor_agent",
                    "status": "active",
                    "created_at": datetime.now().isoformat()
                }
                state["blockers"].append(blocker)
                current_task["status"] = "failed"
                state["status"] = "failed"
                state["next_actions"] = []
    
    elif "Review and validate submitted IRA application" in current_task["description"]:
        # Task: "Review and validate submitted IRA application"
        doc_store = get_doc_store()
        doc = doc_store.get_document(client_id, "ira_application")
        print("Operations Agent: Validating IRA application form")
        
        if doc and doc.get("signature_page3"):
            # Valid application
            current_task["status"] = "completed"
            current_task["result"] = "Form validated successfully"
            
            # Add message
            message = {
                "from_agent": "operations_agent",
                "to_agent": "advisor_agent",
                "timestamp": datetime.now().isoformat(),
                "content": "IRA application form validated successfully. All required signatures present.",
                "type": "response"
            }
            state["messages"].append(message)
            
            # Add decision
            decision = {
                "agent": "operations_agent",
                "timestamp": datetime.now().isoformat(),
                "decision": "Approved IRA application form",
                "reasoning": "All required signatures and information present"
            }
            state["decisions"].append(decision)
            
            # Set next_actions to operations_agent (next task)
            state["next_actions"] = [{"agent": "operations_agent", "action": "open_account", "priority": "high"}]
        else:
            # Invalid application - missing signature
            blocker = {
                "id": "blocker_2",
                "description": "IRA application missing signature on page 3",
                "identified_by": "operations_agent",
                "assigned_to": "advisor_agent",
                "status": "active",
                "created_at": datetime.now().isoformat()
            }
            state["blockers"].append(blocker)
            
            # Add message to advisor_agent requesting signature
            message = {
                "from_agent": "operations_agent",
                "to_agent": "advisor_agent",
                "timestamp": datetime.now().isoformat(),
                "content": "IRA application form is missing signature on page 3. Please request client to complete and resubmit.",
                "type": "question"
            }
            state["messages"].append(message)
            
            # Mark task as failed and set status to failed
            current_task["status"] = "failed"
            state["status"] = "failed"
            state["next_actions"] = []
    
    elif "Open Roth IRA account in system" in current_task["description"]:
        # Task: "Open Roth IRA account in system"
        account_system = get_account_system()
        result = account_system.open_account(client_id, "roth_ira")
        account_number = result["account_number"]
        print(f"Operations Agent: Opening account - {account_number}")
        
        # Update task status to "completed"
        current_task["status"] = "completed"
        current_task["result"] = f"Account {account_number} opened successfully"
        
        # Add message
        message = {
            "from_agent": "operations_agent",
            "to_agent": "advisor_agent",
            "timestamp": datetime.now().isoformat(),
            "content": f"Roth IRA account {account_number} has been successfully opened in the system.",
            "type": "update"
        }
        state["messages"].append(message)
        
        # Add decision
        decision = {
            "agent": "operations_agent",
            "timestamp": datetime.now().isoformat(),
            "decision": f"Opened Roth IRA account {account_number}",
            "reasoning": "All validation complete, account creation successful"
        }
        state["decisions"].append(decision)
        
        # Store account_number in state["outcome"]
        state["outcome"] = {"account_number": account_number}
        
        # Set next_actions to advisor_agent for final notification
        state["next_actions"] = [{"agent": "advisor_agent", "action": "notify_client", "priority": "high"}]
    
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
