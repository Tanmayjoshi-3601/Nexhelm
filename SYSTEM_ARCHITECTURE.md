# Nexhelm System Architecture & Flow

## 🏗️ System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                NEXHELM SYSTEM                                  │
│                    Real-time Financial Advisor Opportunity Detection            │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    WebSocket     ┌─────────────────┐    Redis     ┌─────────────────┐
│   REACT FRONTEND │ ◄──────────────► │  FASTAPI BACKEND │ ◄──────────► │   REDIS SERVER  │
│   (Port 3000)   │                  │   (Port 8002)   │              │   (Port 6379)   │
└─────────────────┘                  └─────────────────┘              └─────────────────┘
         │                                    │                                │
         │                                    │                                │
         ▼                                    ▼                                ▼
┌─────────────────┐                  ┌─────────────────┐              ┌─────────────────┐
│  User Interface │                  │  Opportunity    │              │  Data Storage   │
│  - Meeting UI   │                  │  Detection      │              │  - Conversations│
│  - Demo Controls│                  │  - LLM Analysis │              │  - Opportunities│
│  - Real-time    │                  │  - Pattern Match│              │  - Meeting Data │
│    Updates      │                  │  - Scoring      │              │  - TTL: 1 hour  │
└─────────────────┘                  └─────────────────┘              └─────────────────┘
         │                                    │
         │                                    │
         ▼                                    ▼
┌─────────────────┐                  ┌─────────────────┐
│  Demo System    │                  │  OpenAI API     │
│  - Scenarios    │                  │  - GPT-3.5-turbo│
│  - Auto Messages│                  │  - Opportunity  │
│  - Timing       │                  │    Detection    │
└─────────────────┘                  └─────────────────┘
```

## 🔄 System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SYSTEM FLOW                                       │
└─────────────────────────────────────────────────────────────────────────────────┘

1. USER INITIATION
   ┌─────────────┐
   │ User opens  │
   │ Frontend    │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │ Create      │
   │ Meeting     │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │ WebSocket   │
   │ Connection  │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │ Demo Mode   │
   │ Selection   │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │ Start Demo  │
   └──────┬──────┘
          │
          ▼
   ┌─────────────────────────────────────────────────────────────────────────────┐
   │                           DEMO EXECUTION FLOW                              │
   └─────────────────────────────────────────────────────────────────────────────┘
   
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │ Send Demo   │───►│ Store in    │───►│ AI Analysis │───►│ Detect      │
   │ Message     │    │ Redis       │    │ (LLM)       │    │ Opportunities│
   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
          │                  │                  │                  │
          │                  ▼                  │                  ▼
          │         ┌─────────────┐             │         ┌─────────────┐
          │         │ Conversation│             │         │ Score &     │
          │         │ History     │             │         │ Rank        │
          │         └─────────────┘             │         └──────┬──────┘
          │                                    │                  │
          │                                    ▼                  ▼
          │                           ┌─────────────┐    ┌─────────────┐
          │                           │ Context     │    │ Store in    │
          │                           │ Building    │    │ Redis       │
          │                           └─────────────┘    └──────┬──────┘
          │                                                    │
          │                                                    ▼
          │                                           ┌─────────────┐
          │                                           │ Broadcast   │
          │                                           │ to Frontend │
          │                                           └──────┬──────┘
          │                                                  │
          │                                                  ▼
          │                                           ┌─────────────┐
          │                                           │ Real-time   │
          │                                           │ UI Updates  │
          │                                           └─────────────┘
          │
          ▼
   ┌─────────────┐
   │ Wait Delay  │
   │ (2-5 sec)   │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │ Next        │
   │ Message?    │
   └──────┬──────┘
          │
          ├─ YES ──► Back to Send Demo Message
          │
          └─ NO ──► Demo Complete
```

## 🎭 Demo Functionality Deep Dive

### Demo System Components

1. **Dummy Transcript Service** (`dummy_transcript.py`)
2. **Demo API Endpoints** (`main.py`)
3. **Frontend Demo Controls** (`App.tsx`)

### Demo Scenarios Available

1. **Retirement Planning** (90 seconds)
   - Client turning 60, concerned about 401k sufficiency
   - Opportunities: Retirement planning, IRA rollover, catch-up contributions

2. **Education Planning** (75 seconds)
   - Daughter accepted to Northwestern University
   - Opportunities: 529 plans, education funding, tax benefits

3. **Life Changes** (80 seconds)
   - Expecting first child, promotion at work
   - Opportunities: Life insurance, estate planning, income protection

### Demo Flow Step-by-Step

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DEMO EXECUTION DETAILS                               │
└─────────────────────────────────────────────────────────────────────────────────┘

1. USER ACTIONS
   ┌─────────────┐
   │ User clicks │
   │ "Start Demo"│
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │ Frontend    │
   │ sends POST  │
   │ /api/demo/  │
   │ start/{id}  │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │ Backend     │
   │ creates     │
   │ async task  │
   └──────┬──────┘
          │
          ▼
   ┌─────────────────────────────────────────────────────────────────────────────┐
   │                        ASYNC DEMO TASK EXECUTION                           │
   └─────────────────────────────────────────────────────────────────────────────┘
   
   FOR EACH MESSAGE IN SCENARIO:
   
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │ Send        │───►│ Store       │───►│ AI          │───►│ Detect      │
   │ Message     │    │ Message     │    │ Analysis    │    │ Opportunities│
   │ via WS      │    │ in Redis    │    │ (LLM)       │    │             │
   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
          │                  │                  │                  │
          │                  ▼                  │                  ▼
          │         ┌─────────────┐             │         ┌─────────────┐
          │         │ Conversation│             │         │ Score &     │
          │         │ List        │             │         │ Store       │
          │         └─────────────┘             │         └──────┬──────┘
          │                                    │                  │
          │                                    ▼                  ▼
          │                           ┌─────────────┐    ┌─────────────┐
          │                           │ Build       │    │ Broadcast   │
          │                           │ Context     │    │ to Frontend │
          │                           │ (Last 5     │    │ via WS      │
          │                           │ messages)   │    └─────────────┘
          │                           └─────────────┘
          │
          ▼
   ┌─────────────┐
   │ Wait Delay  │
   │ (2-5 sec)   │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │ Next        │
   │ Message?    │
   └──────┬──────┘
          │
          ├─ YES ──► Continue Loop
          │
          └─ NO ──► Demo Complete
```

## 🔧 Technical Implementation Details

### 1. Demo Service Architecture

```python
class DummyTranscriptService:
    def __init__(self):
        self.active_demos: Dict[str, asyncio.Task] = {}
        self.scenarios = {
            "retirement_planning": {
                "name": "Retirement Planning",
                "duration": 90,
                "messages": [
                    {"speaker": "Client", "text": "...", "delay": 3},
                    {"speaker": "Advisor", "text": "...", "delay": 4},
                    # ... more messages
                ]
            }
        }
```

### 2. Opportunity Detection Integration

```python
async def opportunity_callback(text: str, speaker: str):
    # 1. Store message in Redis
    message = f"{speaker}: {text}"
    redis_client.add_message(meeting_id, message)
    
    # 2. Get recent context
    recent_messages = redis_client.get_conversation(meeting_id, last_n=5)
    context = "\n".join(recent_messages)
    
    # 3. AI analysis
    opportunities = detector.detect_opportunities(
        transcript=context,
        client_profile=client_profile,
        use_llm=True
    )
    
    # 4. Store and broadcast
    for opportunity in opportunities:
        redis_client.add_opportunity(meeting_id, opportunity, score)
        await manager.send_to_meeting(meeting_id, {
            "type": "opportunity",
            "opportunity": opportunity,
            "score": score
        })
```

### 3. Frontend Demo Controls

```typescript
// Demo state management
const [isDemoMode, setIsDemoMode] = useState(false);
const [demoScenarios, setDemoScenarios] = useState({});
const [selectedScenario, setSelectedScenario] = useState('');

// Start demo
const startDemo = async () => {
    const response = await axios.post(
        `${BACKEND_URL}/api/demo/start/${meetingId}?scenario=${selectedScenario}`
    );
    if (response.data.status === 'Demo started') {
        setIsDemoMode(true);
        toast.success(`Demo started: ${demoScenarios[selectedScenario]?.name}`);
    }
};
```

## 🎯 Key Features of Demo System

### 1. **Realistic Conversations**
- Pre-written scenarios based on real financial advisor conversations
- Natural timing with 2-5 second delays between messages
- Realistic client concerns and advisor responses

### 2. **Live Opportunity Detection**
- Each demo message triggers the same AI analysis as real messages
- Opportunities are detected, scored, and ranked in real-time
- High-priority opportunities (score ≥ 85) trigger toast notifications

### 3. **Complete Data Flow**
- Messages stored in Redis with 1-hour TTL
- Opportunities stored in Redis sorted set
- Real-time WebSocket updates to frontend
- Full conversation history preserved

### 4. **Demo Management**
- Start/stop controls
- Multiple scenario options
- Status monitoring
- Automatic cleanup on completion

## 🚀 How to Use Demo System

1. **Start the application** (Redis, Backend, Frontend)
2. **Create a meeting** in the frontend
3. **Select a demo scenario** from the dropdown
4. **Click "Start Demo"** to begin automatic conversation
5. **Watch opportunities appear** in real-time
6. **Monitor Redis** to see data being stored
7. **Stop demo** anytime or let it complete naturally

The demo system provides a complete end-to-end demonstration of the Nexhelm opportunity detection system without requiring manual conversation input.
