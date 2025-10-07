"""
State schema definition for the multi-agent workflow system.
Defines the WorkflowState TypedDict that all nodes will use.
"""

from typing import TypedDict, List, Dict, Optional


class WorkflowState(TypedDict):
    """
    State schema for the multi-agent workflow system.
    All nodes read from and write to this shared state.
    """
    
    # Request information
    request: dict
    # Fields:
    #   - type: str (e.g., "open_roth_ira")
    #   - client_id: str
    #   - client_name: str
    #   - initiator: str (advisor name)
    
    # Workflow metadata
    workflow_id: str  # UUID format
    status: str  # Allowed values: "pending", "in_progress", "completed", "failed"
    created_at: str  # ISO timestamp
    updated_at: str  # ISO timestamp
    
    # Client context
    context: dict
    # Fields:
    #   - client_age: int
    #   - existing_accounts: List[str]
    #   - available_documents: List[str]
    
    # Task management
    tasks: List[dict]
    # Each task dict contains:
    #   - id: str
    #   - description: str
    #   - owner: str ("advisor_agent" or "operations_agent")
    #   - status: str ("pending", "in_progress", "completed", "failed")
    #   - dependencies: List[str] (list of task IDs)
    #   - result: Optional[str]
    
    # Agent communication
    messages: List[dict]
    # Each message dict contains:
    #   - from_agent: str
    #   - to_agent: str
    #   - timestamp: str (ISO format)
    #   - content: str
    #   - type: str ("question", "response", "update")
    
    # Decision tracking
    decisions: List[dict]
    # Each decision dict contains:
    #   - agent: str
    #   - timestamp: str
    #   - decision: str
    #   - reasoning: str
    
    # Blocker management
    blockers: List[dict]
    # Each blocker dict contains:
    #   - id: str
    #   - description: str
    #   - identified_by: str
    #   - assigned_to: str
    #   - status: str ("active", "resolved")
    #   - created_at: str
    
    # Next actions
    next_actions: List[dict]
    # Each action dict contains:
    #   - agent: str
    #   - action: str
    #   - priority: str ("low", "medium", "high")
    
    # Final outcome
    outcome: Optional[dict]
