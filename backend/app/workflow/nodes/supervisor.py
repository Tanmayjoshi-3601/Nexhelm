"""
Supervisor node for routing between agents.
Determines which node to execute next based on workflow state.
"""

from typing import List
from ..state import WorkflowState


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


def supervisor_node(state: WorkflowState) -> str:
    """
    Supervisor node that determines which node to execute next.
    Returns string indicating next node name.
    """
    
    # 1. Check completion
    if state["status"] == "completed":
        return "end"
    if state["status"] == "failed":
        return "end"
    
    # 2. Check next_actions
    if state["next_actions"]:
        # Get first action's agent field
        first_action = state["next_actions"][0]
        agent = first_action["agent"]
        
        if agent == "advisor_agent":
            return "advisor_agent"
        elif agent == "operations_agent":
            return "operations_agent"
    
    # 3. Fallback: Find first task with status "pending" and no unmet dependencies
    if state["status"] == "in_progress":
        for task in state["tasks"]:
            if (task["status"] == "pending" and 
                check_task_dependencies(task, state["tasks"])):
                return task["owner"]
    
    # 4. Default fallback
    return "end"
