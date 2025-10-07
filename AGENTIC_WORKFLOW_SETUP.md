# 🚀 Agentic Workflow System - Setup Guide

## ✅ What's Been Added

### Backend
- ✅ **SSE Streaming Endpoint** (`/api/workflow/stream`) - Real-time event streaming
- ✅ **Workflow Execution API** - Execute workflows with live updates
- ✅ **Event Capture System** - Captures all agent communications, LLM calls, tool executions
- ✅ **Integrated with FastAPI** - No interference with existing opportunity detection

### Frontend  
- ✅ **Separate Workflow Page** - `/workflow` route (completely isolated)
- ✅ **Navigation System** - Switch between Opportunity Detection and Agentic Workflow
- ✅ **Real-time Event Stream** - Beautiful UI showing live agent communication
- ✅ **Task Progress Tracker** - Visual task completion status
- ✅ **SSE Client** - EventSource for streaming updates

---

## 📦 Installation Steps

### 1. Install Backend Dependencies

```bash
# Activate conda environment
conda activate nexhelm

# Navigate to backend
cd /Volumes/Personal/Northeastern/nex/Nexhelm/backend

# Install new package (sse-starlette for Server-Sent Events)
pip install sse-starlette==1.6.5
```

### 2. Install Frontend Dependencies

```bash
# Navigate to frontend
cd /Volumes/Personal/Northeastern/nex/Nexhelm/frontend

# Install react-router-dom for routing
npm install react-router-dom@^6.22.0
```

---

## 🎯 How to Run

### Terminal 1: Redis Server
```bash
redis-server
```

### Terminal 2: Backend Server
```bash
conda activate nexhelm
cd /Volumes/Personal/Northeastern/nex/Nexhelm/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### Terminal 3: Frontend Server
```bash
cd /Volumes/Personal/Northeastern/nex/Nexhelm/frontend
npm start
```

---

## 🌐 Access the Application

### Main Application
- **URL**: http://localhost:3000
- **Navigation**: 
  - `/` - Opportunity Detection System (original)
  - `/workflow` - Agentic Workflow System (new)

### Backend API
- **Docs**: http://localhost:8002/docs
- **SSE Stream**: http://localhost:8002/api/workflow/stream
- **Scenarios**: http://localhost:8002/api/workflow/scenarios

---

## 🎨 Features

### Agentic Workflow Page (`/workflow`)

1. **Workflow Configuration**
   - Select scenario (Open Roth IRA, Traditional IRA, 401k Rollover)
   - Enter client ID
   - Start/Stop workflow execution

2. **Task Progress Panel**
   - Real-time task status (pending → in_progress → completed)
   - Visual progress indicators
   - Task ownership (Orchestrator, Advisor, Operations)
   - Task results display

3. **Live Event Stream**
   - 🤖 Agent messages
   - 🔗 LLM API calls
   - 🔧 Tool executions
   - 🔄 Routing decisions
   - ✅ Success events
   - 📧 Notifications
   - Real-time timestamps

4. **Progress Bar**
   - Visual workflow completion percentage
   - Automatic updates based on task completion

---

## 🔧 API Endpoints

### Workflow Scenarios
```bash
GET /api/workflow/scenarios
```

### Stream Workflow Execution (SSE)
```bash
GET /api/workflow/stream?request_type=open_roth_ira&client_id=john_smith_123
```

### Execute Workflow (REST)
```bash
POST /api/workflow/execute
{
  "request_type": "open_roth_ira",
  "client_id": "john_smith_123",
  "client_name": "John Smith",
  "initiator": "web_ui"
}
```

---

## 🎯 Testing the System

### Quick Test

1. **Open Browser**: http://localhost:3000
2. **Navigate to Workflow**: Click "Agentic Workflow" in top navigation
3. **Configure**:
   - Scenario: "Open Roth IRA"
   - Client ID: "john_smith_123"
4. **Click "Start Workflow"**
5. **Watch**: Real-time agent communication, task execution, and completion

### Expected Output

You should see:
- 🚀 Workflow started
- 🤖 Orchestrator creating plan
- 🔗 LLM API calls
- ⚙️ Operations agent checking eligibility
- 👔 Advisor agent sending forms
- ✅ Tasks completing
- 🎉 Workflow completed

---

## 🔍 Architecture

### Backend Flow
```
User clicks "Start Workflow" 
    ↓
POST /api/workflow/stream
    ↓
Execute LangGraph workflow
    ↓
Capture console output & events
    ↓
Stream via SSE to frontend
    ↓
Frontend displays in real-time
```

### Frontend Flow
```
EventSource connection
    ↓
Listen for event types:
- workflow_start
- agent_message
- llm_call
- tool_execution
- routing
- task_update
- success
- notification
- workflow_complete
    ↓
Update UI in real-time
```

---

## 🚨 Troubleshooting

### Issue: SSE not streaming

**Solution**:
```bash
# Check if sse-starlette is installed
pip list | grep sse-starlette

# If not, install it
pip install sse-starlette==1.6.5
```

### Issue: React Router not working

**Solution**:
```bash
# Check if react-router-dom is installed
npm list react-router-dom

# If not, install it
npm install react-router-dom@^6.22.0
```

### Issue: CORS errors

**Solution**: The backend is already configured for CORS. Ensure backend is running on port 8002.

### Issue: Workflow not executing

**Solution**: 
1. Check that LangGraph workflow is working: `python -m app.workflow.main`
2. Ensure OpenAI API key is set in `.env`
3. Check backend console for errors

---

## 🎉 Success Indicators

✅ Navigation bar shows two tabs  
✅ Can switch between Opportunity Detection and Agentic Workflow  
✅ Workflow page loads without errors  
✅ Can select scenarios and start workflow  
✅ Events stream in real-time  
✅ Tasks update as they complete  
✅ No interference with opportunity detection system  

---

## 📝 File Structure

```
backend/
├── app/
│   ├── main.py                 # Updated: Added workflow router
│   ├── workflow_api.py         # NEW: SSE streaming endpoints
│   └── workflow/               # Existing LangGraph system
│       ├── graph.py
│       ├── state.py
│       └── agents/
└── requirements.txt            # Updated: Added sse-starlette

frontend/
├── src/
│   ├── App.tsx                 # NEW: Router with navigation
│   ├── pages/
│   │   ├── OpportunityDetectionPage.tsx  # Renamed from App.tsx
│   │   └── WorkflowPage.tsx              # NEW: Agentic workflow UI
└── package.json                # Updated: Added react-router-dom
```

---

## 🎨 UI Preview

### Navigation Bar
```
┌─────────────────────────────────────────────────────────┐
│ 🏠 Nexhelm AI    [Opportunity Detection]  [Agentic Workflow]  │
└─────────────────────────────────────────────────────────┘
```

### Workflow Page Layout
```
┌─────────────────────────────────────────────────────────┐
│  🧠 Agentic Workflow System                        ⚪ Idle  │
├─────────────────────────────────────────────────────────┤
│  Scenario: [Open Roth IRA ▼]  Client: [john_smith_123]  │
│  [Start Workflow ▶]                                     │
│  Progress: ████████░░░░░░░░░ 60%                        │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌────────────────────────────────┐  │
│  │   TASKS      │  │   LIVE EVENT STREAM            │  │
│  │              │  │                                │  │
│  │ ✅ Task 1    │  │ 🤖 Orchestrator: Creating...  │  │
│  │ ⏳ Task 2    │  │ 🔗 LLM Call: GPT-3.5 response │  │
│  │ ⚪ Task 3    │  │ 🔧 Tool: check_eligibility     │  │
│  │ ⚪ Task 4    │  │ ✅ Success: Eligible!          │  │
│  └──────────────┘  └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Next Steps

The system is now ready to use! You have:
- ✅ Complete separation of concerns
- ✅ Real-time streaming workflow execution
- ✅ Beautiful UI with agent visualization
- ✅ No interference with existing opportunity detection

Enjoy your multi-agent AI system! 🎉

