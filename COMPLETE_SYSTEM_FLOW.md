# Complete Nexhelm System Flow Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    NEXHELM SYSTEM                                              │
│                              Real-time Financial Advisor AI                                    │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React         │    │   FastAPI       │    │   Dummy         │    │   Opportunity   │    │   OpenAI        │
│   Frontend      │◄──►│   Backend       │◄──►│   Transcript    │◄──►│   Detector      │◄──►│   GPT-4         │
│   (TypeScript)  │    │   (Python)      │    │   Service       │    │   (3-Layer AI)  │    │   API           │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WebSocket     │    │   WebSocket     │    │   Async         │    │   Pattern       │    │   HTTP          │
│   Client        │    │   Manager       │    │   Message       │    │   Matching      │    │   Requests      │
│   (Browser)     │    │   (FastAPI)     │    │   Streaming     │    │   + Context     │    │   (API Calls)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │                       │
                                ▼                       ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                       │   Redis         │    │   React         │    │   Toast         │
                       │   Database      │    │   State         │    │   Notifications │
                       │   (Persistence) │    │   Management    │    │   (UI Feedback) │
                       └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Complete System Flow: From Start to Finish

### Phase 1: Application Startup & Initialization

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                PHASE 1: APPLICATION STARTUP                                    │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

1. BACKEND SERVER STARTUP
   ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
   │ python main.py                                                                              │
   │                                                                                             │
   │ • FastAPI server starts on port 8002                                                       │
   │ • Redis connection established                                                              │
   │ • OpportunityDetector initialized                                                          │
   │ • DummyTranscriptService loaded with scenarios                                             │
   │ • WebSocket manager ready                                                                   │
   │                                                                                             │
   │ ✅ Server running at http://localhost:8002                                                 │
   └─────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
2. FRONTEND APPLICATION STARTUP
   ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
   │ npm start (React Development Server)                                                       │
   │                                                                                             │
   │ • React app starts on port 3000                                                            │
   │ • App.tsx component mounts                                                                 │
   │ • State initialized:                                                                       │
   │   - meetingId: null                                                                        │
   │   - isConnected: false                                                                     │
   │   - messages: []                                                                           │
   │   - opportunities: []                                                                      │
   │   - isDemoMode: false                                                                      │
   │                                                                                             │
   │ ✅ Frontend running at http://localhost:3000                                               │
   └─────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
3. DEMO SCENARIOS LOADING
   ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
   │ useEffect(() => { loadDemoScenarios() })                                                   │
   │                                                                                             │
   │ GET /api/demo/scenarios                                                                    │
   │ ↓                                                                                           │
   │ FastAPI: return dummy_transcript_service.get_available_scenarios()                         │
   │ ↓                                                                                           │
   │ Response: {                                                                                 │
   │   "retirement_planning": {"name": "Retirement Planning", "duration": 90},                  │
   │   "education_planning": {"name": "Education Planning", "duration": 75},                    │
   │   "life_changes": {"name": "Life Changes & Planning", "duration": 80}                      │
   │ }                                                                                           │
   │ ↓                                                                                           │
   │ React: setDemoScenarios(response.data)                                                     │
   │       setSelectedScenario("retirement_planning")                                           │
   └─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Phase 2: Meeting Creation & Connection

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           PHASE 2: MEETING CREATION & CONNECTION                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

4. USER CLICKS "CREATE MEETING" BUTTON
   ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
   │ Frontend: createMeeting() function called                                                  │
   │                                                                                             │
   │ • Show loading toast: "Creating meeting..."                                                │
   │ • Make API call: POST /api/meeting/create                                                  │
   └─────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
5. BACKEND CREATES MEETING
   ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
   │ FastAPI: @app.post("/api/meeting/create")                                                  │
   │                                                                                             │
   │ • Generate UUID: meeting_id = "abc-123-def-456"                                            │
   │ • Create meeting in Redis:                                                                 │
   │   Key: "meeting:abc-123-def-456"                                                           │
   │   Value: {                                                                                 │
   │     "client_id": "demo-client",                                                            │
   │     "status": "active",                                                                    │
   │     "start_time": "1705312200"                                                             │
   │   }                                                                                        │
   │ • Return: {"meeting_id": "abc-123-def-456", "status": "created"}                          │
   └─────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
6. FRONTEND RECEIVES MEETING ID
   ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
   │ React: setMeetingId("abc-123-def-456")                                                     │
   │ • Update toast: "Meeting created!"                                                         │
   │ • Auto-connect after 500ms: connectToMeeting("abc-123-def-456")                           │
   └─────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
7. WEBSOCKET CONNECTION ESTABLISHED
   ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
   │ Frontend: new WebSocket("ws://localhost:8002/ws/abc-123-def-456")                         │
   │                                                                                             │
   │ • WebSocket connection opens                                                                │
   │ • onopen event: setIsConnected(true)                                                       │
   │ • Show toast: "Connected to meeting"                                                       │
   │                                                                                             │
   │ Backend: @app.websocket("/ws/{meeting_id}")                                                │
   │ • manager.connect(websocket, "abc-123-def-456")                                            │
   │ • Add to active_connections["abc-123-def-456"] = [websocket]                               │
   │ • Send connection confirmation                                                              │
   └─────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
8. CONVERSATION HISTORY LOADED
   ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
   │ Backend: Send existing conversation history                                                │
   │                                                                                             │
   │ • redis_client.get_conversation("abc-123-def-456", last_n=10)                             │
   │ • Send WebSocket message:                                                                  │
   │   {                                                                                        │
   │     "type": "history",                                                                     │
   │     "messages": []  // Empty for new meeting                                               │
   │   }                                                                                        │
   │                                                                                             │
   │ Frontend: onmessage handler                                                                │
   │ • Parse history message                                                                     │
   │ • setMessages([])  // Empty for new meeting                                                │
   └─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Phase 3: Demo Conversation Execution

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           PHASE 3: DEMO CONVERSATION EXECUTION                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

9. USER STARTS DEMO
   ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
   │ User clicks "Start Demo" button                                                             │
   │ • Frontend: startDemo() function called                                                    │
   │ • POST /api/demo/start/abc-123-def-456?scenario=retirement_planning                        │
   └─────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
10. BACKEND INITIATES DEMO
    ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
    │ FastAPI: @app.post("/api/demo/start/{meeting_id}")                                        │
    │                                                                                             │
    │ • Check if demo already running                                                            │
    │ • Create opportunity_callback function (captures meeting_id)                               │
    │ • Call dummy_transcript_service.start_demo(                                                │
    │     meeting_id="abc-123-def-456",                                                          │
    │     scenario="retirement_planning",                                                        │
    │     send_callback=lambda msg: manager.send_to_meeting(meeting_id, msg),                   │
    │     opportunity_callback=opportunity_callback                                              │
    │   )                                                                                        │
    │                                                                                             │
    │ • Return: {"status": "Demo started", "scenario": "retirement_planning"}                   │
    └─────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
11. DUMMY TRANSCRIPT SERVICE STARTS
    ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
    │ DummyTranscriptService.start_demo()                                                        │
    │                                                                                             │
    │ • Load scenario data for "retirement_planning"                                             │
    │ • Create asyncio task: run_demo()                                                          │
    │ • Add to active_demos["abc-123-def-456"] = task                                            │
    │                                                                                             │
    │ async def run_demo():                                                                      │
    │   for message in scenario_data["messages"]:  # 22 messages total                           │
    │     # Process each message...                                                              │
    └─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Phase 4: Message Streaming & Opportunity Detection

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 4: MESSAGE STREAMING & OPPORTUNITY DETECTION                          │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

12. FIRST MESSAGE STREAMING
    ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
    │ Message 1: "Client: Hi, thanks for meeting with me today."                                 │
    │                                                                                             │
    │ Dummy Service:                                                                              │
    │ • await send_callback({                                                                     │
    │     "type": "message",                                                                      │
    │     "speaker": "Client",                                                                    │
    │     "text": "Hi, thanks for meeting with me today.",                                       │
    │     "timestamp": "2024-01-15T10:30:00"                                                     │
    │   })                                                                                        │
    │                                                                                             │
    │ Backend WebSocket Manager:                                                                  │
    │ • manager.send_to_meeting("abc-123-def-456", message)                                      │
    │ • Broadcast to all connected clients                                                        │
    │                                                                                             │
    │ Frontend:                                                                                   │
    │ • WebSocket onmessage handler receives message                                             │
    │ • setMessages(prev => [...prev, newMessage])                                               │
    │ • UI updates to show new message                                                            │
    └─────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
13. OPPORTUNITY DETECTION TRIGGERED
    ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
    │ Dummy Service:                                                                              │
    │ • await opportunity_callback("Hi, thanks for meeting with me today.", "Client")            │
    │                                                                                             │
    │ Backend opportunity_callback:                                                               │
    │ • Store message in Redis:                                                                  │
    │   Key: "Conversation:abc-123-def-456"                                                      │
    │   Value: ["Client: Hi, thanks for meeting with me today."]                                 │
    │                                                                                             │
    │ • Get recent context: recent_messages = ["Client: Hi, thanks for meeting..."]              │
    │ • Mock client profile: {age: 58, income: 150000, ...}                                      │
    │                                                                                             │
    │ • Run opportunity detection:                                                                │
    │   detector.detect_opportunities(context, client_profile, use_llm=True)                     │
    │                                                                                             │
    │ • Layer 1 (Pattern): No keywords found                                                     │
    │ • Layer 2 (Context): No age/income triggers                                                │
    │ • Layer 3 (LLM): No opportunities detected                                                 │
    │                                                                                             │
    │ • No opportunities to broadcast                                                             │
    └─────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
14. SECOND MESSAGE WITH OPPORTUNITY
    ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
    │ Message 2: "Advisor: Of course! I'm excited to help you plan for retirement."              │
    │                                                                                             │
    │ • Message sent via WebSocket                                                               │
    │ • Frontend displays message                                                                │
    │                                                                                             │
    │ • opportunity_callback("Of course! I'm excited to help you plan for retirement.", "Advisor")│
    │                                                                                             │
    │ • Store in Redis: ["Advisor: Of course! I'm excited...", "Client: Hi, thanks..."]         │
    │                                                                                             │
    │ • Opportunity Detection:                                                                    │
    │   - Layer 1: Keyword "retirement" found!                                                   │
    │   - Create opportunity: {                                                                  │
    │       "type": "retirement_planning",                                                       │
    │       "title": "401(k) and Retirement Planning Review",                                    │
    │       "description": "Client may benefit from retirement account optimization",            │
    │       "score": 75,                                                                         │
    │       "detected_by": "pattern_matching",                                                   │
    │       "trigger": "Keyword: retirement"                                                     │
    │     }                                                                                      │
    │                                                                                             │
    │ • Store in Redis:                                                                          │
    │   Key: "opportunities:abc-123-def-456"                                                     │
    │   Value: Sorted Set with score 75                                                          │
    │                                                                                             │
    │ • Broadcast to clients:                                                                    │
    │   {                                                                                        │
    │     "type": "opportunity",                                                                 │
    │     "opportunity": {...},                                                                  │
    │     "score": 75,                                                                           │
    │     "detected_by": "pattern_matching"                                                      │
    │   }                                                                                        │
    └─────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
15. FRONTEND OPPORTUNITY PROCESSING
    ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
    │ Frontend WebSocket onmessage:                                                              │
    │                                                                                             │
    │ • Parse opportunity message                                                                │
    │ • Create newOpportunity object                                                             │
    │ • setOpportunities(prev => [...prev, newOpportunity])                                      │
    │ • Sort by score (highest first)                                                            │
    │ • Update UI to show opportunity card                                                       │
    │                                                                                             │
    │ • Check if high priority (score >= 85):                                                    │
    │   - Show toast notification: "High Priority: 401(k) and Retirement Planning Review"       │
    │                                                                                             │
    │ • Update total opportunity value:                                                          │
    │   setTotalOpportunityValue(prev => prev + (75 * 100)) = 7500                              │
    └─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Phase 5: Advanced Opportunity Detection

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 5: ADVANCED OPPORTUNITY DETECTION                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

16. THIRD MESSAGE WITH CONTEXTUAL DETECTION
    ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
    │ Message 3: "Client: Well, I'm turning 60 next year and starting to think seriously about   │
    │           retirement."                                                                      │
    │                                                                                             │
    │ • Message streamed and displayed                                                            │
    │                                                                                             │
    │ • Opportunity Detection (3 layers):                                                         │
    │                                                                                             │
    │   Layer 1 (Pattern Matching):                                                              │
    │   • Keywords: "retirement" (already detected)                                              │
    │   • Age mention: "turning 60"                                                              │
    │                                                                                             │
    │   Layer 2 (Contextual Analysis):                                                           │
    │   • Client age: 58 (from profile)                                                          │
    │   • Age 58 + "retirement" + "turning 60" = Early retirement interest                      │
    │   • Create opportunity: {                                                                  │
    │       "type": "early_retirement",                                                          │
    │       "title": "Early Retirement Planning",                                                │
    │       "description": "At age 58, client showing retirement interest",                     │
    │       "score": 88,                                                                         │
    │       "detected_by": "contextual_analysis",                                                │
    │       "trigger": "Age 58 + mentioned 'retirement'"                                         │
    │     }                                                                                      │
    │                                                                                             │
    │   • Age 58 >= 50 = Catch-up contributions eligible                                         │
    │   • Create opportunity: {                                                                  │
    │       "type": "catch_up_contributions",                                                    │
    │       "title": "Catch-Up Contribution Strategy",                                           │
    │       "description": "Age 58 qualifies for additional $7,500 401(k) contributions",       │
    │       "score": 82,                                                                         │
    │       "detected_by": "contextual_analysis",                                                │
    │       "trigger": "Age 58 + retirement discussion"                                          │
    │     }                                                                                      │
    │                                                                                             │
    │   Layer 3 (LLM Analysis):                                                                  │
    │   • Send to GPT-4: "Analyze this conversation for opportunities..."                        │
    │   • GPT-4 response: [                                                                      │
    │       {                                                                                    │
    │         "type": "retirement_planning",                                                     │
    │         "title": "Comprehensive Retirement Strategy",                                      │
    │         "description": "Client at 58 showing strong retirement interest",                 │
    │         "score": 92,                                                                       │
    │         "reasoning": "Client explicitly mentioned turning 60 and retirement planning"     │
    │       }                                                                                    │
    │     ]                                                                                      │
    │                                                                                             │
    │ • Deduplicate and sort by score:                                                           │
    │   1. "Comprehensive Retirement Strategy" (92) - LLM                                        │
    │   2. "Early Retirement Planning" (88) - Contextual                                         │
    │   3. "Catch-Up Contribution Strategy" (82) - Contextual                                    │
    │   4. "401(k) and Retirement Planning Review" (75) - Pattern                               │
    └─────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
17. MULTIPLE OPPORTUNITIES BROADCAST
    ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
    │ Backend: For each opportunity (sorted by score):                                           │
    │                                                                                             │
    │ • Store in Redis Sorted Set:                                                               │
    │   Key: "opportunities:abc-123-def-456"                                                     │
    │   Value: {                                                                                 │
    │     "Comprehensive Retirement Strategy": 92,                                               │
    │     "Early Retirement Planning": 88,                                                       │
    │     "Catch-Up Contribution Strategy": 82,                                                  │
    │     "401(k) and Retirement Planning Review": 75                                            │
    │   }                                                                                        │
    │                                                                                             │
    │ • Broadcast each opportunity via WebSocket                                                 │
    │                                                                                             │
    │ Frontend: For each opportunity received:                                                   │
    │                                                                                             │
    │ • Add to opportunities list                                                                │
    │ • Update UI with new opportunity cards                                                     │
    │ • Show high-priority toast for score >= 85:                                               │
    │   - "High Priority: Comprehensive Retirement Strategy" (92)                               │
    │   - "High Priority: Early Retirement Planning" (88)                                       │
    │                                                                                             │
    │ • Update total value: 7500 + (92*100) + (88*100) + (82*100) = 33,700                     │
    └─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Phase 6: Conversation Continues & Real-time Updates

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 6: CONVERSATION CONTINUES & REAL-TIME UPDATES                         │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

18. CONVERSATION FLOW CONTINUES
    ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
    │ Messages 4-22 continue streaming with 2-5 second delays:                                   │
    │                                                                                             │
    │ Message 4: "Advisor: That's a great milestone! What's your current retirement savings..."  │
    │ Message 5: "Client: I have about $800,000 in my 401k and another $150,000 in a traditional│
    │           IRA."                                                                             │
    │ Message 6: "Advisor: That's a solid foundation. Do you have any other assets..."           │
    │ ...                                                                                         │
    │ Message 22: "Advisor: I'm glad I could help! We'll create a comprehensive plan..."         │
    │                                                                                             │
    │ Each message:                                                                               │
    │ • Streamed via WebSocket                                                                    │
    │ • Stored in Redis                                                                           │
    │ • Triggers opportunity detection                                                            │
    │ • Updates frontend UI in real-time                                                          │
    └─────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
19. ADDITIONAL OPPORTUNITIES DETECTED
    ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
    │ As conversation progresses, more opportunities emerge:                                      │
    │                                                                                             │
    │ Message 5: "I have about $800,000 in my 401k..."                                           │
    │ • Opportunity: "401(k) Optimization Review" (78)                                           │
    │                                                                                             │
    │ Message 8: "We spend about $6,000 per month..."                                            │
    │ • Opportunity: "Budget Analysis and Optimization" (65)                                     │
    │                                                                                             │
    │ Message 12: "I'm also wondering about catch-up contributions..."                           │
    │ • Opportunity: "Catch-Up Contribution Implementation" (85)                                  │
    │                                                                                             │
    │ Message 15: "I'm also thinking about a Roth conversion..."                                 │
    │ • Opportunity: "Roth Conversion Strategy" (80)                                             │
    │                                                                                             │
    │ Message 18: "I'm also worried about healthcare costs..."                                   │
    │ • Opportunity: "Healthcare Cost Planning" (75)                                             │
    │                                                                                             │
    │ Message 20: "Should we look into long-term care insurance..."                              │
    │ • Opportunity: "Long-Term Care Insurance Review" (82)                                      │
    └─────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
20. FRONTEND REAL-TIME UPDATES
    ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
    │ Frontend continuously updates:                                                              │
    │                                                                                             │
    │ • Messages appear in conversation panel                                                    │
    │ • Opportunities populate in opportunities panel                                            │
    │ • Total opportunity value increases: 33,700 → 45,200 → 58,700 → ...                      │
    │ • High-priority toasts appear for scores >= 85                                            │
    │ • UI animations show new opportunities sliding in                                          │
    │ • Opportunity cards show detection method (pattern/context/LLM)                            │
    └─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Phase 7: Demo Completion & Cleanup

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           PHASE 7: DEMO COMPLETION & CLEANUP                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

21. DEMO CONVERSATION COMPLETES
    ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
    │ Dummy Service: All 22 messages sent                                                        │
    │                                                                                             │
    │ • Send completion message:                                                                 │
    │   {                                                                                        │
    │     "type": "demo_complete",                                                               │
    │     "message": "Demo conversation completed! Scenario: Retirement Planning"                │
    │   }                                                                                        │
    │                                                                                             │
    │ • Clean up: del self.active_demos["abc-123-def-456"]                                       │
    │                                                                                             │
    │ Frontend:                                                                                  │
    │ • Receive demo_complete message                                                            │
    │ • Show toast: "Demo completed!"                                                            │
    │ • setIsDemoMode(false)                                                                     │
    │ • Update UI to show demo is finished                                                       │
    └─────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
22. USER CAN CONTINUE OR START NEW DEMO
    ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
    │ User options:                                                                               │
    │                                                                                             │
    │ 1. Send manual messages via text input                                                      │
    │ 2. Start new demo with different scenario                                                   │
    │ 3. View meeting history                                                                     │
    │ 4. Disconnect from meeting                                                                  │
    │                                                                                             │
    │ All data remains in Redis for 1 hour (auto-cleanup)                                        │
    └─────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Summary

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    DATA FLOW SUMMARY                                           │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

1. USER INTERACTION
   Frontend UI → User clicks → React state update → API call/WebSocket message

2. BACKEND PROCESSING
   FastAPI endpoint → Business logic → Redis storage → WebSocket broadcast

3. OPPORTUNITY DETECTION
   Message received → 3-layer analysis → Opportunity objects → Redis storage → WebSocket broadcast

4. REAL-TIME UPDATES
   WebSocket message → Frontend state update → UI re-render → User sees changes

5. PERSISTENCE
   All data stored in Redis with 1-hour expiration for automatic cleanup

6. SCALABILITY
   Multiple clients can connect to same meeting and see real-time updates
   Multiple meetings can run simultaneously with isolated data
```

## Technology Stack Integration

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                TECHNOLOGY STACK                                                │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

FRONTEND (React + TypeScript):
• React hooks for state management
• WebSocket API for real-time communication
• Axios for HTTP requests
• Framer Motion for animations
• React Hot Toast for notifications
• Tailwind CSS for styling

BACKEND (FastAPI + Python):
• FastAPI for REST API and WebSocket endpoints
• Asyncio for concurrent message streaming
• Pydantic for data validation
• CORS middleware for cross-origin requests

DATA STORAGE (Redis):
• Lists for conversation history
• Sorted Sets for opportunity scoring
• Hashes for meeting metadata
• Automatic expiration for cleanup

AI/ML (OpenAI + Custom Logic):
• GPT-4 for intelligent conversation analysis
• Pattern matching for fast keyword detection
• Contextual analysis for age/income-based opportunities
• Multi-layer scoring system

REAL-TIME COMMUNICATION:
• WebSocket for bidirectional communication
• Connection management for multiple clients
• Message broadcasting to all meeting participants
```

This complete flow shows how the Nexhelm system creates a seamless, real-time financial advisor experience from initial startup through conversation completion, with intelligent opportunity detection happening continuously in the background.
