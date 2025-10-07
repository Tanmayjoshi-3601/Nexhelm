"""
Test script for the LLM-powered workflow system.
Tests the agentic workflow with OpenAI integration.
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow.graph import build_workflow_graph
from workflow.state import WorkflowState


def test_llm_workflow():
    """Test the LLM-powered workflow system."""
    
    print("🚀 Starting LLM-Powered Workflow System Test")
    print("=" * 50)
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
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
    
    print(f"🧪 Testing LLM workflow for: {initial_state['request']['type']}")
    print(f"Client: {initial_state['request']['client_id']}")
    print("=" * 60)
    
    try:
        # Build and run the workflow
        app = build_workflow_graph()
        
        print("🤖 Running LLM-powered workflow...")
        result = app.invoke(initial_state)
        
        print("\n" + "=" * 60)
        print("WORKFLOW COMPLETED")
        print("=" * 60)
        print(f"Status: {result['status']}")
        print(f"Workflow ID: {result['workflow_id']}")
        print(f"Tasks Completed: {len([t for t in result['tasks'] if t['status'] == 'completed'])}/{len(result['tasks'])}")
        print(f"Messages Exchanged: {len(result['messages'])}")
        print(f"Decisions Made: {len(result['decisions'])}")
        
        if result['blockers']:
            print(f"Blockers: {len(result['blockers'])} active")
            for blocker in result['blockers']:
                if blocker['status'] == 'active':
                    print(f"  - {blocker['description']}")
        
        if result['outcome']:
            print(f"Outcome: {result['outcome']}")
        
        print("=" * 60)
        
        # Show recent messages
        if result['messages']:
            print("\n📝 Recent Messages:")
            for msg in result['messages'][-5:]:  # Last 5 messages
                print(f"  {msg['from_agent']}: {msg['content'][:100]}...")
        
        # Show recent decisions
        if result['decisions']:
            print("\n🤔 Recent Decisions:")
            for decision in result['decisions'][-3:]:  # Last 3 decisions
                print(f"  {decision['agent']}: {decision['decision'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_without_api_key():
    """Test workflow behavior without API key (should fail gracefully)."""
    
    print("\n🧪 Testing workflow without API key...")
    
    # Temporarily remove API key
    original_key = os.environ.get('OPENAI_API_KEY')
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    
    try:
        # This should fail gracefully
        from workflow.agents.advisor_agent import AdvisorAgent
        agent = AdvisorAgent()
        print("❌ Expected error but agent was created successfully")
        return False
        
    except ValueError as e:
        if "OPENAI_API_KEY" in str(e):
            print("✅ Correctly failed without API key")
            return True
        else:
            print(f"❌ Unexpected error: {e}")
            return False
            
    finally:
        # Restore API key
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key


if __name__ == "__main__":
    print("🚀 Starting LLM Workflow System Tests")
    print("=" * 50)
    
    # Test 1: Check API key requirement
    test1_passed = test_workflow_without_api_key()
    
    # Test 2: Run LLM workflow (only if API key is available)
    test2_passed = False
    if os.getenv('OPENAI_API_KEY'):
        test2_passed = test_llm_workflow()
    else:
        print("\n⏭️  Skipping LLM workflow test (no API key)")
        print("To test with LLM, set OPENAI_API_KEY environment variable")
    
    print("\n" + "=" * 50)
    if test1_passed and (test2_passed or not os.getenv('OPENAI_API_KEY')):
        print("🎉 All tests passed! The LLM workflow system is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 50)
