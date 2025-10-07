# Dummy Transcript Service Flow Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           NEXHELM SYSTEM FLOW                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Dummy         │    │   Opportunity   │
│   (React)       │◄──►│   Backend       │◄──►│   Transcript    │◄──►│   Detector      │
│                 │    │   (main.py)     │    │   Service       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │                        │
                                ▼                        ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                       │   WebSocket     │    │   Redis         │    │   OpenAI        │
                       │   Manager       │    │   Database      │    │   GPT-4         │
                       └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Detailed Flow: Demo Conversation Start

```
1. CLIENT REQUEST
   ┌─────────────────────────────────────────────────────────────────┐
   │ POST /api/demo/start/{meeting_id}?scenario=retirement_planning  │
   └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
2. MAIN.PY PROCESSING
   ┌─────────────────────────────────────────────────────────────────┐
   │ @app.post("/api/demo/start/{meeting_id}")                      │
   │                                                                 │
   │ • Check if demo already running                                │
   │ • Create opportunity_callback function                         │
   │ • Call dummy_transcript_service.start_demo()                   │
   └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
3. DUMMY TRANSCRIPT SERVICE
   ┌─────────────────────────────────────────────────────────────────┐
   │ dummy_transcript_service.start_demo()                          │
   │                                                                 │
   │ • Load scenario data (retirement_planning)                     │
   │ • Create asyncio task for conversation                         │
   │ • Start message streaming loop                                 │
   └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
4. CONVERSATION LOOP (Async)
   ┌─────────────────────────────────────────────────────────────────┐
   │ for message in scenario_data["messages"]:                      │
   │                                                                 │
   │   ┌─────────────────────────────────────────────────────────┐   │
   │   │ 4a. SEND MESSAGE                                        │   │
   │   │ • WebSocket: "Client: Hi, thanks for meeting..."       │   │
   │   │ • All connected clients receive message                 │   │
   │   └─────────────────────────────────────────────────────────┘   │
   │                                │                               │
   │                                ▼                               │
   │   ┌─────────────────────────────────────────────────────────┐   │
   │   │ 4b. TRIGGER OPPORTUNITY DETECTION                       │   │
   │   │ • Call opportunity_callback(text, speaker)              │   │
   │   │ • Store message in Redis                                │   │
   │   │ • Get recent conversation context                       │   │
   │   └─────────────────────────────────────────────────────────┘   │
   │                                │                               │
   │                                ▼                               │
   │   ┌─────────────────────────────────────────────────────────┐   │
   │   │ 4c. WAIT FOR DELAY                                      │   │
   │   │ • await asyncio.sleep(message["delay"])                 │   │
   │   │ • Realistic conversation timing (2-5 seconds)          │   │
   │   └─────────────────────────────────────────────────────────┘   │
   └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
5. OPPORTUNITY DETECTION PROCESS
   ┌─────────────────────────────────────────────────────────────────┐
   │ opportunity_callback() function                                 │
   │                                                                 │
   │ ┌─────────────────────────────────────────────────────────────┐ │
   │ │ 5a. STORE MESSAGE IN REDIS                                  │ │
   │ │ • redis_client.add_message(meeting_id, message)            │ │
   │ │ • Key: "Conversation:{meeting_id}"                         │ │
   │ └─────────────────────────────────────────────────────────────┘ │
   │                                │                               │
   │                                ▼                               │
   │ ┌─────────────────────────────────────────────────────────────┐ │
   │ │ 5b. GET CONVERSATION CONTEXT                               │ │
   │ │ • recent_messages = redis_client.get_conversation(         │ │
   │ │   meeting_id, last_n=5)                                    │ │
   │ │ • context = "\n".join(recent_messages)                     │ │
   │ └─────────────────────────────────────────────────────────────┘ │
   │                                │                               │
   │                                ▼                               │
   │ ┌─────────────────────────────────────────────────────────────┐ │
   │ │ 5c. RUN 3-LAYER DETECTION                                  │ │
   │ │ • detector.detect_opportunities(context, client_profile)   │ │
   │ │ • Layer 1: Pattern matching (keywords)                    │ │
   │ │ • Layer 2: Contextual analysis (age + income)             │ │
   │ │ • Layer 3: LLM analysis (GPT-4)                           │ │
   │ └─────────────────────────────────────────────────────────────┘ │
   └─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
6. OPPORTUNITY PROCESSING
   ┌─────────────────────────────────────────────────────────────────┐
   │ for opportunity in opportunities:                               │
   │                                                                 │
   │   ┌─────────────────────────────────────────────────────────┐   │
   │   │ 6a. STORE IN REDIS                                      │   │
   │   │ • redis_client.add_opportunity(meeting_id, opportunity) │   │
   │   │ • Key: "opportunities:{meeting_id}"                     │   │
   │   │ • Sorted by score (highest first)                       │   │
   │   └─────────────────────────────────────────────────────────┘   │
   │                                │                               │
   │                                ▼                               │
   │   ┌─────────────────────────────────────────────────────────┐   │
   │   │ 6b. BROADCAST TO CLIENTS                                │   │
   │   │ • WebSocket: "opportunity" message                      │   │
   │   │ • All connected clients receive opportunity             │   │
   │   │ • Real-time notification                                │   │
   │   └─────────────────────────────────────────────────────────┘   │
   └─────────────────────────────────────────────────────────────────┘
```

## Example Conversation Flow

```
TIME 0:00  ┌─────────────────────────────────────────────────────────────────┐
           │ CLIENT: "Hi, thanks for meeting with me today."                │
           │ • Stored in Redis                                              │
           │ • No opportunities detected                                     │
           └─────────────────────────────────────────────────────────────────┘
                    │
                    ▼ (2 second delay)
TIME 0:02  ┌─────────────────────────────────────────────────────────────────┐
           │ ADVISOR: "Of course! I'm excited to help you plan for           │
           │         retirement. Tell me about your current situation."      │
           │ • Stored in Redis                                              │
           │ • Keyword "retirement" detected                                 │
           │ • Opportunity: "401(k) and Retirement Planning Review" (75)     │
           └─────────────────────────────────────────────────────────────────┘
                    │
                    ▼ (3 second delay)
TIME 0:05  ┌─────────────────────────────────────────────────────────────────┐
           │ CLIENT: "Well, I'm turning 60 next year and starting to think   │
           │         seriously about retirement."                            │
           │ • Stored in Redis                                              │
           │ • Age 60 + "retirement" = High priority                        │
           │ • Opportunity: "Early Retirement Planning" (88)                 │
           │ • Opportunity: "Catch-Up Contribution Strategy" (82)            │
           └─────────────────────────────────────────────────────────────────┘
                    │
                    ▼ (4 second delay)
TIME 0:09  ┌─────────────────────────────────────────────────────────────────┐
           │ ADVISOR: "That's a great milestone! What's your current         │
           │         retirement savings looking like?"                       │
           │ • Stored in Redis                                              │
           │ • Context builds for better LLM analysis                       │
           └─────────────────────────────────────────────────────────────────┘
```

## Data Flow in Redis

```
┌─────────────────────────────────────────────────────────────────┐
│                        REDIS DATABASE                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Conversation:{meeting_id} (Redis List)                         │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ [0] "Advisor: That's a great milestone! What's your..."    │ │
│ │ [1] "Client: Well, I'm turning 60 next year..."           │ │
│ │ [2] "Advisor: Of course! I'm excited to help..."          │ │
│ │ [3] "Client: Hi, thanks for meeting with me today."       │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ opportunities:{meeting_id} (Redis Sorted Set)                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Score 88: {"type": "early_retirement", "title": "Early...", │ │
│ │           "description": "At age 60, client showing..."}    │ │
│ │ Score 82: {"type": "catch_up_contributions", "title": "...",│ │
│ │           "description": "Age 60 qualifies for additional"} │ │
│ │ Score 75: {"type": "retirement_planning", "title": "401k...",│ │
│ │           "description": "Client may benefit from..."}      │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ meeting:{meeting_id} (Redis Hash)                              │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ client_id: "demo-client"                                    │ │
│ │ status: "active"                                            │ │
│ │ start_time: "1705312200"                                    │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## WebSocket Message Types

```
┌─────────────────────────────────────────────────────────────────┐
│                    WEBSOCKET MESSAGES                          │
└─────────────────────────────────────────────────────────────────┘

1. CONNECTION MESSAGE
   {
     "type": "connection",
     "message": "Connected to meeting",
     "meeting_id": "abc-123-def"
   }

2. CONVERSATION MESSAGE
   {
     "type": "message",
     "speaker": "Client",
     "text": "I'm thinking about retirement...",
     "timestamp": "2024-01-15T10:30:00"
   }

3. OPPORTUNITY DETECTED
   {
     "type": "opportunity",
     "opportunity": {
       "type": "retirement_planning",
       "title": "401(k) and Retirement Planning Review",
       "description": "Client may benefit from retirement account optimization",
       "score": 75,
       "detected_by": "pattern_matching",
       "trigger": "Keyword: retirement"
     },
     "score": 75,
     "detected_by": "pattern_matching"
   }

4. DEMO COMPLETE
   {
     "type": "demo_complete",
     "message": "Demo conversation completed! Scenario: Retirement Planning"
   }
```

## Key Differences from Previous Code

```
┌─────────────────────────────────────────────────────────────────┐
│                    BEFORE vs AFTER                              │
└─────────────────────────────────────────────────────────────────┘

BEFORE (Simple):
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Manual Text     │───►│ Basic Keyword   │───►│ Simple Response │
│ Input           │    │ Matching        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘

AFTER (Sophisticated):
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Realistic       │───►│ 3-Layer AI      │───►│ Real-time       │
│ Conversation    │    │ Detection       │    │ Opportunities   │
│ Scenarios       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Async Streaming │    │ Context-Aware   │    │ WebSocket       │
│ with Delays     │    │ Analysis        │    │ Broadcasting    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Redis State     │    │ Client Profile  │    │ Production      │
│ Management      │    │ Integration     │    │ Architecture    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

This flow diagram shows how the dummy transcription service creates a realistic demo experience by:

1. **Streaming pre-written conversations** with realistic timing
2. **Triggering opportunity detection** on each message
3. **Using 3-layer AI analysis** (pattern → context → LLM)
4. **Storing everything in Redis** for persistence
5. **Broadcasting opportunities** in real-time via WebSockets

The result is a demo that feels like a real financial advisor meeting, complete with intelligent opportunity detection happening in the background.
