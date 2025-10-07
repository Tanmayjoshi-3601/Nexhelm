"""
Routing logic for the workflow system.
Determines which node to execute next based on workflow state.
"""

from typing import List
from .state import WorkflowState


def check_task_dependencies(task: dict, all_tasks: List[dict]) -> bool:
    """
    Returns True if all dependencies are completed.
    Helper function to check if a task's dependencies are met.
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


def route_next_node(state: WorkflowState) -> str:
    """
    Routing function that determines which node to execute next.
    Returns string indicating next node name.
    """
    
    # 1. Check completion
    if state["status"] == "completed":
        print(f"🔄 ROUTING: Workflow completed, ending")
        return "end"
    if state["status"] == "failed":
        print(f"🔄 ROUTING: Workflow failed, ending")
        return "end"
    
    # 2. Check if all tasks are completed
    completed_tasks = len([t for t in state["tasks"] if t["status"] == "completed"])
    total_tasks = len(state["tasks"])
    
    if total_tasks > 0 and completed_tasks >= total_tasks:
        print(f"🔄 ROUTING: All {total_tasks} tasks completed, ending workflow")
        state["status"] = "completed"
        return "end"
    
    # 3. Check next_actions
    if state["next_actions"]:
        # Get first action's agent field
        first_action = state["next_actions"][0]
        agent = first_action["agent"]
        action = first_action.get("action", "unknown action")
        
        print(f"🔄 ROUTING: Next action for {agent}: {action}")
        
        if agent == "advisor_agent":
            return "advisor_agent"
        elif agent == "operations_agent":
            return "operations_agent"
    
    # 4. Fallback: Find first task with status "pending" and no unmet dependencies
    if state["status"] == "in_progress":
        for task in state["tasks"]:
            if (task["status"] == "pending" and 
                check_task_dependencies(task, state["tasks"])):
                print(f"🔄 ROUTING: Found pending task '{task['id']}' for {task['owner']}")
                return task["owner"]
    
    # 5. Default fallback
    print(f"🔄 ROUTING: No more actions available, ending workflow")
    state["status"] = "failed"  # Mark as failed if we can't find next steps
    return "end"
