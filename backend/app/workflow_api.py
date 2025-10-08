"""
Workflow API with Server-Sent Events (SSE) streaming
Provides real-time workflow execution updates to frontend
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import json
from datetime import datetime
import sys
from io import StringIO
import contextlib
import os

# Import workflow components
try:
    from .workflow.graph import app as workflow_app
    from .workflow.state import WorkflowState
    from .workflow.storage import get_account_system
except ImportError:
    from app.workflow.graph import app as workflow_app
    from app.workflow.state import WorkflowState
    from app.workflow.storage import get_account_system


router = APIRouter(prefix="/api/workflow", tags=["workflow"])


class WorkflowRequest(BaseModel):
    """Request model for workflow execution"""
    request_type: str
    client_id: str
    client_name: Optional[str] = None
    initiator: Optional[str] = "system"


class WorkflowEventCapture:
    """Captures workflow events for streaming"""
    
    def __init__(self):
        self.event_queue = asyncio.Queue()
        self.original_stdout = sys.stdout
        self.captured_output = StringIO()
    
    async def emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit an event to the queue"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        await self.event_queue.put(event)
    
    def parse_console_output(self, line: str) -> Optional[Dict[str, str]]:
        """Parse console output into structured events"""
        line = line.strip()
        if not line:
            return None
        
        # Agent messages
        if "🤖" in line and ":" in line:
            parts = line.split(":", 1)
            agent = parts[0].replace("🤖", "").strip()
            message = parts[1].strip() if len(parts) > 1 else ""
            return {
                "type": "agent_message",
                "agent": agent,
                "message": message
            }
        
        # Tool execution
        elif "🔧" in line and ":" in line:
            parts = line.split(":", 1)
            agent = parts[0].replace("🔧", "").strip()
            message = parts[1].strip() if len(parts) > 1 else ""
            return {
                "type": "tool_execution",
                "agent": agent,
                "message": message
            }
        
        # LLM calls
        elif "🔗" in line and ":" in line:
            parts = line.split(":", 1)
            agent = parts[0].replace("🔗", "").strip()
            message = parts[1].strip() if len(parts) > 1 else ""
            return {
                "type": "llm_call",
                "agent": agent,
                "message": message
            }
        
        # Routing
        elif "🔄" in line and ":" in line:
            parts = line.split(":", 1)
            message = parts[1].strip() if len(parts) > 1 else line
            return {
                "type": "routing",
                "agent": "ROUTING",
                "message": message
            }
        
        # Success/Complete
        elif "✅" in line or "🎉" in line:
            return {
                "type": "success",
                "agent": "SYSTEM",
                "message": line.replace("✅", "").replace("🎉", "").strip()
            }
        
        # Notifications
        elif "📧" in line:
            return {
                "type": "notification",
                "agent": "NOTIFICATION",
                "message": line.replace("📧", "").strip()
            }
        
        # General output
        else:
            return {
                "type": "log",
                "agent": "SYSTEM",
                "message": line
            }


class RealTimeStdoutCapture:
    """Captures stdout in real-time and emits events"""
    
    def __init__(self, event_capture: WorkflowEventCapture, loop: asyncio.AbstractEventLoop):
        self.event_capture = event_capture
        self.loop = loop
        self.original_stdout = sys.stdout
        self.buffer = []
    
    def write(self, text):
        """Capture stdout writes"""
        self.original_stdout.write(text)  # Also print to console
        self.buffer.append(text)
        
        # If we have a complete line, emit it
        if '\n' in text:
            line = ''.join(self.buffer).strip()
            self.buffer = []
            
            if line:
                # Parse and emit event
                parsed = self.event_capture.parse_console_output(line)
                if parsed:
                    # Schedule event emission in the async loop
                    asyncio.run_coroutine_threadsafe(
                        self.event_capture.emit_event(
                            parsed["type"],
                            {
                                "agent": parsed.get("agent", "SYSTEM"),
                                "message": parsed.get("message", "")
                            }
                        ),
                        self.loop
                    )
    
    def flush(self):
        """Flush any remaining buffer"""
        self.original_stdout.flush()


async def execute_workflow_with_streaming(
    request: WorkflowRequest,
    event_capture: WorkflowEventCapture
):
    """Execute workflow and capture events in real-time"""
    
    try:
        # Emit start event
        await event_capture.emit_event("workflow_start", {
            "agent": "SYSTEM",
            "message": f"Starting workflow: {request.request_type} for client {request.client_id}"
        })
        
        # Create initial state
        initial_state: WorkflowState = {
            "request": {
                "type": request.request_type,
                "client_id": request.client_id,
                "client_name": request.client_name or "Unknown Client",
                "initiator": request.initiator
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
        
        # Emit orchestrator start
        await event_capture.emit_event("agent_message", {
            "agent": "ORCHESTRATOR",
            "message": "Initializing workflow orchestrator..."
        })
        
        # Get current event loop for real-time capture
        loop = asyncio.get_event_loop()
        
        # Create real-time stdout capture
        realtime_capture = RealTimeStdoutCapture(event_capture, loop)
        
        # Execute workflow with real-time output capture
        with contextlib.redirect_stdout(realtime_capture):
            try:
                final_state = await asyncio.wait_for(
                    asyncio.to_thread(workflow_app.invoke, initial_state),
                    timeout=120.0  # 2 minute timeout
                )
            except asyncio.TimeoutError:
                await event_capture.emit_event("error", {
                    "agent": "SYSTEM",
                    "message": "Workflow execution timed out after 2 minutes"
                })
                raise HTTPException(status_code=408, detail="Workflow execution timeout")
        
        # Emit task updates from final state
        if final_state.get("tasks"):
            for task in final_state["tasks"]:
                await event_capture.emit_event("task_update", {
                    "agent": task.get("owner", "SYSTEM"),
                    "message": f"Task: {task.get('description')}",
                    "task_id": task.get("id"),
                    "description": task.get("description"),
                    "status": task.get("status"),
                    "owner": task.get("owner"),
                    "result": task.get("result")
                })
        
        # Emit completion event
        await event_capture.emit_event("workflow_complete", {
            "agent": "SYSTEM",
            "message": f"Workflow completed successfully! {len([t for t in final_state.get('tasks', []) if t.get('status') == 'completed'])}/{len(final_state.get('tasks', []))} tasks completed",
            "status": final_state.get("status", "completed"),
            "workflow_id": final_state.get("workflow_id"),
            "outcome": final_state.get("outcome"),
            "tasks_completed": len([t for t in final_state.get("tasks", []) if t.get("status") == "completed"]),
            "total_tasks": len(final_state.get("tasks", [])),
            "messages_count": len(final_state.get("messages", [])),
            "decisions_count": len(final_state.get("decisions", []))
        })
        
    except Exception as e:
        # Emit error event with details
        import traceback
        error_details = traceback.format_exc()
        print(f"Workflow error: {error_details}")  # Log to backend
        
        await event_capture.emit_event("error", {
            "agent": "SYSTEM",
            "message": f"Error: {str(e)}",
            "error_type": type(e).__name__,
            "details": error_details[:200]  # First 200 chars of traceback
        })
        raise


@router.get("/stream")
async def stream_workflow_execution(
    request_type: str,
    client_id: str,
    client_name: Optional[str] = None,
    initiator: Optional[str] = "system"
):
    """
    Stream workflow execution events via Server-Sent Events (SSE)
    
    Usage from frontend:
    const eventSource = new EventSource('/api/workflow/stream?request_type=open_roth_ira&client_id=john_smith_123')
    eventSource.onmessage = (event) => console.log(JSON.parse(event.data))
    """
    
    # Create event capture
    event_capture = WorkflowEventCapture()
    
    # Create request
    request = WorkflowRequest(
        request_type=request_type,
        client_id=client_id,
        client_name=client_name,
        initiator=initiator
    )
    
    async def event_generator():
        """Generate SSE events"""
        
        # Start workflow execution in background
        workflow_task = asyncio.create_task(
            execute_workflow_with_streaming(request, event_capture)
        )
        
        try:
            while not workflow_task.done():
                try:
                    # Get event from queue with timeout
                    event = await asyncio.wait_for(
                        event_capture.event_queue.get(),
                        timeout=0.5
                    )
                    
                    # Yield SSE formatted event
                    yield {
                        "event": event["type"],
                        "data": json.dumps(event["data"]),
                        "id": event["timestamp"]
                    }
                    
                    # Check if workflow is complete
                    if event["type"] == "workflow_complete" or event["type"] == "error":
                        break
                        
                except asyncio.TimeoutError:
                    # No events yet, continue waiting
                    continue
            
            # Drain any remaining events from queue
            while not event_capture.event_queue.empty():
                try:
                    event = await asyncio.wait_for(
                        event_capture.event_queue.get(),
                        timeout=0.1
                    )
                    yield {
                        "event": event["type"],
                        "data": json.dumps(event["data"]),
                        "id": event["timestamp"]
                    }
                except asyncio.TimeoutError:
                    break
                    
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Event generator error: {error_trace}")
            
            yield {
                "event": "error",
                "data": json.dumps({
                    "agent": "SYSTEM",
                    "message": f"Event stream error: {str(e)}"
                }),
                "id": datetime.now().isoformat()
            }
    
    return EventSourceResponse(event_generator())


@router.post("/execute")
async def execute_workflow(request: WorkflowRequest):
    """
    Execute workflow without streaming (traditional REST)
    Returns final result after completion
    """
    
    try:
        initial_state: WorkflowState = {
            "request": {
                "type": request.request_type,
                "client_id": request.client_id,
                "client_name": request.client_name or "Unknown Client",
                "initiator": request.initiator
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
        
        # Execute workflow (blocking)
        final_state = workflow_app.invoke(initial_state)
        
        return {
            "success": True,
            "workflow_id": final_state.get("workflow_id"),
            "status": final_state.get("status"),
            "outcome": final_state.get("outcome"),
            "tasks": final_state.get("tasks"),
            "summary": {
                "tasks_completed": len([t for t in final_state.get("tasks", []) if t.get("status") == "completed"]),
                "total_tasks": len(final_state.get("tasks", [])),
                "messages_count": len(final_state.get("messages", [])),
                "decisions_count": len(final_state.get("decisions", []))
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@router.get("/scenarios")
async def get_workflow_scenarios():
    """Get available workflow scenarios"""
    return {
        "scenarios": [
            {
                "id": "open_roth_ira",
                "name": "Open Roth IRA",
                "description": "Open a new Roth IRA account for a client",
                "estimated_duration": "30-45 minutes",
                "agents_involved": ["Orchestrator", "Operations", "Advisor"]
            },
            {
                "id": "open_traditional_ira",
                "name": "Open Traditional IRA",
                "description": "Open a new Traditional IRA account",
                "estimated_duration": "30-45 minutes",
                "agents_involved": ["Orchestrator", "Operations", "Advisor"]
            },
            {
                "id": "account_rollover",
                "name": "401k Rollover",
                "description": "Rollover 401k to IRA",
                "estimated_duration": "45-60 minutes",
                "agents_involved": ["Orchestrator", "Operations", "Advisor"]
            }
        ]
    }


@router.get("/accounts-log")
async def get_accounts_log():
    """Download CSV log of all created accounts"""
    account_system = get_account_system()
    csv_path = account_system.get_csv_log_path()
    
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="No accounts log found")
    
    return FileResponse(
        path=csv_path,
        media_type='text/csv',
        filename='nexhelm_accounts_log.csv'
    )


@router.get("/accounts")
async def get_all_accounts():
    """Get all created accounts as JSON"""
    account_system = get_account_system()
    accounts = account_system.get_all_accounts()
    
    return {
        "total_accounts": len(accounts),
        "accounts": accounts
    }

