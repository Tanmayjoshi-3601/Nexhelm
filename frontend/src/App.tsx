/**
 * Main App Component
 * This is the root component that manages the entire application state
 * and coordinates between different panels
 */

import React, { useState, useEffect } from 'react';
// import io, { Socket } from 'socket.io-client'; // Using native WebSocket instead
import axios from 'axios';
import toast, { Toaster } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Wifi,
  WifiOff,
  Users,
  TrendingUp,
  AlertCircle,
  Mic,
  MicOff
} from 'lucide-react';

// TypeScript interfaces - these define the shape of our data
interface Message {
  speaker: 'Client' | 'Advisor';
  text: string;
  timestamp: string;
}

interface Opportunity {
  type: string;
  title: string;
  description: string;
  score: number;
  detected_by: string;
  trigger?: string;
  timestamp: string;
}

interface ClientProfile {
  age: number;
  income: number;
  family_status: string;
  name: string;
}

// Backend URL - in production this would be an environment variable
const BACKEND_URL = 'http://localhost:8002';

const App: React.FC = () => {
  // State management - React hooks to manage component data
  // useState returns [currentValue, setterFunction]

  // Meeting state
  const [meetingId, setMeetingId] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  // WebSocket state
  const [socket, setSocket] = useState<WebSocket | null>(null);

  // Conversation state
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');

  // Opportunities state
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [totalOpportunityValue, setTotalOpportunityValue] = useState(0);

  // UI state
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  // Demo state
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [demoScenarios, setDemoScenarios] = useState<{ [key: string]: { name: string, duration: number } }>({});
  const [selectedScenario, setSelectedScenario] = useState<string>('');

  // Client profile (mock data for demo)
  const clientProfile: ClientProfile = {
    name: 'John & Sarah Mitchell',
    age: 58,
    income: 150000,
    family_status: 'Married with 2 children'
  };

  /**
   * Create a new meeting
   * This calls our backend API to generate a meeting ID
   */
  const createMeeting = async () => {
    try {
      // Show loading toast
      const loadingToast = toast.loading('Creating meeting...');

      // Make API call to backend
      const response = await axios.post(`${BACKEND_URL}/api/meeting/create`);
      const { meeting_id } = response.data;

      // Update state with new meeting ID
      setMeetingId(meeting_id);

      // Update toast to success
      toast.success('Meeting created!', { id: loadingToast });

      // Automatically connect after creating
      setTimeout(() => connectToMeeting(meeting_id), 500);

    } catch (error) {
      console.error('Failed to create meeting:', error);
      toast.error('Failed to create meeting');
    }
  };

  /**
   * Connect to WebSocket for real-time communication
   * @param meetingIdToConnect - The meeting ID to connect to
   */
  const connectToMeeting = (meetingIdToConnect: string) => {
    // Create new WebSocket connection
    const wsUrl = `${BACKEND_URL.replace('http', 'ws')}/ws/${meetingIdToConnect}`;
    const newSocket = new WebSocket(wsUrl);

    // When connected successfully
    newSocket.onopen = () => {
      console.log('Connected to WebSocket');
      setIsConnected(true);
      toast.success('Connected to meeting');
    };

    // When receiving a message
    newSocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'message') {
          const newMessage: Message = {
            speaker: data.speaker,
            text: data.text,
            timestamp: data.timestamp || new Date().toISOString()
          };
          setMessages(prev => [...prev, newMessage]);
        } else if (data.type === 'history') {
          console.log('Received history:', data.messages);
          if (data.messages && data.messages.length > 0) {
            const historyMessages = data.messages.map((msg: string) => {
              const [speaker, ...textParts] = msg.split(': ');
              return {
                speaker: speaker as 'Client' | 'Advisor',
                text: textParts.join(': '),
                timestamp: new Date().toISOString()
              };
            });
            setMessages(historyMessages);
          }
        } else if (data.type === 'opportunity') {
          console.log('Opportunity detected:', data);

          const newOpportunity: Opportunity = {
            type: data.opportunity.type,
            title: data.opportunity.title,
            description: data.opportunity.description,
            score: data.score,
            detected_by: data.detected_by || data.opportunity.detected_by,
            trigger: data.opportunity.trigger,
            timestamp: data.opportunity.timestamp || new Date().toISOString()
          };

          // Add to opportunities list
          setOpportunities(prev => {
            // Check if this opportunity type already exists
            const exists = prev.some(opp => opp.type === newOpportunity.type);
            if (exists) {
              // Update existing opportunity if score is higher
              return prev.map(opp =>
                opp.type === newOpportunity.type && newOpportunity.score > opp.score
                  ? newOpportunity
                  : opp
              );
            }
            // Add new opportunity
            return [...prev, newOpportunity].sort((a, b) => b.score - a.score);
          });

          // Show notification for high-priority opportunities
          if (data.score >= 85) {
            toast.success(`High Priority: ${data.opportunity.title}`, {
              duration: 5000,
              icon: '🎯',
            });
          }

          // Update total value (mock calculation)
          setTotalOpportunityValue(prev => prev + (data.score * 100));
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    // When disconnected
    newSocket.onclose = () => {
      console.log('Disconnected from WebSocket');
      setIsConnected(false);
      toast.error('Disconnected from meeting');
    };

    // Handle connection errors
    newSocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
      toast.error('WebSocket connection error');
    };

    // Save socket instance to state
    setSocket(newSocket);
  };

  /**
   * Send a message through WebSocket
   */
  const sendMessage = () => {
    // Check if we have a connection and text to send
    if (!socket || socket.readyState !== WebSocket.OPEN || !inputText.trim()) return;

    // Create message object
    const message = {
      speaker: 'Client',
      text: inputText
    };

    // Send through WebSocket
    socket.send(JSON.stringify(message));

    // Clear input field
    setInputText('');

    // Show processing indicator briefly
    setIsProcessing(true);
    setTimeout(() => setIsProcessing(false), 1000);
  };

  /**
   * Simulate voice input (for demo purposes)
   * In production, this would use Web Speech API
   */
  const toggleRecording = () => {
    setIsRecording(!isRecording);

    if (!isRecording) {
      // Start recording simulation
      toast('Recording started...', { icon: '🎤' });

      // Simulate voice input after 3 seconds
      setTimeout(() => {
        if (socket) {
          const simulatedTranscript = "I'm thinking about retiring early. My daughter just got into Northwestern University.";
          setInputText(simulatedTranscript);
          setIsRecording(false);
          toast.success('Recording complete');
        }
      }, 3000);
    } else {
      toast('Recording stopped');
    }
  };

  /**
   * Load demo scenarios when component mounts
   */
  useEffect(() => {
    const loadDemoScenarios = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/api/demo/scenarios`);
        setDemoScenarios(response.data);
        // Set default scenario
        const firstScenario = Object.keys(response.data)[0];
        if (firstScenario) {
          setSelectedScenario(firstScenario);
        }
      } catch (error) {
        console.error('Failed to load demo scenarios:', error);
      }
    };

    loadDemoScenarios();
  }, []);

  /**
   * Start demo conversation
   */
  const startDemo = async () => {
    if (!meetingId || !selectedScenario) return;

    try {
      const response = await axios.post(`${BACKEND_URL}/api/demo/start/${meetingId}?scenario=${selectedScenario}`);
      if (response.data.status === 'Demo started') {
        setIsDemoMode(true);
        toast.success(`Demo started: ${demoScenarios[selectedScenario]?.name}`);
      } else {
        toast.error(response.data.error || 'Failed to start demo');
      }
    } catch (error) {
      console.error('Failed to start demo:', error);
      toast.error('Failed to start demo');
    }
  };

  /**
   * Stop demo conversation
   */
  const stopDemo = async () => {
    if (!meetingId) return;

    try {
      const response = await axios.post(`${BACKEND_URL}/api/demo/stop/${meetingId}`);
      if (response.data.status === 'Demo stopped') {
        setIsDemoMode(false);
        toast.success('Demo stopped');
      } else {
        toast.error(response.data.error || 'Failed to stop demo');
      }
    } catch (error) {
      console.error('Failed to stop demo:', error);
      toast.error('Failed to stop demo');
    }
  };

  /**
   * Clean up WebSocket connection when component unmounts
   */
  useEffect(() => {
    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, [socket]);

  /**
   * Render the UI
   * This is the JSX that defines what appears on screen
   */
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Toast notifications container */}
      <Toaster position="top-right" />

      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-nexhelm-blue">
              Nexhelm AI
            </h1>
            <span className="text-sm text-gray-500">
              Intelligent Opportunity Detection
            </span>
          </div>

          {/* Connection status indicator */}
          <div className="flex items-center space-x-4">
            {clientProfile && (
              <div className="text-sm text-gray-600">
                <span className="font-medium">{clientProfile.name}</span>
                <span className="mx-2">•</span>
                <span>Age {clientProfile.age}</span>
                <span className="mx-2">•</span>
                <span>${(clientProfile.income / 1000).toFixed(0)}k income</span>
              </div>
            )}

            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${isConnected ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
              }`}>
              {isConnected ? <Wifi size={16} /> : <WifiOff size={16} />}
              <span className="text-sm font-medium">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>

        {/* Meeting controls */}
        {!meetingId ? (
          <div className="mt-4">
            <button
              onClick={createMeeting}
              className="px-6 py-2 bg-nexhelm-blue text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Start New Meeting
            </button>
          </div>
        ) : (
          <div className="mt-4 space-y-4">
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                Meeting ID: <code className="bg-gray-100 px-2 py-1 rounded">{meetingId}</code>
              </span>
              {!isConnected && (
                <button
                  onClick={() => connectToMeeting(meetingId)}
                  className="px-4 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors text-sm"
                >
                  Reconnect
                </button>
              )}
            </div>

            {/* Demo Controls */}
            {isConnected && (
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-4 rounded-lg border border-purple-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <span className="text-sm font-medium text-purple-800">🎭 Demo Mode</span>
                    <select
                      value={selectedScenario}
                      onChange={(e) => setSelectedScenario(e.target.value)}
                      className="px-3 py-1 border border-purple-300 rounded text-sm"
                      disabled={isDemoMode}
                    >
                      {Object.entries(demoScenarios).map(([key, scenario]) => (
                        <option key={key} value={key}>
                          {scenario.name} ({scenario.duration}s)
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex items-center space-x-2">
                    {!isDemoMode ? (
                      <button
                        onClick={startDemo}
                        className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
                      >
                        ▶️ Start Demo
                      </button>
                    ) : (
                      <button
                        onClick={stopDemo}
                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
                      >
                        ⏹️ Stop Demo
                      </button>
                    )}
                  </div>
                </div>

                {isDemoMode && (
                  <div className="mt-2 text-xs text-purple-600">
                    🎬 Demo conversation running... Opportunities will appear automatically!
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </header>

      {/* Main content area */}
      <main className="flex h-[calc(100vh-140px)] p-6 gap-6">
        {/* Left Panel - Transcript */}
        <div className="flex-1 bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4">
            <h2 className="text-lg font-semibold">Meeting Transcript</h2>
            <p className="text-sm opacity-90">Real-time conversation</p>
          </div>

          {/* Messages area */}
          <div className="h-[calc(100%-200px)] overflow-y-auto p-4 space-y-3 custom-scrollbar">
            {messages.length === 0 ? (
              <div className="text-center text-gray-400 mt-10">
                <p>No messages yet. Start the conversation!</p>
              </div>
            ) : (
              <AnimatePresence>
                {messages.map((message, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`flex ${message.speaker === 'Client' ? 'justify-end' : 'justify-start'
                      }`}
                  >
                    <div className={`max-w-[70%] rounded-lg px-4 py-2 ${message.speaker === 'Client'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-800'
                      }`}>
                      <p className="text-sm font-medium mb-1">
                        {message.speaker}
                      </p>
                      <p>{message.text}</p>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            )}

            {isProcessing && (
              <div className="flex justify-center">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-100" />
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-200" />
                </div>
              </div>
            )}
          </div>

          {/* Input area */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex items-center space-x-2">
              <button
                onClick={toggleRecording}
                className={`p-2 rounded-full transition-colors ${isRecording
                  ? 'bg-red-500 text-white animate-pulse'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
                  }`}
              >
                {isRecording ? <Mic size={20} /> : <MicOff size={20} />}
              </button>

              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder={isDemoMode ? "Demo mode active - conversation running automatically..." : "Type a message or use voice..."}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={!isConnected || isDemoMode}
              />

              <button
                onClick={sendMessage}
                disabled={!isConnected || !inputText.trim() || isDemoMode}
                className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Send
              </button>
            </div>
          </div>
        </div>

        {/* Right Panel - Opportunities */}
        <div className="w-[400px] bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="bg-gradient-to-r from-amber-500 to-orange-500 text-white p-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Opportunities Detected</h2>
              <span className="bg-white/20 px-2 py-1 rounded-full text-sm">
                {opportunities.length}
              </span>
            </div>
            {totalOpportunityValue > 0 && (
              <p className="text-sm opacity-90 mt-1">
                Potential value: ${(totalOpportunityValue).toLocaleString()}
              </p>
            )}
          </div>

          {/* Opportunities list */}
          <div className="h-[calc(100%-100px)] overflow-y-auto p-4 space-y-3 custom-scrollbar">
            {opportunities.length === 0 ? (
              <div className="text-center text-gray-400 mt-10">
                <AlertCircle size={48} className="mx-auto mb-3 opacity-50" />
                <p>No opportunities detected yet</p>
                <p className="text-sm mt-2">They'll appear here as you talk</p>
              </div>
            ) : (
              <AnimatePresence>
                {opportunities.map((opportunity, index) => (
                  <motion.div
                    key={opportunity.type}
                    initial={{ opacity: 0, x: 100 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-lg p-4"
                  >
                    {/* Priority score badge */}
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-800">
                          {opportunity.title}
                        </h3>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${opportunity.score >= 85
                            ? 'bg-red-100 text-red-700'
                            : opportunity.score >= 70
                              ? 'bg-yellow-100 text-yellow-700'
                              : 'bg-green-100 text-green-700'
                            }`}>
                            {opportunity.score >= 85 ? 'High' : opportunity.score >= 70 ? 'Medium' : 'Low'} Priority
                          </span>
                          <span className="text-xs text-gray-500">
                            {opportunity.detected_by.replace('_', ' ')}
                          </span>
                        </div>
                      </div>
                      <div className="text-2xl font-bold text-amber-600">
                        {opportunity.score}
                      </div>
                    </div>

                    <p className="text-sm text-gray-600 mb-2">
                      {opportunity.description}
                    </p>

                    {opportunity.trigger && (
                      <p className="text-xs text-gray-500 italic">
                        Trigger: {opportunity.trigger}
                      </p>
                    )}

                    {/* Action buttons */}
                    <div className="flex space-x-2 mt-3">
                      <button className="flex-1 text-xs px-3 py-1.5 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors">
                        Add to CRM
                      </button>
                      <button className="flex-1 text-xs px-3 py-1.5 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors">
                        Create Task
                      </button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            )}
          </div>
        </div>
      </main>

      {/* Stats bar at bottom */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-6 text-sm">
            <div className="flex items-center space-x-2">
              <Users size={16} className="text-gray-500" />
              <span className="text-gray-600">
                Meeting Duration: {messages.length > 0 ? '5:23' : '0:00'}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <TrendingUp size={16} className="text-gray-500" />
              <span className="text-gray-600">
                Messages: {messages.length}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <AlertCircle size={16} className="text-gray-500" />
              <span className="text-gray-600">
                Opportunities: {opportunities.length}
              </span>
            </div>
          </div>

          <div className="text-sm text-gray-500">
            Powered by GPT-4 Intelligence
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;