"""
Mock agents for testing the workflow structure without LLM calls.
"""

from typing import Dict, Any
from datetime import datetime
from ..state import WorkflowState


class MockOrchestratorAgent:
    """Mock orchestrator agent that doesn't make LLM calls."""
    
    def __init__(self):
        self.name = "orchestrator_agent"
    
    def create_workflow_plan(self, state: WorkflowState) -> WorkflowState:
        """Create a workflow plan without LLM calls."""
        print(f"🤖 {self.name.upper()}: Creating workflow plan (MOCK)")
        
        # Generate simple tasks
        tasks = [
            {
                "id": "task_1",
                "description": "Verify IRA income eligibility and regulatory requirements",
                "owner": "operations_agent",
                "status": "pending",
                "dependencies": [],
                "result": None,
                "priority": "high",
                "estimated_duration": "5-10 minutes"
            },
            {
                "id": "task_2", 
                "description": "Send personalized IRA application form to client",
                "owner": "advisor_agent",
                "status": "pending",
                "dependencies": ["task_1"],
                "result": None,
                "priority": "high",
                "estimated_duration": "2-5 minutes"
            },
            {
                "id": "task_3",
                "description": "Review and validate submitted IRA application for completeness",
                "owner": "operations_agent", 
                "status": "pending",
                "dependencies": ["task_2"],
                "result": None,
                "priority": "high",
                "estimated_duration": "10-15 minutes"
            },
            {
                "id": "task_4",
                "description": "Open IRA account in system and generate account number",
                "owner": "operations_agent",
                "status": "pending", 
                "dependencies": ["task_3"],
                "result": None,
                "priority": "high",
                "estimated_duration": "5-10 minutes"
            },
            {
                "id": "task_5",
                "description": "Notify client of successful account opening and next steps",
                "owner": "advisor_agent",
                "status": "pending",
                "dependencies": ["task_4"],
                "result": None,
                "priority": "high",
                "estimated_duration": "3-5 minutes"
            }
        ]
        
        # Update state
        state["tasks"] = tasks
        state["workflow_id"] = "mock_workflow_123"
        state["status"] = "in_progress"
        state["created_at"] = datetime.now().isoformat()
        state["updated_at"] = datetime.now().isoformat()
        
        # Add context
        state["context"] = {
            "client_age": 45,
            "existing_accounts": ["checking"],
            "available_documents": ["drivers_license"],
            "client_income": 145000
        }
        
        # Add message
        state["messages"].append({
            "from_agent": self.name,
            "to_agent": "workflow_system",
            "timestamp": datetime.now().isoformat(),
            "content": "Created workflow plan with 5 tasks for IRA opening",
            "type": "workflow_planning"
        })
        
        # Set next action
        state["next_actions"] = [{
            "agent": "operations_agent",
            "action": "Verify IRA income eligibility",
            "priority": "high"
        }]
        
        print(f"🤖 {self.name.upper()}: Workflow plan created with {len(tasks)} tasks")
        return state


class MockAdvisorAgent:
    """Mock advisor agent that doesn't make LLM calls."""
    
    def __init__(self):
        self.name = "advisor_agent"
    
    def process_workflow_state(self, state: WorkflowState) -> WorkflowState:
        """Process workflow state without LLM calls."""
        print(f"🤖 {self.name.upper()}: Processing workflow state (MOCK)")
        
        # Find current task for advisor
        current_task = None
        for task in state["tasks"]:
            if task["owner"] == "advisor_agent" and task["status"] == "pending":
                current_task = task
                break
        
        if current_task:
            print(f"🤖 {self.name.upper()}: Handling task: {current_task['description']}")
            
            # Simulate task completion
            current_task["status"] = "completed"
            current_task["result"] = f"Task completed by {self.name}"
            
            # Add message
            state["messages"].append({
                "from_agent": self.name,
                "to_agent": "workflow_system",
                "timestamp": datetime.now().isoformat(),
                "content": f"Completed task: {current_task['description']}",
                "type": "task_completion"
            })
            
            # Set next action
            next_task = None
            for task in state["tasks"]:
                if task["status"] == "pending":
                    # Check dependencies
                    deps_met = True
                    for dep_id in task.get("dependencies", []):
                        dep_task = next((t for t in state["tasks"] if t["id"] == dep_id), None)
                        if not dep_task or dep_task["status"] != "completed":
                            deps_met = False
                            break
                    
                    if deps_met:
                        next_task = task
                        break
            
            if next_task:
                state["next_actions"] = [{
                    "agent": next_task["owner"],
                    "action": next_task["description"],
                    "priority": next_task["priority"]
                }]
            else:
                # All tasks completed
                state["status"] = "completed"
                state["outcome"] = {"account_number": "ROTH_IRA-1000"}
                state["next_actions"] = []
        
        state["updated_at"] = datetime.now().isoformat()
        print(f"🤖 {self.name.upper()}: Processing complete")
        return state


class MockOperationsAgent:
    """Mock operations agent that doesn't make LLM calls."""
    
    def __init__(self):
        self.name = "operations_agent"
    
    def process_workflow_state(self, state: WorkflowState) -> WorkflowState:
        """Process workflow state without LLM calls."""
        print(f"🤖 {self.name.upper()}: Processing workflow state (MOCK)")
        
        # Find current task for operations
        current_task = None
        for task in state["tasks"]:
            if task["owner"] == "operations_agent" and task["status"] == "pending":
                current_task = task
                break
        
        if current_task:
            print(f"🤖 {self.name.upper()}: Handling task: {current_task['description']}")
            
            # Simulate task completion
            current_task["status"] = "completed"
            current_task["result"] = f"Task completed by {self.name}"
            
            # Add message
            state["messages"].append({
                "from_agent": self.name,
                "to_agent": "workflow_system",
                "timestamp": datetime.now().isoformat(),
                "content": f"Completed task: {current_task['description']}",
                "type": "task_completion"
            })
            
            # Set next action
            next_task = None
            for task in state["tasks"]:
                if task["status"] == "pending":
                    # Check dependencies
                    deps_met = True
                    for dep_id in task.get("dependencies", []):
                        dep_task = next((t for t in state["tasks"] if t["id"] == dep_id), None)
                        if not dep_task or dep_task["status"] != "completed":
                            deps_met = False
                            break
                    
                    if deps_met:
                        next_task = task
                        break
            
            if next_task:
                state["next_actions"] = [{
                    "agent": next_task["owner"],
                    "action": next_task["description"],
                    "priority": next_task["priority"]
                }]
            else:
                # All tasks completed
                state["status"] = "completed"
                state["outcome"] = {"account_number": "ROTH_IRA-1000"}
                state["next_actions"] = []
        
        state["updated_at"] = datetime.now().isoformat()
        print(f"🤖 {self.name.upper()}: Processing complete")
        return state
