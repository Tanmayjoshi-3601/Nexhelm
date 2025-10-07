"""
Debug test to isolate issues with the LLM workflow system.
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test if all imports work correctly."""
    print("🔍 Testing imports...")
    
    try:
        from workflow.state import WorkflowState
        print("✅ WorkflowState imported")
    except Exception as e:
        print(f"❌ WorkflowState import failed: {e}")
        return False
    
    try:
        from workflow.agents.base_agent import BaseAgent
        print("✅ BaseAgent imported")
    except Exception as e:
        print(f"❌ BaseAgent import failed: {e}")
        return False
    
    try:
        from workflow.agents.advisor_agent import AdvisorAgent
        print("✅ AdvisorAgent imported")
    except Exception as e:
        print(f"❌ AdvisorAgent import failed: {e}")
        return False
    
    try:
        from workflow.agents.operations_agent import OperationsAgent
        print("✅ OperationsAgent imported")
    except Exception as e:
        print(f"❌ OperationsAgent import failed: {e}")
        return False
    
    try:
        from workflow.agents.orchestrator_agent import OrchestratorAgent
        print("✅ OrchestratorAgent imported")
    except Exception as e:
        print(f"❌ OrchestratorAgent import failed: {e}")
        return False
    
    try:
        from workflow.graph import build_workflow_graph
        print("✅ build_workflow_graph imported")
    except Exception as e:
        print(f"❌ build_workflow_graph import failed: {e}")
        return False
    
    return True


def test_agent_creation():
    """Test if agents can be created."""
    print("\n🔍 Testing agent creation...")
    
    try:
        from workflow.agents.orchestrator_agent import OrchestratorAgent
        orchestrator = OrchestratorAgent()
        print("✅ OrchestratorAgent created")
    except Exception as e:
        print(f"❌ OrchestratorAgent creation failed: {e}")
        return False
    
    try:
        from workflow.agents.advisor_agent import AdvisorAgent
        advisor = AdvisorAgent()
        print("✅ AdvisorAgent created")
    except Exception as e:
        print(f"❌ AdvisorAgent creation failed: {e}")
        return False
    
    try:
        from workflow.agents.operations_agent import OperationsAgent
        operations = OperationsAgent()
        print("✅ OperationsAgent created")
    except Exception as e:
        print(f"❌ OperationsAgent creation failed: {e}")
        return False
    
    return True


def test_graph_creation():
    """Test if the graph can be created."""
    print("\n🔍 Testing graph creation...")
    
    try:
        from workflow.graph import build_workflow_graph
        app = build_workflow_graph()
        print("✅ Graph created successfully")
        return True
    except Exception as e:
        print(f"❌ Graph creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_workflow():
    """Test a simple workflow execution."""
    print("\n🔍 Testing simple workflow execution...")
    
    try:
        from workflow.state import WorkflowState
        from workflow.graph import build_workflow_graph
        
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
        
        print("📝 Initial state created")
        
        # Build graph
        app = build_workflow_graph()
        print("📝 Graph built")
        
        # Try to invoke
        print("🚀 Starting workflow execution...")
        result = app.invoke(initial_state)
        print("✅ Workflow completed")
        
        print(f"📊 Final status: {result['status']}")
        print(f"📊 Tasks: {len(result['tasks'])}")
        print(f"📊 Messages: {len(result['messages'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting Debug Tests")
    print("=" * 50)
    
    # Test 1: Imports
    test1_passed = test_imports()
    
    if test1_passed:
        # Test 2: Agent creation
        test2_passed = test_agent_creation()
        
        if test2_passed:
            # Test 3: Graph creation
            test3_passed = test_graph_creation()
            
            if test3_passed:
                # Test 4: Simple workflow
                test4_passed = test_simple_workflow()
            else:
                test4_passed = False
        else:
            test3_passed = False
            test4_passed = False
    else:
        test2_passed = False
        test3_passed = False
        test4_passed = False
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Imports: {'✅' if test1_passed else '❌'}")
    print(f"  Agent Creation: {'✅' if test2_passed else '❌'}")
    print(f"  Graph Creation: {'✅' if test3_passed else '❌'}")
    print(f"  Workflow Execution: {'✅' if test4_passed else '❌'}")
    print("=" * 50)
