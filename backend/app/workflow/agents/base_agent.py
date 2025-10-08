"""
Base class for LLM-powered agents in the workflow system.
Provides common functionality for all agents.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
from dotenv import load_dotenv
from ..state import WorkflowState
from ..tools.agent_tools import agent_tools

# Load environment variables from .env file
load_dotenv()


class BaseAgent:
    """
    Base class for all LLM-powered agents.
    Provides common functionality for agent communication and tool usage.
    """
    
    def __init__(self, name: str, role: str, system_prompt: str):
        """
        Initialize the agent.
        
        Args:
            name: Agent name (e.g., 'advisor_agent', 'operations_agent')
            role: Agent role description
            system_prompt: System prompt defining agent behavior
        """
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.tools = agent_tools
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')  # Much cheaper than GPT-4
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize cache for this agent
        self._cache = {}
    
    def call_llm(self, messages: List[Dict[str, str]], temperature: float = 0.3) -> str:
        """
        Call the LLM with the given messages.
        Includes caching to reduce API costs.
        
        Args:
            messages: List of message dictionaries
            temperature: Temperature for response generation
            
        Returns:
            LLM response text
        """
        # Simple caching based on message content
        cache_key = str(hash(str(messages) + str(temperature)))
        if hasattr(self, '_cache') and cache_key in self._cache:
            print(f"🔗 {self.name.upper()}: Using cached LLM response")
            return self._cache[cache_key]
        
        print(f"🔗 {self.name.upper()}: Making LLM API call...")
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': 1000
        }
        
        try:
            print(f"🔗 {self.name.upper()}: Sending request to OpenAI API...")
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30  # Increased timeout for complex prompts
            )
            
            print(f"🔗 {self.name.upper()}: Received response (status: {response.status_code})")
            
            if response.status_code != 200:
                error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
                print(f" {self.name.upper()}: {error_msg}")
                raise Exception(error_msg)
            
            response_data = response.json()
            content = response_data['choices'][0]['message']['content']
            print(f" {self.name.upper()}: LLM response received ({len(content)} chars)")
            
            # Cache the response
            if not hasattr(self, '_cache'):
                self._cache = {}
            self._cache[cache_key] = content
            
            return content
            
        except requests.exceptions.Timeout:
            error_msg = "LLM API call timed out"
            print(f" {self.name.upper()}: {error_msg}")
            return f"Error: {error_msg}"
        except requests.exceptions.ConnectionError:
            error_msg = "LLM API connection failed"
            print(f" {self.name.upper()}: {error_msg}")
            return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"LLM call failed: {str(e)}"
            print(f" {self.name.upper()}: {error_msg}")
            return f"Error: {error_msg}"
    
    def get_available_tools(self) -> List[Dict[str, str]]:
        """
        Get list of available tools for this agent.
        
        Returns:
            List of tool descriptions
        """
        return self.tools.get_available_tools()
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool with the given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        if not hasattr(self.tools, tool_name):
            return {"error": f"Tool {tool_name} not found"}
        
        try:
            tool_func = getattr(self.tools, tool_name)
            result = tool_func(**kwargs)
            return result
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def parse_agent_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the agent's response to extract actions and reasoning.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed response with actions and reasoning
        """
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                return json.loads(response)
            
            # If not JSON, try to extract structured information
            lines = response.strip().split('\n')
            parsed = {
                "reasoning": "",
                "actions": [],
                "next_steps": [],
                "status": "continue"
            }
            
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.lower().startswith("reasoning:"):
                    current_section = "reasoning"
                    parsed["reasoning"] = line[10:].strip()
                elif line.lower().startswith("actions:"):
                    current_section = "actions"
                elif line.lower().startswith("next steps:"):
                    current_section = "next_steps"
                elif line.lower().startswith("status:"):
                    parsed["status"] = line[7:].strip().lower()
                elif current_section == "reasoning":
                    parsed["reasoning"] += " " + line
                elif current_section == "actions" and line.startswith("-"):
                    parsed["actions"].append(line[1:].strip())
                elif current_section == "next_steps" and line.startswith("-"):
                    parsed["next_steps"].append(line[1:].strip())
            
            return parsed
            
        except Exception as e:
            return {
                "reasoning": response,
                "actions": [],
                "next_steps": [],
                "status": "continue",
                "error": f"Failed to parse response: {str(e)}"
            }
    
    def add_message_to_state(self, state: WorkflowState, content: str, message_type: str = "update") -> None:
        """
        Add a message to the workflow state.
        
        Args:
            state: Current workflow state
            content: Message content
            message_type: Type of message
        """
        message = {
            "from_agent": self.name,
            "to_agent": "workflow_system",
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "type": message_type
        }
        state["messages"].append(message)
    
    def add_decision_to_state(self, state: WorkflowState, decision: str, reasoning: str) -> None:
        """
        Add a decision to the workflow state.
        
        Args:
            state: Current workflow state
            decision: Decision made
            reasoning: Reasoning behind the decision
        """
        decision_record = {
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "reasoning": reasoning
        }
        state["decisions"].append(decision_record)
    
    def add_blocker_to_state(self, state: WorkflowState, description: str, assigned_to: str = None) -> None:
        """
        Add a blocker to the workflow state.
        
        Args:
            state: Current workflow state
            description: Blocker description
            assigned_to: Agent assigned to resolve the blocker
        """
        blocker = {
            "id": f"blocker_{len(state['blockers']) + 1}",
            "description": description,
            "identified_by": self.name,
            "assigned_to": assigned_to or "advisor_agent",
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        state["blockers"].append(blocker)
    
    def process_workflow_state(self, state: WorkflowState) -> WorkflowState:
        """
        Process the workflow state and return updated state.
        This method should be implemented by subclasses.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        raise NotImplementedError("Subclasses must implement process_workflow_state")
    
    def get_context_for_llm(self, state: WorkflowState) -> str:
        """
        Get context information for the LLM based on current state.
        
        Args:
            state: Current workflow state
            
        Returns:
            Context string for LLM
        """
        context_parts = [
            f"Workflow ID: {state.get('workflow_id', 'N/A')}",
            f"Request Type: {state.get('request', {}).get('type', 'N/A')}",
            f"Client ID: {state.get('request', {}).get('client_id', 'N/A')}",
            f"Current Status: {state.get('status', 'N/A')}",
        ]
        
        # Add task information
        if state.get('tasks'):
            context_parts.append("\nCurrent Tasks:")
            for task in state['tasks']:
                context_parts.append(f"  - {task['id']}: {task['description']} (Status: {task['status']}, Owner: {task['owner']})")
        
        # Add recent messages
        if state.get('messages'):
            context_parts.append("\nRecent Messages:")
            for msg in state['messages'][-3:]:  # Last 3 messages
                context_parts.append(f"  - {msg['from_agent']} to {msg['to_agent']}: {msg['content']}")
        
        # Add active blockers
        if state.get('blockers'):
            active_blockers = [b for b in state['blockers'] if b['status'] == 'active']
            if active_blockers:
                context_parts.append("\nActive Blockers:")
                for blocker in active_blockers:
                    context_parts.append(f"  - {blocker['description']}")
        
        return "\n".join(context_parts)
