"""
Simple test for LLM agents with improved error handling.
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_llm_agent_creation():
    """Test if LLM agents can be created."""
    print("🔍 Testing LLM agent creation...")
    
    try:
        from app.workflow.agents.orchestrator_agent import OrchestratorAgent
        
        print("Creating OrchestratorAgent...")
        orchestrator = OrchestratorAgent()
        print("✅ OrchestratorAgent created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_api_call():
    """Test a simple LLM API call."""
    print("\n🔍 Testing LLM API call...")
    
    try:
        from app.workflow.agents.orchestrator_agent import OrchestratorAgent
        
        orchestrator = OrchestratorAgent()
        
        # Test simple API call
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, I am working!' in exactly those words."}
        ]
        
        print("Making test LLM call...")
        response = orchestrator.call_llm(messages)
        print(f"✅ LLM Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM API call failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_workflow():
    """Test a simple workflow with LLM agents."""
    print("\n🔍 Testing simple LLM workflow...")
    
    try:
        from app.workflow.state import WorkflowState
        from app.workflow.graph import build_workflow_graph
        
        # Create initial state
        initial_state: WorkflowState = {
            "request": {
                "type": "open_roth_ira",
                "client_id": "john_smith_123",
                "client_name": "John Smith",
                "initiator": "sarah_advisor"
            },
            "workflow_id": "",
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "context": {},
            "tasks": [],
            "messages": [],
            "decisions": [],
            "blockers": [],
            "next_actions": [],
            "outcome": None
        }
        
        print("Building workflow graph...")
        app = build_workflow_graph()
        
        print("Starting workflow execution...")
        result = app.invoke(initial_state)
        
        print(f"✅ Workflow completed with status: {result['status']}")
        return True
        
    except Exception as e:
        print(f"❌ Simple workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting LLM Agent Tests")
    print("=" * 50)
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        exit(1)
    
    print("✅ OpenAI API key is set")
    
    # Test 1: Agent creation
    test1_passed = test_llm_agent_creation()
    
    if test1_passed:
        # Test 2: Simple API call
        test2_passed = test_llm_api_call()
        
        if test2_passed:
            # Test 3: Simple workflow
            test3_passed = test_simple_workflow()
        else:
            test3_passed = False
    else:
        test2_passed = False
        test3_passed = False
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Agent Creation: {'✅' if test1_passed else '❌'}")
    print(f"  LLM API Call: {'✅' if test2_passed else '❌'}")
    print(f"  Simple Workflow: {'✅' if test3_passed else '❌'}")
    print("=" * 50)
