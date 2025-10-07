"""
Mock graph for testing the workflow structure without LLM calls.
"""

from langgraph.graph import StateGraph, END
from .state import WorkflowState
from .agents.mock_agent import MockOrchestratorAgent, MockAdvisorAgent, MockOperationsAgent
from .routing import route_next_node


def build_mock_workflow_graph():
    """
    Build and compile the mock workflow graph without LLM calls.
    Returns a compiled LangGraph application.
    """
    
    # Initialize mock agents
    orchestrator = MockOrchestratorAgent()
    advisor_agent = MockAdvisorAgent()
    operations_agent = MockOperationsAgent()
    
    # Initialize StateGraph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes with mock agents
    workflow.add_node("orchestrator", orchestrator.create_workflow_plan)
    workflow.add_node("advisor_agent", advisor_agent.process_workflow_state)
    workflow.add_node("operations_agent", operations_agent.process_workflow_state)
    
    # Set entry point
    workflow.set_entry_point("orchestrator")
    
    # Add conditional edges from orchestrator
    workflow.add_conditional_edges(
        "orchestrator",
        route_next_node,  # Routing function
        {
            "advisor_agent": "advisor_agent",
            "operations_agent": "operations_agent",
            "end": END
        }
    )
    
    # Add conditional edges from advisor_agent
    workflow.add_conditional_edges(
        "advisor_agent",
        route_next_node,  # Routing function
        {
            "advisor_agent": "advisor_agent",
            "operations_agent": "operations_agent",
            "end": END
        }
    )
    
    # Add conditional edges from operations_agent
    workflow.add_conditional_edges(
        "operations_agent",
        route_next_node,  # Routing function
        {
            "advisor_agent": "advisor_agent",
            "operations_agent": "operations_agent",
            "end": END
        }
    )
    
    # Compile and return
    return workflow.compile()


# Create compiled mock app
mock_app = build_mock_workflow_graph()
