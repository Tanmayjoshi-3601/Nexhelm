# Nexhelm - Real-Time Financial Advisor Opportunity Detection System

A cutting-edge AI-powered system that detects financial opportunities from live meeting transcripts in real-time. Built with FastAPI, React, WebSockets, and Redis for seamless real-time communication and intelligent opportunity detection.

## Features

### **Intelligent Opportunity Detection**
- **AI-Powered Analysis**: Uses GPT-3.5-turbo for sophisticated financial opportunity detection
- **Real-Time Processing**: Analyzes conversation context as it happens
- **Multiple Opportunity Types**: Retirement planning, education savings, life insurance, estate planning
- **Priority Scoring**: High/Medium/Low priority classification with numerical scores
- **Context-Aware**: Considers client profile, age, income, and conversation history

### **Interactive Demo System**
- **3 Realistic Scenarios**: Retirement Planning, Education Planning, Life Changes
- **1-2 Minute Conversations**: Natural timing with realistic pauses
- **Automatic Opportunity Detection**: Opportunities appear in real-time during demo
- **Professional Demo Experience**: Perfect for presentations and client meetings

###  **Real-Time Communication**
- **WebSocket Integration**: Instant message delivery and opportunity notifications
- **Live Transcript**: Real-time conversation display with speaker identification
- **Toast Notifications**: High-priority opportunity alerts
- **Connection Management**: Automatic reconnection and status indicators

###  **Modern UI/UX**
- **Beautiful Design**: Gradient backgrounds, smooth animations, and professional styling
- **Responsive Layout**: Works perfectly on desktop and mobile devices
- **Interactive Elements**: Hover effects, loading states, and visual feedback
- **Accessibility**: Clear typography, color contrast, and intuitive navigation

## 🏗️ Architecture

### **Backend (FastAPI + Python)**
```
backend/
├── app/
│   ├── main.py                 # FastAPI server with WebSocket endpoints
│   ├── opportunity_detector.py # AI-powered opportunity detection engine
│   ├── dummy_transcript.py     # Demo conversation scenarios
│   └── redis_client.py         # Redis state management
├── requirements.txt            # Python dependencies
└── test_*.py                  # Test files
```

### **Frontend (React + TypeScript)**
```
frontend/
├── src/
│   ├── App.tsx                # Main application component
│   ├── index.tsx              # Application entry point
│   └── index.css              # Global styles with Tailwind
├── package.json               # Node.js dependencies
└── tailwind.config.js         # Tailwind CSS configuration
```

### **Data Flow**
1. **WebSocket Connection**: Real-time bidirectional communication
2. **Message Processing**: Store in Redis, analyze with AI
3. **Opportunity Detection**: Context-aware financial opportunity identification
4. **Real-Time Updates**: Instant UI updates and notifications

##  Quick Start

### **Prerequisites**
- Python 3.11+ with conda
- Node.js 16+
- Redis server
- OpenAI API key

### **1. Environment Setup**
```bash
# Create and activate conda environment
conda create -n nexhelm python=3.11
conda activate nexhelm

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Install Node.js dependencies
cd ../frontend
npm install
```

### **2. Environment Variables**
Create a `.env` file in the backend directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### **3. Start the Application**

**Terminal 1 - Redis Server:**
```bash
redis-server
```

**Terminal 2 - Backend Server:**
```bash
conda activate nexhelm
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

**Terminal 3 - Frontend Server:**
```bash
cd frontend
npm start
```

### **4. Access the Application**
- **Main App**: http://localhost:3000
- **Backend API**: http://localhost:8002
- **API Documentation**: http://localhost:8002/docs
- **Test Interface**: http://localhost:8002/test

##  Demo Mode

### **Available Scenarios**

#### **1. Retirement Planning (90 seconds)**
- Topics: 401k optimization, Roth conversions, healthcare planning
- Opportunities: Retirement income planning, catch-up contributions, long-term care

#### **2. Education Planning (75 seconds)**
- Topics: 529 plans, college savings, Northwestern University
- Opportunities: Education savings strategies, financial aid optimization

#### **3. Life Changes & Planning (80 seconds)**
- Topics: New baby, promotion, house buying, life insurance
- Opportunities: Life insurance needs, estate planning, financial protection

### **How to Use Demo Mode**
1. **Start a Meeting**: Click "Start New Meeting"
2. **Select Scenario**: Choose from dropdown (Retirement, Education, Life Changes)
3. **Start Demo**: Click "▶️ Start Demo"
4. **Watch Magic**: Opportunities appear automatically in real-time
5. **Stop Anytime**: Click "⏹️ Stop Demo" to end early

## 🔧 API Endpoints

### **Meeting Management**
- `POST /api/meeting/create` - Create new meeting session
- `GET /api/meeting/{meeting_id}/history` - Get conversation history
- `WebSocket /ws/{meeting_id}` - Real-time communication

### **Demo System**
- `GET /api/demo/scenarios` - Get available demo scenarios
- `POST /api/demo/start/{meeting_id}` - Start demo conversation
- `POST /api/demo/stop/{meeting_id}` - Stop demo conversation
- `GET /api/demo/status/{meeting_id}` - Check demo status

##  Opportunity Detection Engine

### **Detection Methods**
1. **Pattern Matching**: Keyword-based detection for common financial topics
2. **AI Analysis**: GPT-3.5-turbo for sophisticated context understanding
3. **Client Profile**: Age, income, and family status consideration
4. **Conversation Context**: Recent message analysis for relevance

### **Opportunity Types**
- **Retirement Planning**: 401k, IRA, Roth conversions, catch-up contributions
- **Education Savings**: 529 plans, college funding, financial aid
- **Life Insurance**: Term life, whole life, disability insurance
- **Estate Planning**: Wills, trusts, beneficiary planning
- **Investment Planning**: Portfolio diversification, risk management

### **Scoring System**
- **High Priority (85-100)**: Immediate action recommended
- **Medium Priority (70-84)**: Important but not urgent
- **Low Priority (50-69)**: Good to consider for future

##  UI Components

### **Main Interface**
- **Header**: Connection status, client profile, meeting controls
- **Transcript Panel**: Real-time conversation with speaker identification
- **Opportunities Panel**: Live opportunity detection with priority scoring
- **Demo Controls**: Scenario selection and demo management
- **Input Area**: Message composition with voice simulation

### **Visual Elements**
- **Gradient Backgrounds**: Professional blue and amber color schemes
- **Smooth Animations**: Framer Motion for polished interactions
- **Toast Notifications**: Real-time feedback and alerts
- **Status Indicators**: Connection status, demo mode, processing states

## 🔒 Security & Best Practices

### **Data Handling**
- **Redis Storage**: Temporary conversation storage with TTL
- **API Key Management**: Secure environment variable handling
- **CORS Configuration**: Proper cross-origin resource sharing
- **Input Validation**: Sanitized user inputs and message handling

### **Performance**
- **Connection Pooling**: Efficient Redis connection management
- **Message Batching**: Optimized WebSocket message delivery
- **Caching Strategy**: Redis-based conversation and opportunity caching
- **Error Handling**: Graceful degradation and user feedback

##  Testing

### **Backend Testing**
```bash
cd backend
python -m pytest test_*.py
```

### **Frontend Testing**
```bash
cd frontend
npm test
```

### **Integration Testing**
- WebSocket connection testing
- Opportunity detection validation
- Demo scenario verification
- API endpoint testing

##  Monitoring & Logging

### **Backend Logs**
- Connection status and WebSocket events
- Opportunity detection results
- Redis operations and errors
- API request/response logging

### **Frontend Logs**
- WebSocket connection status
- Demo mode state changes
- User interaction tracking
- Error boundary handling

##  Deployment

### **Production Considerations**
- **Environment Variables**: Secure API key management
- **Redis Configuration**: Production Redis setup
- **WebSocket Scaling**: Load balancer WebSocket support
- **SSL/TLS**: HTTPS for secure communication
- **Monitoring**: Application performance monitoring

### **Docker Deployment**
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]

# Frontend Dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

##  Contributing

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### **Code Standards**
- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Strict mode, proper interfaces
- **React**: Functional components with hooks
- **Styling**: Tailwind CSS utility classes

##  License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI**: For providing the GPT-3.5-turbo API
- **FastAPI**: For the excellent Python web framework
- **React**: For the powerful frontend library
- **Redis**: For reliable data storage and caching
- **Tailwind CSS**: For beautiful, utility-first styling


*Nexhelm - Where AI meets financial opportunity detection*