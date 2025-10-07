"""
Graph construction for the multi-agent workflow system.
Creates and wires up the LangGraph workflow.
"""

from langgraph.graph import StateGraph, END
from .state import WorkflowState
from .agents.orchestrator_agent import OrchestratorAgent
from .agents.advisor_agent import AdvisorAgent
from .agents.operations_agent import OperationsAgent
from .routing import route_next_node


def build_workflow_graph():
    """
    Build and compile the workflow graph with LLM-powered agents.
    Returns a compiled LangGraph application.
    """
    
    # Initialize agents
    orchestrator = OrchestratorAgent()
    advisor_agent = AdvisorAgent()
    operations_agent = OperationsAgent()
    
    # Initialize StateGraph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes with LLM agents
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


# Create compiled app
app = build_workflow_graph()
