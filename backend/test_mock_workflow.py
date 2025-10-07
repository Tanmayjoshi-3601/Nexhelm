"""
Test the mock workflow system to verify the structure works.
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_mock_workflow():
    """Test the mock workflow system."""
    
    print("🚀 Starting Mock Workflow System Test")
    print("=" * 50)
    
    try:
        from app.workflow.state import WorkflowState
        from app.workflow.mock_graph import build_mock_workflow_graph
        
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
        
        print(f"🧪 Testing mock workflow for: {initial_state['request']['type']}")
        print(f"Client: {initial_state['request']['client_id']}")
        print("=" * 60)
        
        # Build and run the mock workflow
        app = build_mock_workflow_graph()
        
        print("🤖 Running mock workflow...")
        result = app.invoke(initial_state)
        
        print("\n" + "=" * 60)
        print("WORKFLOW COMPLETED")
        print("=" * 60)
        print(f"Status: {result['status']}")
        print(f"Workflow ID: {result['workflow_id']}")
        print(f"Tasks Completed: {len([t for t in result['tasks'] if t['status'] == 'completed'])}/{len(result['tasks'])}")
        print(f"Messages Exchanged: {len(result['messages'])}")
        
        if result['outcome']:
            print(f"Outcome: {result['outcome']}")
        
        print("=" * 60)
        
        # Show task details
        print("\n📋 Task Details:")
        for task in result['tasks']:
            print(f"  - {task['id']}: {task['description']} (Status: {task['status']}, Owner: {task['owner']})")
        
        # Show messages
        print("\n📝 Messages:")
        for msg in result['messages']:
            print(f"  {msg['from_agent']}: {msg['content']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting Mock Workflow Test")
    print("=" * 50)
    
    success = test_mock_workflow()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Mock workflow test passed! The workflow structure is working correctly.")
    else:
        print("❌ Mock workflow test failed. Please check the errors above.")
    print("=" * 50)
