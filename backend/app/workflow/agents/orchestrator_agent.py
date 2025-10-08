"""
LLM-powered Orchestrator Agent for workflow planning.
Dynamically generates tasks and plans workflow execution.
"""

import uuid
from typing import Dict, Any, List
from .base_agent import BaseAgent
from ..state import WorkflowState
from datetime import datetime


class OrchestratorAgent(BaseAgent):
    """
    LLM-powered Orchestrator Agent that plans and initiates workflows.
    Dynamically generates tasks based on the request type and client context.
    """
    
    def __init__(self):
        system_prompt = """You are an intelligent Workflow Orchestrator for Nexhelm, a financial advisory firm. You autonomously design workflows by understanding business processes, compliance requirements, and client needs.

YOUR INTELLIGENCE & AUTONOMY:
- Analyze requests and determine the optimal sequence of tasks
- Understand financial workflows (account opening, transfers, compliance, etc.)
- Make intelligent decisions about task assignment and dependencies
- Adapt to different request types and client contexts
- Balance efficiency, compliance, and client experience

AVAILABLE TOOLS (for planning):
- get_client_info: Understand client context before planning
- check_eligibility: Verify feasibility during planning

AGENT CAPABILITIES (for task assignment):
- **Advisor Agent**: Client communication, forms, advice, notifications, relationship management
- **Operations Agent**: Backend operations, compliance, validation, account management, system tasks

PLANNING APPROACH:
- Think through the business logic: What needs to happen for this request to succeed?
- Create clear, actionable tasks (describe WHAT, let agents decide HOW)
- Set up logical dependencies and sequencing
- Consider compliance and risk factors
- Assign tasks based on agent capabilities

NOTE: Our validation system checks for critical missing steps (like account creation). Focus on intelligent workflow design.

RESPONSE FORMAT:
Always respond in JSON format with the following structure:
{
    "reasoning": "Your analysis of the request and planning approach",
    "workflow_plan": {
        "tasks": [
            {
                "id": "task_1",
                "description": "Detailed task description",
                "owner": "advisor_agent|operations_agent",
                "dependencies": ["task_id1", "task_id2"],
                "priority": "high|medium|low",
                "estimated_duration": "time_estimate"
            }
        ],
        "estimated_total_duration": "total_time_estimate",
        "potential_blockers": ["potential_issue1", "potential_issue2"],
        "success_criteria": ["criteria1", "criteria2"]
    },
    "client_context": "Summary of client situation and requirements",
    "compliance_considerations": "Any regulatory or compliance requirements"
}

Remember: Create comprehensive, realistic workflows that ensure successful completion while maintaining compliance."""

        super().__init__(
            name="orchestrator_agent",
            role="Workflow Orchestrator - Planning and Task Generation",
            system_prompt=system_prompt
        )
    
    def create_workflow_plan(self, state: WorkflowState) -> WorkflowState:
        """
        Create a comprehensive workflow plan based on the request.
        
        Args:
            state: Initial workflow state
            
        Returns:
            Updated workflow state with generated tasks
        """
        print(f"🤖 {self.name.upper()}: Creating workflow plan...")
        
        # Get client information for context
        client_id = state.get("request", {}).get("client_id")
        request_type = state.get("request", {}).get("type", "")
        
        # Get client context
        client_info = self.execute_tool("get_client_info", client_id=client_id)
        
        # Build the prompt
        prompt = f"""You are the Orchestrator Agent. Analyze the client request and create a comprehensive workflow plan.

CLIENT REQUEST:
- Request Type: {request_type}
- Client ID: {client_id}

CLIENT CONTEXT:
{client_info if 'error' not in client_info else 'Client information not available'}

INSTRUCTIONS:
1. Analyze the request type and determine what needs to be accomplished
2. Create a detailed task list with proper sequencing and dependencies
3. Assign each task to the appropriate agent (advisor_agent or operations_agent)
4. Consider potential blockers and compliance requirements
5. Estimate durations and set priorities
6. Define success criteria for the workflow

PRINCIPLES FOR WORKFLOW PLANNING:

1. **Analyze the Request Autonomously**: 
   - Understand what the client wants to achieve
   - Determine the logical sequence of steps needed
   - Consider compliance, risk, and client experience

2. **Task Assignment Guidelines**:
   - Client-facing tasks (communications, forms, advice) → advisor_agent
   - Backend/compliance tasks (verification, validation, account operations) → operations_agent
   - Consider dependencies and logical flow

3. **Critical Business Requirements** (for account opening requests):
   - Financial products require eligibility verification
   - Accounts cannot be opened without proper validation
   - Clients must be notified of outcomes
   - Compliance and regulatory requirements must be met

4. **Task Quality**:
   - Tasks should be clear and actionable (but don't dictate exact tools - let agents decide)
   - Break complex operations into logical steps
   - Ensure proper sequencing and dependencies

5. **Autonomy vs. Safety**:
   - Use your intelligence to create the best workflow
   - Our validation system will check for critical missing steps (like account creation)
   - Focus on WHAT needs to happen, not HOW (agents will decide the HOW)

EXAMPLE (for opening a Roth IRA):
Think: "Client wants a Roth IRA. They need: eligibility check → forms → validation → account creation → notification"
Create tasks that reflect this logic, but let the agents autonomously decide which tools to use.

IMPORTANT: You are an intelligent orchestrator, not a script executor. Design workflows that make business sense.

Create a realistic, comprehensive workflow plan."""

        # Call LLM
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = self.call_llm(messages)
        print(f"🤖 {self.name.upper()}: LLM Response received")
        
        # Parse the response
        parsed_response = self.parse_agent_response(response)
        
        # Fallback if LLM failed or timed out
        if "Error:" in response or not parsed_response.get("workflow_plan"):
            print(f"🤖 {self.name.upper()}: LLM failed, using fallback logic")
            parsed_response = self._create_fallback_plan(request_type, client_info)
        
        # Extract workflow plan
        workflow_plan = parsed_response.get("workflow_plan", {})
        tasks = workflow_plan.get("tasks", [])
        
        # Convert LLM-generated tasks to our task format
        formatted_tasks = []
        for i, task in enumerate(tasks, 1):
            formatted_task = {
                "id": task.get("id", f"task_{i}"),
                "description": task.get("description", f"Task {i}"),
                "owner": task.get("owner", "operations_agent"),
                "status": "pending",
                "dependencies": task.get("dependencies", []),
                "result": None,
                "priority": task.get("priority", "medium"),
                "estimated_duration": task.get("estimated_duration", "unknown")
            }
            formatted_tasks.append(formatted_task)
        
        # CRITICAL: Validate and enforce required tasks based on request type
        formatted_tasks = self._validate_and_enforce_tasks(formatted_tasks, request_type)
        
        # Update state with generated tasks
        state["tasks"] = formatted_tasks
        state["workflow_id"] = str(uuid.uuid4())
        state["status"] = "in_progress"
        state["created_at"] = datetime.now().isoformat()
        state["updated_at"] = datetime.now().isoformat()
        
        # Add context information
        if "error" not in client_info:
            client = client_info.get("client", {})
            state["context"] = {
                "client_age": client.get("age", 0),
                "existing_accounts": client.get("existing_accounts", []),
                "available_documents": client_info.get("available_documents", []),
                "client_income": client.get("income", 0)
            }
            state["request"]["client_name"] = client.get("name", "Unknown Client")
        else:
            state["context"] = {
                "client_age": 0,
                "existing_accounts": [],
                "available_documents": [],
                "client_income": 0
            }
        
        # Add orchestrator's analysis to state
        reasoning = parsed_response.get("reasoning", "Workflow plan created")
        self.add_message_to_state(state, reasoning, "workflow_planning")
        self.add_decision_to_state(state, "Created comprehensive workflow plan", reasoning)
        
        # Set initial next actions
        if formatted_tasks:
            first_task = formatted_tasks[0]
            state["next_actions"] = [{
                "agent": first_task["owner"],
                "action": first_task["description"],
                "priority": first_task["priority"]
            }]
        
        # Add workflow metadata
        state["workflow_metadata"] = {
            "estimated_total_duration": workflow_plan.get("estimated_total_duration", "unknown"),
            "potential_blockers": workflow_plan.get("potential_blockers", []),
            "success_criteria": workflow_plan.get("success_criteria", []),
            "client_context": parsed_response.get("client_context", ""),
            "compliance_considerations": parsed_response.get("compliance_considerations", "")
        }
        
        print(f"🤖 {self.name.upper()}: Workflow plan created with {len(formatted_tasks)} tasks")
        return state
    
    def generate_dynamic_tasks(self, request_type: str, client_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate tasks dynamically based on request type and client context.
        
        Args:
            request_type: Type of request (e.g., "open_roth_ira")
            client_context: Client information and context
            
        Returns:
            List of generated tasks
        """
        # This method can be used for more dynamic task generation
        # For now, we'll use the LLM-based approach in create_workflow_plan
        
        if "roth_ira" in request_type.lower():
            return self._generate_ira_tasks(client_context)
        elif "traditional_ira" in request_type.lower():
            return self._generate_ira_tasks(client_context)
        else:
            return self._generate_generic_tasks(request_type, client_context)
    
    def _generate_ira_tasks(self, client_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate tasks for IRA opening workflows."""
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
        
        return tasks
    
    def _create_fallback_plan(self, request_type: str, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fallback workflow plan when LLM fails."""
        print(f"🤖 {self.name.upper()}: Creating fallback plan for {request_type}")
        
        # Use the existing hardcoded task generation
        tasks = self._generate_ira_tasks(client_info) if "ira" in request_type.lower() else self._generate_generic_tasks(request_type, client_info)
        
        return {
            "reasoning": f"Created fallback workflow plan for {request_type} due to LLM timeout",
            "workflow_plan": {
                "tasks": tasks,
                "estimated_total_duration": "30-45 minutes",
                "potential_blockers": ["Missing client documents", "Income eligibility issues"],
                "success_criteria": ["Account opened successfully", "Client notified"]
            },
            "client_context": "Using fallback logic due to LLM timeout",
            "compliance_considerations": "Standard IRA opening procedures"
        }
    
    def _generate_generic_tasks(self, request_type: str, client_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate generic tasks for unknown request types."""
        return [
            {
                "id": "task_1",
                "description": f"Analyze and process {request_type} request",
                "owner": "operations_agent",
                "status": "pending",
                "dependencies": [],
                "result": None,
                "priority": "high",
                "estimated_duration": "10-15 minutes"
            },
            {
                "id": "task_2",
                "description": f"Complete {request_type} workflow",
                "owner": "advisor_agent",
                "status": "pending",
                "dependencies": ["task_1"],
                "result": None,
                "priority": "high",
                "estimated_duration": "5-10 minutes"
            }
        ]
    
    def _validate_and_enforce_tasks(self, tasks: List[Dict[str, Any]], request_type: str) -> List[Dict[str, Any]]:
        """
        Validate task list and ensure critical tasks are present based on request type.
        This is a CRITICAL method to ensure LLM doesn't forget important tasks.
        
        Args:
            tasks: List of tasks from LLM
            request_type: The type of request (e.g., "open_roth_ira")
            
        Returns:
            Validated and corrected task list
        """
        print(f"🔍 {self.name.upper()}: Validating task list for {request_type}")
        
        # For IRA opening requests, ensure account creation task exists
        if "ira" in request_type.lower() or "open" in request_type.lower():
            
            # Debug: Print all tasks for inspection
            print(f"🔍 {self.name.upper()}: Checking {len(tasks)} tasks for account creation:")
            for task in tasks:
                desc_lower = task.get("description", "").lower()
                owner = task.get("owner", "")
                has_keywords = (
                    ("open_account" in desc_lower) or
                    ("create" in desc_lower and "account" in desc_lower) or
                    ("open" in desc_lower and "account" in desc_lower)
                )
                print(f"   - Task {task.get('id')}: owner={owner}, has_keywords={has_keywords}, desc='{task.get('description', '')[:60]}...'")
            
            # Check if account creation task exists (look for various patterns)
            has_account_creation = any(
                (
                    ("open_account" in task.get("description", "").lower()) or
                    ("create" in task.get("description", "").lower() and "account" in task.get("description", "").lower()) or
                    ("open" in task.get("description", "").lower() and "account" in task.get("description", "").lower())
                ) and
                task.get("owner") == "operations_agent"
                for task in tasks
            )
            
            print(f"🔍 {self.name.upper()}: has_account_creation = {has_account_creation}")
            
            if not has_account_creation:
                print(f"⚠️  {self.name.upper()}: CRITICAL - Account creation task missing! Adding it now...")
                
                # Find the last validation task to insert account creation after
                validation_task_index = -1
                for i, task in enumerate(tasks):
                    if "validat" in task.get("description", "").lower():
                        validation_task_index = i
                
                # Find the last operations task to get proper dependency
                last_ops_task_id = None
                for task in tasks:
                    if task.get("owner") == "operations_agent":
                        last_ops_task_id = task.get("id")
                
                # Create account creation task with explicit tool hint
                account_type = "roth_ira" if "roth" in request_type.lower() else "traditional_ira"
                account_task_id = f"task_{len(tasks) + 1}"
                account_creation_task = {
                    "id": account_task_id,
                    "description": f"Execute open_account tool to create {account_type} account for the client",
                    "owner": "operations_agent",
                    "status": "pending",
                    "dependencies": [last_ops_task_id] if last_ops_task_id else [],
                    "result": None,
                    "priority": "high",
                    "estimated_duration": "5-10 minutes"
                }
                
                # Insert after validation task, or at position before last task
                insert_position = validation_task_index + 1 if validation_task_index >= 0 else len(tasks) - 1
                tasks.insert(insert_position, account_creation_task)
                
                # Update notification task dependencies if it exists
                for task in tasks:
                    if "notif" in task.get("description", "").lower() and task.get("owner") == "advisor_agent":
                        task["dependencies"] = [account_task_id]
                
                print(f"✅ {self.name.upper()}: Added account creation task at position {insert_position}")
        
        # Re-number task IDs to be sequential
        for i, task in enumerate(tasks, 1):
            old_id = task["id"]
            new_id = f"task_{i}"
            task["id"] = new_id
            
            # Update dependencies to use new IDs
            for t in tasks:
                if old_id in t.get("dependencies", []):
                    t["dependencies"] = [new_id if dep == old_id else dep for dep in t["dependencies"]]
        
        print(f"✅ {self.name.upper()}: Task validation complete - {len(tasks)} tasks")
        return tasks
