"""
Main entry point for the workflow system.
Executes workflows and provides testing interface.
"""

from .graph import build_workflow_graph
from .state import WorkflowState
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def run_workflow(client_id: str, request_type: str):
    """
    Execute workflow for given request.
    
    Args:
        client_id: ID of the client
        request_type: Type of request (e.g., "open_roth_ira")
    
    Returns:
        Final workflow state
    """
    
    # Initialize state
    initial_state = {
        "request": {
            "type": request_type,
            "client_id": client_id,
            "client_name": "",  # Will be filled by orchestrator
            "initiator": "sarah_advisor"
        },
        "workflow_id": "",
        "status": "pending",
        "created_at": "",
        "updated_at": "",
        "context": {},
        "tasks": [],
        "messages": [],
        "decisions": [],
        "blockers": [],
        "next_actions": [],
        "outcome": None
    }
    
    # Build and invoke workflow
    print(f"\n{'='*60}")
    print(f"Starting LLM-powered workflow: {request_type}")
    print(f"Client: {client_id}")
    print(f"{'='*60}\n")
    
    # Build the LLM-powered workflow graph
    app = build_workflow_graph()
    
    # Set recursion limit to prevent infinite loops
    config = {"recursion_limit": 20}
    result = app.invoke(initial_state, config=config)
    
    # Print results
    print(f"\n{'='*60}")
    print("WORKFLOW COMPLETED")
    print(f"{'='*60}")
    print(f"Status: {result['status']}")
    print(f"Workflow ID: {result['workflow_id']}")
    print(f"\nTasks Completed: {len([t for t in result['tasks'] if t['status'] == 'completed'])}/{len(result['tasks'])}")
    print(f"\nMessages Exchanged: {len(result['messages'])}")
    print(f"\nDecisions Made: {len(result['decisions'])}")
    
    if result['outcome']:
        print(f"\nOutcome: {result['outcome']}")
    
    if result['blockers']:
        active_blockers = [b for b in result['blockers'] if b['status'] == 'active']
        print(f"\nBlockers: {len(active_blockers)} active")
        for blocker in active_blockers:
            print(f"  - {blocker['description']}")
    
    print(f"\n{'='*60}\n")
    
    return result


def run_workflow_with_detailed_output(client_id: str, request_type: str):
    """
    Run workflow and print detailed state information.
    Useful for debugging and understanding workflow execution.
    """
    
    result = run_workflow(client_id, request_type)
    
    # Print detailed state
    print("\n=== DETAILED STATE ===")
    print(f"Tasks: {result['tasks']}")
    print(f"\nMessages: {result['messages']}")
    print(f"\nDecisions: {result['decisions']}")
    
    if result['blockers']:
        print(f"\nBlockers: {result['blockers']}")
    
    return result


def run_sample_workflows():
    """Run sample workflows to demonstrate the system."""
    
    print("🚀 Starting Nexhelm LLM-Powered Agentic Workflow System")
    print("=" * 60)
    
    # Sample workflow 1: Open Roth IRA
    print("\n📋 Sample Workflow 1: Open Roth IRA")
    result1 = run_workflow(
        client_id="john_smith_123",
        request_type="open_roth_ira"
    )
    
    # Sample workflow 2: Open Traditional IRA (if you want to test different types)
    # print("\n📋 Sample Workflow 2: Open Traditional IRA")
    # result2 = run_workflow(
    #     client_id="jane_doe_456", 
    #     request_type="open_traditional_ira"
    # )
    
    return result1


if __name__ == "__main__":
    # Check for API key (now loaded from .env file)
    if not os.getenv('OPENAI_API_KEY'):
        print(" Error: OPENAI_API_KEY not found in .env file")
        print("Please add your OpenAI API key to the .env file:")
        print("OPENAI_API_KEY=your-api-key-here")
        exit(1)
    
    print("OpenAI API key loaded from .env file")
    
    # Run sample workflows
    result = run_sample_workflows()
    
    # Print detailed state for the last workflow
    print("\n=== DETAILED STATE ===")
    print(f"Tasks: {result['tasks']}")
    print(f"\nMessages: {result['messages']}")
    print(f"\nDecisions: {result['decisions']}")
    
    if result['blockers']:
        print(f"\nBlockers: {result['blockers']}")
