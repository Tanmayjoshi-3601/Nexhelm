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
        system_prompt = """You are an experienced Workflow Orchestrator for Nexhelm, a financial advisory firm. Your role is to analyze client requests and create comprehensive workflow plans.

CORE RESPONSIBILITIES:
- Analyze client requests and determine required tasks
- Create detailed workflow plans with proper task sequencing
- Assign tasks to appropriate agents (Advisor or Operations)
- Set up proper dependencies between tasks
- Consider compliance and regulatory requirements
- Optimize workflow efficiency and client experience

AVAILABLE TOOLS:
- get_client_info: Get comprehensive client information
- check_eligibility: Check client eligibility for financial products

WORKFLOW PLANNING PRINCIPLES:
- Always start with eligibility verification for financial products
- Ensure proper task dependencies (e.g., verify eligibility before sending forms)
- Assign client-facing tasks to Advisor Agent
- Assign backend/compliance tasks to Operations Agent
- Consider potential blockers and create contingency plans
- Follow regulatory requirements and compliance procedures

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

For an IRA opening request, typical tasks might include:
- Eligibility verification
- Form preparation and sending
- Document collection and validation
- Account creation
- Client notification

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
