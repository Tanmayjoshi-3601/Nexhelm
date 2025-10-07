"""
LLM-powered Advisor Agent for client-facing tasks.
Handles client communication, form management, and notifications.
"""

from typing import Dict, Any
from datetime import datetime
from .base_agent import BaseAgent
from ..state import WorkflowState


class AdvisorAgent(BaseAgent):
    """
    LLM-powered Advisor Agent that handles client-facing tasks.
    Specializes in client communication, form management, and notifications.
    """
    
    def __init__(self):
        system_prompt = """You are an experienced Financial Advisor Agent working for Nexhelm, a financial advisory firm. Your role is to handle all client-facing tasks and communications.

CORE RESPONSIBILITIES:
- Client communication and relationship management
- Sending and collecting forms and documents
- Explaining financial products and processes to clients
- Managing client expectations and timelines
- Coordinating with Operations Agent for backend processes

AVAILABLE TOOLS:
- get_client_info(client_id): Get comprehensive client information
- update_client_info(client_id, field, value): Update client information in CRM
- get_document(client_id, doc_type): Retrieve client documents
- update_document(client_id, doc_type, data): Update client documents
- create_document(client_id, doc_type, data): Create new documents for clients
- send_notification(client_id, message_type, content): Send notifications to clients
- validate_document(client_id, doc_type): Validate document completeness

DECISION MAKING:
- Always prioritize client experience and satisfaction
- Be proactive in communicating with clients
- Escalate complex issues to Operations Agent when needed
- Ensure all client communications are clear and professional
- Follow compliance requirements for client interactions

RESPONSE FORMAT:
Always respond in JSON format with the following structure:
{
    "reasoning": "Your analysis of the current situation and what needs to be done",
    "actions": ["List of specific actions you will take"],
    "next_steps": ["What should happen next in the workflow"],
    "status": "continue|completed|failed|needs_help",
    "client_message": "Message to send to client (if applicable)",
    "tools_to_use": [{"tool": "tool_name", "params": {"param1": "value1"}}],
    "task_completion": "Describe what task you completed (if any)"
}

IMPORTANT: 
- If you complete a task, set status to "completed" and describe the completion in task_completion
- If you notify client of successful account opening, set status to "completed" and next_steps to []
- If all tasks are done, set status to "completed" and next_steps to []
- Use exact parameter names: client_id, doc_type, message_type, content, product_type
- When client is notified of account opening, the workflow should end immediately

Remember: You are the client's primary point of contact. Always be helpful, professional, and proactive."""

        super().__init__(
            name="advisor_agent",
            role="Financial Advisor - Client Communication Specialist",
            system_prompt=system_prompt
        )
    
    def process_workflow_state(self, state: WorkflowState) -> WorkflowState:
        """
        Process the workflow state as an Advisor Agent.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        print(f"🤖 {self.name.upper()}: Analyzing workflow state...")
        
        # Get context for LLM
        context = self.get_context_for_llm(state)
        
        # Build the prompt
        prompt = f"""You are the Advisor Agent in a financial workflow system. Analyze the current situation and determine what actions to take.

CURRENT SITUATION:
{context}

AVAILABLE TOOLS:
{self.get_available_tools()}

INSTRUCTIONS:
1. Analyze the current workflow state
2. Determine what client-facing tasks need to be completed
3. Use appropriate tools to gather information or take actions
4. Provide clear reasoning for your decisions
5. Suggest next steps for the workflow

Remember: Focus on client communication, form management, and ensuring the client has a smooth experience."""

        # Call LLM
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = self.call_llm(messages)
        print(f"🤖 {self.name.upper()}: LLM Response received")
        
        # Parse the response
        parsed_response = self.parse_agent_response(response)
        
        # Execute any tools specified
        if "tools_to_use" in parsed_response:
            for tool_call in parsed_response["tools_to_use"]:
                tool_name = tool_call["tool"]
                tool_params = tool_call.get("params", {})
                
                print(f"🔧 {self.name.upper()}: Executing tool '{tool_name}' with params: {tool_params}")
                result = self.execute_tool(tool_name, **tool_params)
                print(f"🔧 {self.name.upper()}: Tool result: {result}")
        
        # Add message to state
        reasoning = parsed_response.get("reasoning", "No reasoning provided")
        self.add_message_to_state(state, reasoning, "analysis")
        
        # Add decision to state
        decision = f"Advisor Agent analysis: {reasoning}"
        self.add_decision_to_state(state, decision, reasoning)
        
        # Handle task completion if agent completed a task
        if "task_completion" in parsed_response and parsed_response["task_completion"]:
            # Find and mark the current task as completed
            for task in state["tasks"]:
                if task["owner"] == "advisor_agent" and task["status"] == "pending":
                    task["status"] = "completed"
                    task["result"] = parsed_response["task_completion"]
                    print(f"🤖 {self.name.upper()}: Marked task '{task['id']}' as completed")
                    break
        
        # Handle client message if provided
        if "client_message" in parsed_response and parsed_response["client_message"]:
            client_message = parsed_response["client_message"]
            print(f"📧 {self.name.upper()}: Sending message to client: {client_message}")
            
            # Send notification to client
            client_id = state.get("request", {}).get("client_id", "unknown")
            notification_result = self.execute_tool(
                "send_notification",
                client_id=client_id,
                message_type="advisor_communication",
                content=client_message
            )
            
            self.add_message_to_state(state, f"Sent message to client: {client_message}", "client_communication")
            
            # Check if this is a completion notification (account opened)
            if "account" in client_message.lower() and ("opened" in client_message.lower() or "created" in client_message.lower()):
                print(f"🎉 {self.name.upper()}: Client notified of account opening!")
                
                # Mark current task as completed
                for task in state["tasks"]:
                    if task["owner"] == "advisor_agent" and task["status"] == "pending":
                        task["status"] = "completed"
                        task["result"] = "Client notified of successful account opening"
                        break
                
                # Check if all tasks are now completed
                completed_tasks = len([t for t in state["tasks"] if t["status"] == "completed"])
                total_tasks = len(state["tasks"])
                
                if completed_tasks >= total_tasks:
                    print(f"🎉 {self.name.upper()}: All tasks completed - workflow complete!")
                    state["status"] = "completed"
                    state["next_actions"] = []
                else:
                    print(f"📋 {self.name.upper()}: {completed_tasks}/{total_tasks} tasks completed, continuing workflow...")
                    state["next_actions"] = []
                
                return state
        
        # Update next actions based on agent's recommendations
        if "next_steps" in parsed_response:
            next_actions = []
            for step in parsed_response["next_steps"]:
                # Determine which agent should handle the next step
                if any(keyword in step.lower() for keyword in ["verify", "validate", "check", "open", "create", "process"]):
                    next_actions.append({
                        "agent": "operations_agent",
                        "action": step,
                        "priority": "high"
                    })
                else:
                    next_actions.append({
                        "agent": "advisor_agent",
                        "action": step,
                        "priority": "medium"
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
            state["status"] = "completed"
        elif agent_status == "failed":
            state["status"] = "failed"
        
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
        if "send" in task_description.lower() and "form" in task_description.lower():
            return self._handle_send_form_task(state, client_info)
        elif "notify" in task_description.lower():
            return self._handle_notification_task(state, client_info)
        elif "collect" in task_description.lower() or "gather" in task_description.lower():
            return self._handle_collection_task(state, client_info)
        else:
            # Generic task handling
            return self._handle_generic_task(state, task_description, client_info)
    
    def _handle_send_form_task(self, state: WorkflowState, client_info: Dict[str, Any]) -> WorkflowState:
        """Handle sending forms to clients."""
        client = client_info["client"]
        client_name = client.get("name", "Client")
        
        # Create personalized message
        message = f"""Dear {client_name},

I hope this message finds you well. As part of your financial planning process, I need to send you an IRA application form to complete your account setup.

The form has been pre-filled with your known information to make the process as smooth as possible. Please review all sections carefully and ensure you sign on page 3.

If you have any questions or need assistance completing the form, please don't hesitate to contact me.

Best regards,
Your Financial Advisor"""

        # Send notification
        client_id = state.get("request", {}).get("client_id")
        self.execute_tool(
            "send_notification",
            client_id=client_id,
            message_type="form_sent",
            content=message
        )
        
        self.add_message_to_state(state, f"Sent IRA application form to {client_name}", "form_sent")
        self.add_decision_to_state(
            state,
            f"Sent personalized IRA application form to {client_name}",
            "Client is existing customer, pre-filled form with known details for better experience"
        )
        
        # Set next action for operations agent
        state["next_actions"] = [{
            "agent": "operations_agent",
            "action": "wait_for_form_submission",
            "priority": "medium"
        }]
        
        return state
    
    def _handle_notification_task(self, state: WorkflowState, client_info: Dict[str, Any]) -> WorkflowState:
        """Handle client notifications."""
        client = client_info["client"]
        client_name = client.get("name", "Client")
        
        # Check if account was opened successfully
        outcome = state.get("outcome", {})
        if outcome and "account_number" in outcome:
            account_number = outcome["account_number"]
            message = f"""Dear {client_name},

Great news! Your Roth IRA account has been successfully opened.

Account Details:
- Account Number: {account_number}
- Account Type: Roth IRA
- Status: Active

You can now begin making contributions to your Roth IRA. Remember, you can contribute up to $7,000 for 2024 (or $8,000 if you're 50 or older).

If you have any questions about your new account or would like to discuss contribution strategies, please don't hesitate to reach out.

Congratulations on taking this important step toward your retirement goals!

Best regards,
Your Financial Advisor"""
        else:
            message = f"""Dear {client_name},

I wanted to provide you with an update on your IRA application process. We're currently working through the final steps to get your account set up.

I'll keep you informed of any progress and will notify you as soon as your account is ready.

Thank you for your patience.

Best regards,
Your Financial Advisor"""
        
        # Send notification
        client_id = state.get("request", {}).get("client_id")
        self.execute_tool(
            "send_notification",
            client_id=client_id,
            message_type="status_update",
            content=message
        )
        
        self.add_message_to_state(state, f"Sent status update to {client_name}", "client_notification")
        
        # Mark workflow as completed if account was opened
        if outcome and "account_number" in outcome:
            state["status"] = "completed"
            state["next_actions"] = []
        
        return state
    
    def _handle_collection_task(self, state: WorkflowState, client_info: Dict[str, Any]) -> WorkflowState:
        """Handle document collection tasks."""
        # This would involve following up with clients for missing documents
        # For now, we'll add a message about the collection process
        self.add_message_to_state(state, "Initiated document collection process", "collection_started")
        return state
    
    def _handle_generic_task(self, state: WorkflowState, task_description: str, client_info: Dict[str, Any]) -> WorkflowState:
        """Handle generic advisor tasks."""
        self.add_message_to_state(state, f"Handling advisor task: {task_description}", "task_handling")
        return state
