"""
LLM-powered Operations Agent for backend tasks.
Handles compliance, account management, and system operations.
"""

from typing import Dict, Any
from datetime import datetime
from .base_agent import BaseAgent
from ..state import WorkflowState


class OperationsAgent(BaseAgent):
    """
    LLM-powered Operations Agent that handles backend operations.
    Specializes in compliance, account management, and system operations.
    """
    
    def __init__(self):
        system_prompt = """You are an experienced Operations Agent working for Nexhelm, a financial advisory firm. Your role is to handle all backend operations and compliance tasks.

CORE RESPONSIBILITIES:
- Compliance verification and regulatory checks
- Account creation and management
- Document validation and processing
- Risk assessment and eligibility verification
- System integration and data processing
- Quality assurance and error handling

AVAILABLE TOOLS:
- get_client_info(client_id): Get comprehensive client information
- get_document(client_id, doc_type): Retrieve client documents
- update_document(client_id, doc_type, data): Update client documents
- create_document(client_id, doc_type, data): Create new documents for clients
- open_account(client_id, account_type): Open new accounts for clients
- get_account(account_number): Retrieve account information
- check_eligibility(client_id, product_type): Verify client eligibility for products
- validate_document(client_id, doc_type): Validate document completeness and accuracy

DECISION MAKING:
- Always prioritize compliance and regulatory requirements
- Be thorough in verification processes
- Identify and escalate potential issues or blockers
- Ensure data accuracy and system integrity
- Follow established procedures and best practices

RESPONSE FORMAT:
Always respond in JSON format with the following structure:
{
    "reasoning": "Your analysis of the current situation and what needs to be done",
    "actions": ["List of specific actions you will take"],
    "next_steps": ["What should happen next in the workflow"],
    "status": "continue|completed|failed|blocked",
    "compliance_notes": "Any compliance or regulatory considerations",
    "tools_to_use": [{"tool": "tool_name", "params": {"param1": "value1"}}],  <-- CRITICAL: Use ONLY ONE tool per task!
    "blockers": ["Any issues that need to be resolved"],
    "task_completion": "Describe what task you completed (if any)"
}

CRITICAL: In tools_to_use, include ONLY ONE tool - the one that matches the current task!

INTELLIGENT TOOL SELECTION:
You have access to these tools - choose the RIGHT ONE based on what the task requires:

1. **check_eligibility(client_id, product_type)**: Verify if client qualifies for a financial product
2. **validate_document(client_id, doc_type)**: Check if a document is valid and complete
3. **get_document(client_id, doc_type)**: Retrieve a specific document
4. **open_account(client_id, account_type)**: Create a new financial account
5. **get_client_info(client_id)**: Get comprehensive client information
6. **create_document/update_document**: Manage client documents

DECISION MAKING GUIDELINES:
- Read the task description carefully and understand the intent
- Choose the tool that BEST accomplishes the task objective
- For account creation tasks: use open_account (account_type: "roth_ira", "traditional_ira", etc.)
- For validation tasks: use validate_document with specific doc types like "driver's license", "tax return", "IRA application"
- For document retrieval: use get_document
- Use ONLY ONE tool per task execution

IMPORTANT CONSTRAINTS:
- NEVER pass lists or arrays to tools - always use single string values
- For document types, use specific names: "driver's license", "tax return", "IRA application"
- Avoid generic names like "documents", "submitted_documents", "required_documents"
- Always include required parameters: client_id is almost always needed

CRITICAL ERROR HANDLING RULES:
- BEFORE creating an account: Check if client already has this account type
- If a tool returns {"success": false} or {"error": "..."} → STOP immediately and create a BLOCKER
- If check_eligibility returns {"eligible": false} → DO NOT proceed, set status to "blocked"
- If validate_document returns {"valid": false} → DO NOT proceed, set status to "blocked"
- NEVER create accounts for ineligible clients or when documents are invalid
- If account already exists → set status to "blocked", DO NOT mark task as completed

IMPORTANT: 
- Work on ONE task at a time - mark ONLY the current task as completed
- Check tool results for errors BEFORE proceeding to next tool
- If you successfully open an account, set status to "completed" and next_steps to []
- Use exact parameter names: client_id, doc_type, product_type, account_type
- DO NOT use multiple tools for a single task - use only the tool that matches the task description

Remember: You are responsible for ensuring all operations meet regulatory standards and company policies."""

        super().__init__(
            name="operations_agent",
            role="Operations Specialist - Compliance and Backend Operations",
            system_prompt=system_prompt
        )
    
    def process_workflow_state(self, state: WorkflowState) -> WorkflowState:
        """
        Process the workflow state as an Operations Agent.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        print(f"🤖 {self.name.upper()}: Analyzing workflow state...")
        
        # Get context for LLM
        context = self.get_context_for_llm(state)
        
        # Build the prompt
        prompt = f"""You are the Operations Agent in a financial workflow system. Analyze the current situation and determine what backend operations need to be completed.

CURRENT SITUATION:
{context}

AVAILABLE TOOLS:
{self.get_available_tools()}

INSTRUCTIONS:
1. Analyze the current workflow state
2. Determine what backend operations need to be completed
3. Use appropriate tools to gather information or take actions
4. Check for compliance and regulatory requirements
5. Identify any potential blockers or issues
6. Provide clear reasoning for your decisions
7. Suggest next steps for the workflow

Remember: Focus on compliance, accuracy, and ensuring all regulatory requirements are met."""

        # Call LLM
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = self.call_llm(messages)
        print(f"🤖 {self.name.upper()}: LLM Response received")
        
        # Parse the response
        parsed_response = self.parse_agent_response(response)
        
        # Execute any tools specified - CRITICAL: Execute ONLY the first tool per task
        if "tools_to_use" in parsed_response:
            # Limit to first tool only to enforce ONE TOOL PER TASK rule
            tools_list = parsed_response["tools_to_use"]
            if len(tools_list) > 1:
                print(f"⚠️  {self.name.upper()}: LLM requested {len(tools_list)} tools, but will execute ONLY the first one per task")
            
            for tool_call in tools_list[:1]:  # Execute ONLY the first tool
                tool_name = tool_call["tool"]
                tool_params = tool_call.get("params", {})
                
                print(f"🔧 {self.name.upper()}: Executing tool '{tool_name}' with params: {tool_params}")
                result = self.execute_tool(tool_name, **tool_params)
                print(f"🔧 {self.name.upper()}: Tool result: {result}")
                
                # CRITICAL: Check for errors in tool results
                # Handle case where result might not be a dict
                if not isinstance(result, dict):
                    error_msg = f"Tool returned invalid format: {result}"
                    print(f"❌ {self.name.upper()}: Tool '{tool_name}' returned non-dict: {error_msg}")
                    self.add_blocker_to_state(state, f"{tool_name} failed: {error_msg}")
                    for task in state["tasks"]:
                        if task["owner"] == "operations_agent" and task["status"] == "pending":
                            task["status"] = "failed"
                            task["result"] = f"Failed: {error_msg}"
                            print(f"❌ {self.name.upper()}: Marked task '{task['id']}' as failed")
                            break
                    state["status"] = "blocked"
                    state["next_actions"] = []
                    return state
                
                if result.get("success") == False or "error" in result:
                    error_msg = result.get("error") or result.get("message", "Unknown error")
                    print(f"❌ {self.name.upper()}: Tool '{tool_name}' failed: {error_msg}")
                    
                    # Create blocker and stop execution
                    self.add_blocker_to_state(state, f"{tool_name} failed: {error_msg}")
                    
                    # Mark task as failed
                    for task in state["tasks"]:
                        if task["owner"] == "operations_agent" and task["status"] == "pending":
                            task["status"] = "failed"
                            task["result"] = f"Failed: {error_msg}"
                            print(f"❌ {self.name.upper()}: Marked task '{task['id']}' as failed")
                            break
                    
                    state["status"] = "blocked"
                    state["next_actions"] = []
                    return state
                
                # Check eligibility tool - stop if not eligible
                if tool_name == "check_eligibility":
                    if result.get("eligible") == False:
                        reason = result.get("reason", "Eligibility check failed")
                        print(f"❌ {self.name.upper()}: Client not eligible: {reason}")
                        self.add_blocker_to_state(state, f"Eligibility failed: {reason}")
                        
                        for task in state["tasks"]:
                            if task["owner"] == "operations_agent" and task["status"] == "pending":
                                task["status"] = "failed"
                                task["result"] = f"Ineligible: {reason}"
                                print(f"❌ {self.name.upper()}: Marked task '{task['id']}' as failed")
                                break
                        
                        state["status"] = "blocked"
                        state["next_actions"] = []
                        return state
                
                # Check validation tool - stop if invalid
                if tool_name == "validate_document":
                    if result.get("valid") == False:
                        errors = result.get("errors", ["Validation failed"])
                        error_msg = "; ".join(errors)
                        print(f"❌ {self.name.upper()}: Document validation failed: {error_msg}")
                        self.add_blocker_to_state(state, f"Document validation failed: {error_msg}")
                        
                        for task in state["tasks"]:
                            if task["owner"] == "operations_agent" and task["status"] == "pending":
                                task["status"] = "failed"
                                task["result"] = f"Validation failed: {error_msg}"
                                print(f"❌ {self.name.upper()}: Marked task '{task['id']}' as failed")
                                break
                        
                        state["status"] = "blocked"
                        state["next_actions"] = []
                        return state
                
                # Check if account was successfully created
                if tool_name == "open_account" and result.get("success") == True and "account" in result:
                    account_info = result["account"]
                    if "account_number" in account_info:
                        print(f"🎉 {self.name.upper()}: Account created successfully! {account_info['account_number']}")
                        
                        # Set workflow outcome
                        state["outcome"] = {
                            "account_number": account_info["account_number"],
                            "account_type": account_info.get("account_type", "roth_ira"),
                            "status": account_info["status"],
                            "created_at": account_info["created_at"]
                        }
        
        # Add message to state
        reasoning = parsed_response.get("reasoning", "No reasoning provided")
        self.add_message_to_state(state, reasoning, "analysis")
        
        # Add decision to state
        decision = f"Operations Agent analysis: {reasoning}"
        self.add_decision_to_state(state, decision, reasoning)
        
        # Handle task completion if agent completed a task
        if "task_completion" in parsed_response and parsed_response["task_completion"]:
            # Find and mark ONLY THE FIRST pending task as completed
            task_marked = False
            for task in state["tasks"]:
                if task["owner"] == "operations_agent" and task["status"] == "pending" and not task_marked:
                    task["status"] = "completed"
                    task["result"] = parsed_response["task_completion"]
                    print(f"🤖 {self.name.upper()}: Marked task '{task['id']}' as completed")
                    task_marked = True
                    break
        
        # Handle compliance notes
        if "compliance_notes" in parsed_response and parsed_response["compliance_notes"]:
            compliance_message = f"Compliance Note: {parsed_response['compliance_notes']}"
            self.add_message_to_state(state, compliance_message, "compliance")
        
        # Handle blockers
        if "blockers" in parsed_response and parsed_response["blockers"]:
            for blocker_desc in parsed_response["blockers"]:
                self.add_blocker_to_state(state, blocker_desc, "advisor_agent")
        
        # Update next actions based on agent's recommendations
        if "next_steps" in parsed_response:
            next_actions = []
            for step in parsed_response["next_steps"]:
                # Determine which agent should handle the next step
                if any(keyword in step.lower() for keyword in ["send", "notify", "communicate", "client"]):
                    next_actions.append({
                        "agent": "advisor_agent",
                        "action": step,
                        "priority": "high"
                    })
                else:
                    next_actions.append({
                        "agent": "operations_agent",
                        "action": step,
                        "priority": "high"
                    })
            
            state["next_actions"] = next_actions
        else:
            # If no next steps, check if we should complete the workflow
            completed_tasks = len([t for t in state["tasks"] if t["status"] == "completed"])
            total_tasks = len(state["tasks"])
            
            if completed_tasks >= total_tasks and total_tasks > 0:
                state["status"] = "completed"
                state["next_actions"] = []
                print(f"🤖 {self.name.upper()}: All tasks completed, ending workflow")
            elif not state["next_actions"]:
                # No more actions and not all tasks completed - something went wrong
                state["status"] = "failed"
                state["next_actions"] = []
                print(f"🤖 {self.name.upper()}: No more actions available, marking workflow as failed")
        
        # Update workflow status based on agent's assessment
        agent_status = parsed_response.get("status", "continue")
        if agent_status == "completed":
            # Mark ONLY ONE task as completed
            task_marked = False
            for task in state["tasks"]:
                if task["owner"] == "operations_agent" and task["status"] == "pending" and not task_marked:
                    task["status"] = "completed"
                    task["result"] = parsed_response.get("task_completion", "Task completed by operations agent")
                    print(f"🤖 {self.name.upper()}: Marked task '{task['id']}' as completed")
                    task_marked = True
                    break
            # Don't set workflow status to completed here - let routing system handle it
        elif agent_status == "failed" or agent_status == "blocked":
            state["status"] = "failed"
        
        # If agent is continuing but has done work, mark ONE task as completed
        if agent_status == "continue" and "tools_to_use" in parsed_response and parsed_response["tools_to_use"]:
            # Check if we successfully executed tools and should mark task as completed
            tools_executed = parsed_response.get("tools_to_use", [])
            if tools_executed:
                # Mark ONLY THE FIRST pending task as completed
                task_marked = False
                for task in state["tasks"]:
                    if task["owner"] == "operations_agent" and task["status"] == "pending" and not task_marked:
                        task["status"] = "completed"
                        task["result"] = f"Completed task using tools: {[t.get('tool', 'unknown') for t in tools_executed]}"
                        print(f"🤖 {self.name.upper()}: Marked task '{task['id']}' as completed after tool execution")
                        task_marked = True
                        break
        
        # Update timestamp
        state["updated_at"] = datetime.now().isoformat()
        
        print(f"🤖 {self.name.upper()}: Processing complete. Status: {agent_status}")
        return state
    
    def handle_specific_task(self, state: WorkflowState, task_description: str) -> WorkflowState:
        """
        Handle a specific task based on its description.
        
        Args:
            state: Current workflow state
            task_description: Description of the task to handle
            
        Returns:
            Updated workflow state
        """
        print(f"🤖 {self.name.upper()}: Handling task: {task_description}")
        
        # Get client information
        client_id = state.get("request", {}).get("client_id")
        client_info = self.execute_tool("get_client_info", client_id=client_id)
        
        if "error" in client_info:
            self.add_blocker_to_state(state, f"Could not retrieve client information: {client_info['error']}")
            return state
        
        # Handle different types of tasks
        if "verify" in task_description.lower() and "eligibility" in task_description.lower():
            return self._handle_eligibility_verification(state, client_info)
        elif "validate" in task_description.lower() and "application" in task_description.lower():
            return self._handle_application_validation(state, client_info)
        elif "open" in task_description.lower() and "account" in task_description.lower():
            return self._handle_account_creation(state, client_info)
        elif "check" in task_description.lower():
            return self._handle_compliance_check(state, client_info)
        else:
            # Generic task handling
            return self._handle_generic_task(state, task_description, client_info)
    
    def _handle_eligibility_verification(self, state: WorkflowState, client_info: Dict[str, Any]) -> WorkflowState:
        """Handle eligibility verification tasks."""
        client_id = state.get("request", {}).get("client_id")
        request_type = state.get("request", {}).get("type", "")
        
        # Determine product type from request
        product_type = "roth_ira" if "roth" in request_type.lower() else "traditional_ira"
        
        # Check eligibility
        eligibility_result = self.execute_tool("check_eligibility", client_id=client_id, product_type=product_type)
        
        if "error" in eligibility_result:
            self.add_blocker_to_state(state, f"Eligibility check failed: {eligibility_result['error']}")
            return state
        
        if eligibility_result["eligible"]:
            # Client is eligible
            reasoning = eligibility_result["reason"]
            self.add_message_to_state(state, f"Eligibility verified: {reasoning}", "eligibility_verified")
            self.add_decision_to_state(
                state,
                f"Confirmed {product_type.upper()} eligibility",
                reasoning
            )
            
            # Set next action for advisor agent
            state["next_actions"] = [{
                "agent": "advisor_agent",
                "action": "send_application_form",
                "priority": "high"
            }]
        else:
            # Client is not eligible
            reason = eligibility_result["reason"]
            self.add_blocker_to_state(state, reason)
            self.add_message_to_state(state, f"Eligibility check failed: {reason}", "eligibility_failed")
            state["status"] = "failed"
            state["next_actions"] = []
        
        return state
    
    def _handle_application_validation(self, state: WorkflowState, client_info: Dict[str, Any]) -> WorkflowState:
        """Handle application validation tasks."""
        client_id = state.get("request", {}).get("client_id")
        
        # Validate the IRA application
        validation_result = self.execute_tool("validate_document", client_id=client_id, doc_type="ira_application")
        
        if "error" in validation_result:
            self.add_blocker_to_state(state, f"Document validation failed: {validation_result['error']}")
            return state
        
        if validation_result["valid"]:
            # Application is valid
            self.add_message_to_state(state, "IRA application validated successfully", "validation_success")
            self.add_decision_to_state(
                state,
                "Approved IRA application form",
                "All required signatures and information present"
            )
            
            # Set next action for account creation
            state["next_actions"] = [{
                "agent": "operations_agent",
                "action": "open_account",
                "priority": "high"
            }]
        else:
            # Application has issues
            errors = validation_result["errors"]
            warnings = validation_result["warnings"]
            
            if errors:
                # Critical errors - workflow fails
                error_message = "; ".join(errors)
                self.add_blocker_to_state(state, f"Application validation failed: {error_message}")
                self.add_message_to_state(state, f"Application validation failed: {error_message}", "validation_failed")
                state["status"] = "failed"
                state["next_actions"] = []
            else:
                # Only warnings - continue but notify advisor
                warning_message = "; ".join(warnings)
                self.add_message_to_state(state, f"Application validation warnings: {warning_message}", "validation_warnings")
                
                # Continue with account creation
                state["next_actions"] = [{
                    "agent": "operations_agent",
                    "action": "open_account",
                    "priority": "high"
                }]
        
        return state
    
    def _handle_account_creation(self, state: WorkflowState, client_info: Dict[str, Any]) -> WorkflowState:
        """Handle account creation tasks."""
        client_id = state.get("request", {}).get("client_id")
        request_type = state.get("request", {}).get("type", "")
        
        # Determine account type from request
        account_type = "roth_ira" if "roth" in request_type.lower() else "traditional_ira"
        
        # Open the account
        account_result = self.execute_tool("open_account", client_id=client_id, account_type=account_type)
        
        if "error" in account_result:
            self.add_blocker_to_state(state, f"Account creation failed: {account_result['error']}")
            return state
        
        # Account created successfully
        account_number = account_result["account"]["account_number"]
        self.add_message_to_state(state, f"Account {account_number} opened successfully", "account_created")
        self.add_decision_to_state(
            state,
            f"Opened {account_type.upper()} account {account_number}",
            "All validation complete, account creation successful"
        )
        
        # Store account information in outcome
        state["outcome"] = {"account_number": account_number, "account_type": account_type}
        
        # Set next action for advisor agent to notify client
        state["next_actions"] = [{
            "agent": "advisor_agent",
            "action": "notify_client_account_opened",
            "priority": "high"
        }]
        
        return state
    
    def _handle_compliance_check(self, state: WorkflowState, client_info: Dict[str, Any]) -> WorkflowState:
        """Handle compliance and regulatory checks."""
        # This would involve various compliance checks
        # For now, we'll add a message about compliance verification
        self.add_message_to_state(state, "Compliance checks completed", "compliance_verified")
        return state
    
    def _handle_generic_task(self, state: WorkflowState, task_description: str, client_info: Dict[str, Any]) -> WorkflowState:
        """Handle generic operations tasks."""
        self.add_message_to_state(state, f"Handling operations task: {task_description}", "task_handling")
        return state
