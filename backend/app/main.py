from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import json
import uuid
from datetime import datetime

# Import opportunity detector with fallback
try:
    from .opportunity_detector import OpportunityDetector
except ImportError:
    from opportunity_detector import OpportunityDetector

# Import from the same directory
try:
    from .redis_client import redis_client
    from .dummy_transcript import dummy_transcript_service
    from .workflow_api import router as workflow_router
except ImportError:
    try:
        # Fallback for direct execution
        from redis_client import redis_client
        from dummy_transcript import dummy_transcript_service
        from workflow_api import router as workflow_router
    except ImportError:
        # Final fallback with app prefix
        from app.redis_client import redis_client
        from app.dummy_transcript import dummy_transcript_service
        from app.workflow_api import router as workflow_router

app = FastAPI(title="Nexhelm POC")
detector = OpportunityDetector()

# Include workflow router for agentic workflows
app.include_router(workflow_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, meeting_id: str):
        await websocket.accept()
        
        if meeting_id not in self.active_connections:
            self.active_connections[meeting_id] = []
        
        self.active_connections[meeting_id].append(websocket)
        
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to meeting",
            "meeting_id": meeting_id
        })
        
        print(f"Client connected to meeting {meeting_id}")
    
    def disconnect(self, websocket: WebSocket, meeting_id: str):
        if meeting_id in self.active_connections:
            self.active_connections[meeting_id].remove(websocket)
            if not self.active_connections[meeting_id]:
                del self.active_connections[meeting_id]
        print(f"Client disconnected from meeting {meeting_id}")
    
    async def send_to_meeting(self, meeting_id: str, message: dict):
        if meeting_id in self.active_connections:
            for connection in self.active_connections[meeting_id]:
                await connection.send_json(message)

manager = ConnectionManager()

# Serve the HTML test client
@app.get("/test", response_class=HTMLResponse)
async def test_page():
    """Serve test client HTML"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nexhelm WebSocket Test</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 50px auto; }
            #messages { border: 1px solid #ccc; height: 300px; overflow-y: scroll; padding: 10px; margin: 20px 0; }
            .message { margin: 5px 0; padding: 5px; background: #f0f0f0; }
            .opportunity { background: #ffffcc; border-left: 4px solid orange; padding: 10px; margin: 10px 0; }
            button { padding: 10px 20px; margin: 5px; cursor: pointer; }
            input { padding: 10px; width: 300px; }
            .status { padding: 10px; background: #e0f0e0; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>Nexhelm POC - WebSocket Test</h1>
        
        <div class="status" id="status">Status: Not connected</div>
        
        <div>
            <button onclick="createMeeting()">1. Create Meeting</button>
            <button onclick="connect()">2. Connect to Meeting</button>
            <button onclick="disconnect()">3. Disconnect</button>
        </div>
        
        <div>
            <input type="text" id="messageInput" placeholder="Type a message (try 'retirement')..." />
            <button onclick="sendMessage()">Send</button>
        </div>
        
        <div id="messages"></div>
        
        <script>
            let ws = null;
            let meetingId = null;
            
            async function createMeeting() {
                try {
                    const response = await fetch('/api/meeting/create', {
                        method: 'POST'
                    });
                    const data = await response.json();
                    meetingId = data.meeting_id;
                    
                    document.getElementById('status').innerHTML = 
                        `Status: Meeting created - ID: ${meetingId}`;
                    document.getElementById('messages').innerHTML += 
                        `<div class="message">✓ Meeting created: ${meetingId}</div>`;
                } catch (error) {
                    alert('Error creating meeting: ' + error);
                }
            }
            
            function connect() {
                if (!meetingId) {
                    alert('Create a meeting first!');
                    return;
                }
                
                ws = new WebSocket(`ws://localhost:8001/ws/${meetingId}`);
                
                ws.onopen = () => {
                    document.getElementById('status').innerHTML = 
                        `Status: Connected to meeting ${meetingId}`;
                    console.log('Connected');
                };
                
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    const messagesDiv = document.getElementById('messages');
                    
                    if (data.type === 'opportunity') {
                        messagesDiv.innerHTML += 
                            `<div class="opportunity">
                                <strong>🎯 Opportunity Detected!</strong><br>
                                ${data.opportunity.title}<br>
                                Score: ${data.score}
                            </div>`;
                    } else if (data.type === 'message') {
                        messagesDiv.innerHTML += 
                            `<div class="message">${data.speaker}: ${data.text}</div>`;
                    } else if (data.type === 'history') {
                        messagesDiv.innerHTML += 
                            `<div class="message">📜 Loaded ${data.messages.length} historical messages</div>`;
                    }
                    
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                };
                
                ws.onclose = () => {
                    document.getElementById('status').innerHTML = 'Status: Disconnected';
                    console.log('Disconnected');
                };
                
                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    alert('WebSocket error - check console');
                };
            }
            
            function sendMessage() {
                const input = document.getElementById('messageInput');
                if (ws && ws.readyState === WebSocket.OPEN && input.value) {
                    ws.send(JSON.stringify({
                        speaker: 'Client',
                        text: input.value
                    }));
                    input.value = '';
                } else if (!ws || ws.readyState !== WebSocket.OPEN) {
                    alert('Not connected! Click Connect first.');
                }
            }
            
            function disconnect() {
                if (ws) {
                    ws.close();
                }
            }
            
            // Send on Enter key
            document.getElementById('messageInput').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/")
def read_root():
    return {"message": "Nexhelm POC Server Running!", "test_url": "http://localhost:8001/test", "status": "Redis connected and ready"}

@app.post("/api/meeting/create")
async def create_meeting(client_id: str = "demo-client"):
    """Create a new meeting session"""
    meeting_id = str(uuid.uuid4())
    
    # Create meeting in Redis
    meeting_data = redis_client.create_meeting(meeting_id, client_id)
    
    return {
        "meeting_id": meeting_id,
        "client_id": client_id,
        "status": "created"
    }

@app.get("/api/meeting/{meeting_id}/history")
async def get_meeting_history(meeting_id: str):
    """Get conversation history for a meeting"""
    conversation = redis_client.get_conversation(meeting_id)
    opportunities = redis_client.get_top_opportunities(meeting_id)
    
    return {
        "meeting_id": meeting_id,
        "conversation": conversation,
        "opportunities": opportunities
    }

@app.get("/api/demo/scenarios")
async def get_demo_scenarios():
    """Get available demo scenarios"""
    return dummy_transcript_service.get_available_scenarios()

@app.post("/api/demo/start/{meeting_id}")
async def start_demo(meeting_id: str, scenario: str):
    """Start a demo conversation"""
    try:
        # Check if demo is already running
        if dummy_transcript_service.is_demo_running(meeting_id):
            return {"error": "Demo already running for this meeting"}
        
        # Create opportunity detection callback
        async def opportunity_callback(text: str, speaker: str):
            # Store message in Redis (same as normal flow)
            message = f"{speaker}: {text}"
            redis_client.add_message(meeting_id, message)
            
            # Get recent messages for context
            recent_messages = redis_client.get_conversation(meeting_id, last_n=5)
            context = "\n".join(recent_messages)
            
            # Mock client profile
            client_profile = {
                'age': 58,
                'income': 150000,
                'family_status': 'married_with_children',
                'products': ['401k', 'term_life']
            }
            
            # Run opportunity detection
            opportunities = detector.detect_opportunities(
                transcript=context,
                client_profile=client_profile,
                use_llm=True
            )
            
            # Process and send opportunities
            for opportunity in opportunities:
                # Store in Redis
                redis_client.add_opportunity(
                    meeting_id,
                    opportunity,
                    opportunity.get('score', 50)
                )
                
                # Broadcast to clients
                await manager.send_to_meeting(meeting_id, {
                    "type": "opportunity",
                    "opportunity": opportunity,
                    "score": opportunity.get('score', 50),
                    "detected_by": opportunity.get('detected_by', 'unknown')
                })
        
        # Start the demo with opportunity detection
        await dummy_transcript_service.start_demo(
            meeting_id, 
            scenario, 
            lambda msg: manager.send_to_meeting(meeting_id, msg),
            opportunity_callback
        )
        
        return {"status": "Demo started", "scenario": scenario}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to start demo: {str(e)}"}

@app.post("/api/demo/stop/{meeting_id}")
async def stop_demo(meeting_id: str):
    """Stop a running demo"""
    try:
        await dummy_transcript_service.stop_demo(meeting_id)
        return {"status": "Demo stopped"}
    except Exception as e:
        return {"error": f"Failed to stop demo: {str(e)}"}

@app.get("/api/demo/status/{meeting_id}")
async def get_demo_status(meeting_id: str):
    """Get demo status for a meeting"""
    is_running = dummy_transcript_service.is_demo_running(meeting_id)
    return {"meeting_id": meeting_id, "demo_running": is_running}

@app.websocket("/ws/{meeting_id}")
async def websocket_endpoint(websocket: WebSocket, meeting_id: str):
    """WebSocket endpoint for real-time meeting communication with intelligent opportunity detection added"""
    
    await manager.connect(websocket, meeting_id)
    
    # Send existing conversation history
    history = redis_client.get_conversation(meeting_id, last_n=10)
    await websocket.send_json({
        "type": "history",
        "messages": history
    })

    # mock client profile -> should come from CRM 
    client_profile = {
        'age': 58,
        'income': 150000,
        'family_status': 'married_with_children',
        'products': ['401k', 'term_life']
    }
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Store in Redis
            message = f"{data.get('speaker', 'Unknown')}: {data.get('text', '')}"
            redis_client.add_message(meeting_id, message)
            
            # Echo to all in meeting
            await manager.send_to_meeting(meeting_id, {
                "type": "message",
                "speaker": data.get('speaker'),
                "text": data.get('text'),
                "timestamp": datetime.now().isoformat()
            })
            
            # intelligent opportunity detection
            # get recent messages -> recent 5 messages
            recent_messages = redis_client.get_conversation(meeting_id, last_n = 5)
            context = "\n".join(recent_messages)

            # opportunity detection
            opportunities = detector.detect_opportunities(
                transcript=context,
                client_profile=client_profile,
                use_llm = True
            )
            for opportunity in opportunities:

                # store in Redis
                redis_client.add_opportunity(
                    meeting_id,
                    opportunity,
                    opportunity.get('score',50)
                )

                # broadcast to clients
                await manager.send_to_meeting(meeting_id,{
                     "type": "opportunity",
                    "opportunity": opportunity,
                    "score": opportunity.get('score', 50),
                    "detected_by": opportunity.get('detected_by', 'unknown')
                })


            # # Simple opportunity detection
            # text_lower = data.get('text', '').lower()
            # if "retirement" in text_lower:
            #     opportunity = {
            #         "type": "retirement_planning",
            #         "title": "Retirement Planning Opportunity",
            #         "description": "Client mentioned retirement - review 401k options"
            #     }
            #     redis_client.add_opportunity(meeting_id, opportunity, 85)
                
            #     await manager.send_to_meeting(meeting_id, {
            #         "type": "opportunity",
            #         "opportunity": opportunity,
            #         "score": 85
            #     })
            # elif "college" in text_lower or "daughter" in text_lower:
            #     opportunity = {
            #         "type": "education_planning",
            #         "title": "529 Education Savings Plan",
            #         "description": "Client mentioned college - discuss education savings"
            #     }
            #     redis_client.add_opportunity(meeting_id, opportunity, 75)
                
            #     await manager.send_to_meeting(meeting_id, {
            #         "type": "opportunity",
            #         "opportunity": opportunity,
            #         "score": 75
            #     })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, meeting_id)

if __name__ == "__main__":
    print("Starting Nexhelm POC Server...")
    print("Test interface will be available at: http://localhost:8001/test")
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)