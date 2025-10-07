"""
Simple test to debug the workflow system.
"""

print("🚀 Starting Simple Test")
print("=" * 50)

try:
    print("🔍 Testing basic imports...")
    
    # Test basic imports
    from app.workflow.state import WorkflowState
    print("✅ WorkflowState imported")
    
    from app.workflow.agents.base_agent import BaseAgent
    print("✅ BaseAgent imported")
    
    from app.workflow.agents.orchestrator_agent import OrchestratorAgent
    print("✅ OrchestratorAgent imported")
    
    print("\n🔍 Testing agent creation...")
    
    # Test agent creation
    orchestrator = OrchestratorAgent()
    print("✅ OrchestratorAgent created")
    
    print("\n🔍 Testing graph creation...")
    
    from app.workflow.graph import build_workflow_graph
    app = build_workflow_graph()
    print("✅ Graph created")
    
    print("\n🔍 Testing simple workflow...")
    
    # Create simple state
    from datetime import datetime
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
    
    # Try to run workflow
    print("🚀 Starting workflow...")
    result = app.invoke(initial_state)
    print("✅ Workflow completed!")
    
    print(f"📊 Final status: {result['status']}")
    print(f"📊 Tasks: {len(result['tasks'])}")
    print(f"📊 Messages: {len(result['messages'])}")
    
    print("\n🎉 All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
