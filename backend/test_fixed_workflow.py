"""
Test the fixed LLM workflow system with improved error handling and task completion.
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_fixed_workflow():
    """Test the fixed LLM workflow system."""
    
    print("🚀 Starting Fixed LLM Workflow System Test")
    print("=" * 50)
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        return False
    
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
        
        print(f"🧪 Testing fixed workflow for: {initial_state['request']['type']}")
        print(f"Client: {initial_state['request']['client_id']}")
        print("=" * 60)
        
        # Build and run the workflow with recursion limit
        app = build_workflow_graph()
        
        print("🤖 Running fixed LLM workflow...")
        
        # Set recursion limit to prevent infinite loops
        config = {"recursion_limit": 15}
        result = app.invoke(initial_state, config=config)
        
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
        
        # Show task details
        print("\n📋 Task Details:")
        for task in result['tasks']:
            print(f"  - {task['id']}: {task['description']} (Status: {task['status']}, Owner: {task['owner']})")
        
        # Show recent messages
        print("\n📝 Recent Messages:")
        for msg in result['messages'][-5:]:  # Last 5 messages
            print(f"  {msg['from_agent']}: {msg['content'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting Fixed Workflow Test")
    print("=" * 50)
    
    success = test_fixed_workflow()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Fixed workflow test completed! Check the results above.")
    else:
        print("❌ Fixed workflow test failed. Please check the errors above.")
    print("=" * 50)
