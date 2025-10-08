/**
 * Agentic Workflow Page - Enhanced UI/UX
 * Real-time multi-agent workflow execution with SSE streaming
 */

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Play,
    Square,
    Brain,
    Users,
    Settings,
    CheckCircle,
    Circle,
    Loader,
    Activity,
    Bot,
    User,
    Cog,
    TrendingUp,
    Clock,
    AlertCircle,
    ChevronDown,
    ChevronUp,
    Download
} from 'lucide-react';

// Backend URL
const BACKEND_URL = 'http://localhost:8002';

// TypeScript Interfaces
interface WorkflowEvent {
    type: string;
    data: {
        agent?: string;
        message?: string;
        task_id?: string;
        description?: string;
        status?: string;
        owner?: string;
        result?: string;
        workflow_id?: string;
        outcome?: any;
        tasks_completed?: number;
        total_tasks?: number;
    };
    timestamp: string;
}

interface Task {
    id: string;
    description: string;
    status: 'pending' | 'in_progress' | 'completed' | 'failed';
    owner: string;
    result?: string;
}

interface WorkflowScenario {
    id: string;
    name: string;
    description: string;
    estimated_duration: string;
    agents_involved: string[];
}

const WorkflowPage: React.FC = () => {
    // State
    const [events, setEvents] = useState<WorkflowEvent[]>([]);
    const [tasks, setTasks] = useState<Task[]>([]);
    const [isRunning, setIsRunning] = useState(false);
    const [selectedScenario, setSelectedScenario] = useState('open_roth_ira');
    const [clientId, setClientId] = useState('test_client_complete');
    const [scenarios, setScenarios] = useState<WorkflowScenario[]>([]);
    const [workflowStatus, setWorkflowStatus] = useState<string>('idle');
    const [progress, setProgress] = useState(0);
    const [thinkingAgent, setThinkingAgent] = useState<string | null>(null);
    const [startTime, setStartTime] = useState<Date | null>(null);
    const [endTime, setEndTime] = useState<Date | null>(null);
    const [expandedEvents, setExpandedEvents] = useState(true);

    // Refs
    const eventSourceRef = useRef<EventSource | null>(null);
    const eventsEndRef = useRef<HTMLDivElement>(null);

    // Load scenarios on mount
    useEffect(() => {
        loadScenarios();
    }, []);

    // Auto-scroll to bottom when new events arrive
    useEffect(() => {
        eventsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [events]);

    // Load available scenarios
    const loadScenarios = async () => {
        try {
            const response = await axios.get(`${BACKEND_URL}/api/workflow/scenarios`);
            setScenarios(response.data.scenarios);
        } catch (error) {
            console.error('Failed to load scenarios:', error);
            toast.error('Failed to load workflow scenarios');
        }
    };

    // Start workflow with SSE streaming
    const startWorkflow = () => {
        if (isRunning) return;

        const scenario = scenarios.find(s => s.id === selectedScenario);
        if (!scenario) {
            toast.error('Please select a scenario');
            return;
        }

        setIsRunning(true);
        setWorkflowStatus('running');
        setEvents([]);
        setTasks([]);
        setProgress(0);
        setStartTime(new Date());
        setEndTime(null);

        const url = `${BACKEND_URL}/api/workflow/stream?request_type=${selectedScenario}&client_id=${clientId}&client_name=${encodeURIComponent(clientId)}&initiator=web_ui`;

        const eventSource = new EventSource(url);
        eventSourceRef.current = eventSource;

        // Event: workflow_start
        eventSource.addEventListener('workflow_start', (e) => {
            const data = JSON.parse(e.data);
            const event: WorkflowEvent = {
                type: 'workflow_start',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);
        });

        // Event: agent_message
        eventSource.addEventListener('agent_message', (e) => {
            const data = JSON.parse(e.data);
            const event: WorkflowEvent = {
                type: 'agent_message',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);

            // Parse task completion from agent messages
            const message = data.message || '';
            const taskMatch = message.match(/Marked task '(task_\d+)' as completed/);
            if (taskMatch) {
                const taskId = taskMatch[1];
                setTasks(prev => prev.map(t =>
                    t.id === taskId ? { ...t, status: 'completed' as const } : t
                ));
            }

            // Initialize tasks from workflow plan
            const planMatch = message.match(/Workflow plan created with (\d+) tasks/);
            if (planMatch) {
                const taskCount = parseInt(planMatch[1]);
                const newTasks = Array.from({ length: taskCount }, (_, i) => ({
                    id: `task_${i + 1}`,
                    description: `Task ${i + 1}`,
                    status: 'pending' as const,
                    owner: 'unknown'
                }));
                setTasks(newTasks);
            }
        });

        // Event: task_update
        eventSource.addEventListener('task_update', (e) => {
            const data = JSON.parse(e.data);
            const event: WorkflowEvent = {
                type: 'task_update',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);

            if (data?.task_id) {
                setTasks(prev => {
                    const existing = prev.find(t => t.id === data?.task_id);
                    if (existing) {
                        return prev.map(t =>
                            t.id === data?.task_id
                                ? {
                                    ...t,
                                    status: data?.status as any,
                                    result: data?.result,
                                    description: data?.description || t.description,
                                    owner: data?.owner || t.owner
                                }
                                : t
                        );
                    } else {
                        return [...prev, {
                            id: data.task_id!,
                            description: data?.description || `Task ${data.task_id}`,
                            status: data?.status as any || 'pending',
                            owner: data?.owner || 'unknown',
                            result: data?.result
                        }];
                    }
                });
            }
        });

        // Event: llm_call
        eventSource.addEventListener('llm_call', (e) => {
            const data = JSON.parse(e.data);
            if (data.message?.includes('Making LLM API call')) {
                setThinkingAgent(data.agent);
            }
            const event: WorkflowEvent = {
                type: 'llm_call',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);
        });

        // Event: tool_execution
        eventSource.addEventListener('tool_execution', (e) => {
            const data = JSON.parse(e.data);
            setThinkingAgent(null);
            const event: WorkflowEvent = {
                type: 'tool_execution',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);
        });

        // Event: success
        eventSource.addEventListener('success', (e) => {
            const data = JSON.parse(e.data);
            setThinkingAgent(null);
            const event: WorkflowEvent = {
                type: 'success',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);
        });

        // Event: error
        eventSource.addEventListener('error', (e: any) => {
            setThinkingAgent(null);
            // Error events from EventSource don't have data property
            const data = e.data ? JSON.parse(e.data) : { message: 'Connection error' };
            const event: WorkflowEvent = {
                type: 'error',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);
            toast.error(data.message || 'Workflow error occurred');
        });

        // Event: routing
        eventSource.addEventListener('routing', (e) => {
            const data = JSON.parse(e.data);
            const event: WorkflowEvent = {
                type: 'routing',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);
        });

        // Event: log
        eventSource.addEventListener('log', (e) => {
            const data = JSON.parse(e.data);
            const event: WorkflowEvent = {
                type: 'log',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);
        });

        // Event: notification
        eventSource.addEventListener('notification', (e) => {
            const data = JSON.parse(e.data);
            const event: WorkflowEvent = {
                type: 'notification',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);
        });

        // Event: workflow_complete
        eventSource.addEventListener('workflow_complete', (e) => {
            const data = JSON.parse(e.data);
            const event: WorkflowEvent = {
                type: 'workflow_complete',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);
            setThinkingAgent(null);
            setWorkflowStatus(data.status || 'completed');
            setProgress(100);
            setIsRunning(false);
            setEndTime(new Date());
            eventSource.close();
            toast.success(`Workflow ${data.status || 'completed'}!`);
        });

        // Connection error handler
        eventSource.onerror = (error) => {
            console.error('EventSource error:', error);
            setIsRunning(false);
            setWorkflowStatus('error');
            setThinkingAgent(null);
            eventSource.close();
            toast.error('Connection to workflow stream lost');
        };

        toast.success('Workflow started!');
    };

    // Stop workflow
    const stopWorkflow = () => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }
        setIsRunning(false);
        setWorkflowStatus('stopped');
        setThinkingAgent(null);
        toast('Workflow stopped', { icon: '⏹️' });
    };

    // Download CSV log of all created accounts
    const downloadCSVLog = async () => {
        try {
            const response = await axios.get(`${BACKEND_URL}/api/workflow/accounts-log`, {
                responseType: 'blob'
            });

            // Create a download link
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'nexhelm_accounts_log.csv');
            document.body.appendChild(link);
            link.click();
            link.remove();

            toast.success('📥 CSV log downloaded successfully!');
        } catch (error: any) {
            if (error.response?.status === 404) {
                toast.error('No accounts log found. Create an account first!');
            } else {
                toast.error('Failed to download CSV log');
            }
            console.error('CSV download error:', error);
        }
    };

    // Update progress based on task completion
    useEffect(() => {
        const validTasks = tasks.filter(t => t.id && (t.description || t.owner));
        if (validTasks.length > 0) {
            const completed = validTasks.filter(t => t.status === 'completed').length;
            const newProgress = (completed / validTasks.length) * 100;
            setProgress(newProgress);
        }
    }, [tasks]);

    // Format technical messages to human-readable
    const formatEventMessage = (message: string): string => {
        if (!message) return 'Processing...';

        // Tool execution formatting
        if (message.includes("Executing tool")) {
            if (message.includes("check_eligibility")) {
                return "✅ Checking client eligibility for Roth IRA";
            }
            if (message.includes("validate_document")) {
                return "📄 Validating submitted documents";
            }
            if (message.includes("get_document")) {
                return "📥 Retrieving client documents";
            }
            if (message.includes("open_account")) {
                return "🏦 Creating Roth IRA account";
            }
            if (message.includes("create_document")) {
                return "📝 Preparing application forms";
            }
            if (message.includes("send_notification")) {
                return "📧 Sending notification to client";
            }
            if (message.includes("get_client_info")) {
                return "👤 Fetching client information";
            }
        }

        // Tool result formatting
        if (message.includes("Tool result:")) {
            if (message.includes("eligible")) {
                return "✅ Client is eligible for Roth IRA";
            }
            if (message.includes("account_number")) {
                const match = message.match(/ROTH_IRA-\d+/);
                return match ? `🎉 Account ${match[0]} created successfully!` : "🎉 Account created successfully!";
            }
            if (message.includes("valid")) {
                return "✅ Documents validated successfully";
            }
            if (message.includes("success")) {
                return "✅ Task completed successfully";
            }
            // Hide verbose tool results
            return "";
        }

        // Notification formatting
        if (message.includes("NOTIFICATION SENT")) {
            return "📧 Client notification sent successfully";
        }

        // Clean up agent names
        let formatted = message
            .replace(/_AGENT/g, '')
            .replace(/_/g, ' ')
            .replace(/ORCHESTRATOR/g, 'Orchestrator')
            .replace(/ADVISOR/g, 'Advisor')
            .replace(/OPERATIONS/g, 'Operations');

        // Remove overly technical details but keep important info
        if (formatted.includes("with params:")) {
            formatted = formatted.split("with params:")[0].trim();
        }

        return formatted;
    };

    // Get agent color
    const getAgentColor = (agent?: string) => {
        if (!agent) return 'text-gray-600';
        if (agent.includes('ORCHESTRATOR')) return 'text-purple-600';
        if (agent.includes('ADVISOR')) return 'text-blue-600';
        if (agent.includes('OPERATIONS')) return 'text-orange-600';
        if (agent.includes('SYSTEM')) return 'text-gray-600';
        return 'text-gray-600';
    };

    // Get agent icon
    const getAgentIcon = (agent?: string) => {
        if (!agent) return <Bot size={20} />;
        if (agent.includes('ORCHESTRATOR')) return <Brain size={20} />;
        if (agent.includes('ADVISOR')) return <User size={20} />;
        if (agent.includes('OPERATIONS')) return <Cog size={20} />;
        if (agent.includes('SYSTEM')) return <Settings size={20} />;
        return <Bot size={20} />;
    };

    // Get task status icon
    const getTaskIcon = (status: string) => {
        switch (status) {
            case 'completed': return <CheckCircle className="text-green-500" size={20} />;
            case 'in_progress': return <Loader className="text-blue-500 animate-spin" size={20} />;
            case 'failed': return <AlertCircle className="text-red-500" size={20} />;
            default: return <Circle className="text-gray-400" size={20} />;
        }
    };

    // Filter events - only show important conversational messages
    const shouldDisplayEvent = (event: WorkflowEvent): boolean => {
        const message = event.data?.message?.toLowerCase() || '';

        // Always show these
        if (event.type === 'workflow_start') return true;
        if (event.type === 'workflow_complete') return true;
        if (event.type === 'success' && !message.includes('llm response')) return true;
        if (event.type === 'error') return true;
        if (event.type === 'notification') return true;

        // Show important agent messages
        if (event.type === 'agent_message') {
            if (message.includes('creating') ||
                message.includes('plan created') ||
                message.includes('tasks completed') ||
                message.includes('eligible') ||
                message.includes('account') ||
                message.includes('client notified') ||
                message.includes('workflow complete')) {
                return true;
            }
        }

        // Show important tool executions
        if (event.type === 'tool_execution' && message.includes('executing tool')) {
            return true;
        }

        // Hide noisy technical events
        return false;
    };

    // Get filtered events for display with deduplication
    const displayEvents = events
        .filter(shouldDisplayEvent)
        .filter(event => {
            const formatted = formatEventMessage(event.data?.message || '');
            return formatted && formatted !== 'Processing...';
        })
        .filter((event, index, array) => {
            // Remove consecutive duplicates
            if (index === 0) return true;
            const currentFormatted = formatEventMessage(event.data?.message || '');
            const previousFormatted = formatEventMessage(array[index - 1].data?.message || '');
            const currentAgent = event.data?.agent;
            const previousAgent = array[index - 1].data?.agent;

            // Keep if message is different OR agent is different
            return currentFormatted !== previousFormatted || currentAgent !== previousAgent;
        });

    // Calculate workflow duration
    const getWorkflowDuration = () => {
        if (!startTime) return '0s';
        const end = endTime || new Date();
        const duration = Math.floor((end.getTime() - startTime.getTime()) / 1000);
        const minutes = Math.floor(duration / 60);
        const seconds = duration % 60;
        return minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
    };

    // Get workflow phase
    const getWorkflowPhase = () => {
        const validTasks = tasks.filter(t => t.id && (t.description || t.owner));
        const completedTasks = validTasks.filter(t => t.status === 'completed').length;
        const totalTasks = validTasks.length;

        if (totalTasks === 0) return 'Initializing';
        if (completedTasks === 0) return 'Planning';
        if (completedTasks < totalTasks * 0.5) return 'Execution';
        if (completedTasks < totalTasks) return 'Finalizing';
        return 'Complete';
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
            {/* Header */}
            <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 px-6 py-4 shadow-sm sticky top-0 z-10">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <div className="p-2 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl">
                            <Brain className="text-white" size={28} />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                                Agentic Workflow System
                            </h1>
                            <p className="text-sm text-gray-500">Multi-Agent LLM-Powered Automation</p>
                        </div>
                    </div>

                    <div className="flex items-center space-x-4">
                        {/* Status Badge */}
                        <div className={`px-4 py-2 rounded-full text-sm font-medium flex items-center space-x-2 ${workflowStatus === 'running' ? 'bg-blue-100 text-blue-700' :
                            workflowStatus === 'completed' ? 'bg-green-100 text-green-700' :
                                workflowStatus === 'error' ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                            }`}>
                            <span className={`w-2 h-2 rounded-full ${workflowStatus === 'running' ? 'bg-blue-500 animate-pulse' :
                                workflowStatus === 'completed' ? 'bg-green-500' :
                                    workflowStatus === 'error' ? 'bg-red-500' :
                                        'bg-gray-400'
                                }`} />
                            <span>
                                {workflowStatus === 'running' ? 'Running' :
                                    workflowStatus === 'completed' ? 'Completed' :
                                        workflowStatus === 'error' ? 'Error' :
                                            'Idle'}
                            </span>
                        </div>

                        {/* Duration */}
                        {startTime && (
                            <div className="flex items-center space-x-2 text-sm text-gray-600 bg-gray-100 px-3 py-2 rounded-lg">
                                <Clock size={16} />
                                <span>{getWorkflowDuration()}</span>
                            </div>
                        )}
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="p-6 max-w-7xl mx-auto">
                {/* Control Panel */}
                <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl p-6 mb-6 border border-gray-100">
                    <h2 className="text-lg font-semibold mb-4 flex items-center">
                        <Settings className="mr-2 text-purple-600" size={20} />
                        Workflow Configuration
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Scenario
                            </label>
                            <select
                                value={selectedScenario}
                                onChange={(e) => setSelectedScenario(e.target.value)}
                                disabled={isRunning}
                                className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100 transition-all"
                            >
                                {scenarios.map(scenario => (
                                    <option key={scenario.id} value={scenario.id}>
                                        {scenario.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Client ID
                            </label>
                            <input
                                type="text"
                                value={clientId}
                                onChange={(e) => setClientId(e.target.value)}
                                disabled={isRunning}
                                className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100 transition-all"
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-3 items-end">
                            {!isRunning ? (
                                <button
                                    onClick={startWorkflow}
                                    className="px-6 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl transform hover:scale-105"
                                >
                                    <Play size={20} />
                                    <span>Start Workflow</span>
                                </button>
                            ) : (
                                <button
                                    onClick={stopWorkflow}
                                    className="px-6 py-2 bg-gradient-to-r from-red-600 to-pink-600 text-white rounded-xl hover:from-red-700 hover:to-pink-700 transition-all flex items-center justify-center space-x-2 shadow-lg"
                                >
                                    <Square size={20} />
                                    <span>Stop Workflow</span>
                                </button>
                            )}
                            <button
                                onClick={downloadCSVLog}
                                className="px-6 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl transform hover:scale-105"
                            >
                                <Download size={20} />
                                <span>Download Log</span>
                            </button>
                        </div>
                    </div>

                    {/* Progress Bar & Phase */}
                    {isRunning && (
                        <div className="mt-6 space-y-3">
                            <div className="flex justify-between items-center text-sm">
                                <span className="text-gray-600">Phase: <span className="font-semibold text-purple-600">{getWorkflowPhase()}</span></span>
                                <span className="text-gray-600">{Math.round(progress)}% Complete</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                                <motion.div
                                    className="bg-gradient-to-r from-purple-500 to-indigo-500 h-3 rounded-full shadow-lg"
                                    initial={{ width: 0 }}
                                    animate={{ width: `${progress}%` }}
                                    transition={{ duration: 0.5, ease: "easeOut" }}
                                />
                            </div>
                        </div>
                    )}
                </div>

                {/* Metrics Dashboard */}
                {tasks.length > 0 && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                        <div className="bg-white/90 backdrop-blur-sm rounded-xl p-4 border border-gray-100 shadow-md">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-500">Total Tasks</p>
                                    <p className="text-2xl font-bold text-gray-800">
                                        {tasks.filter(t => t.id && (t.description || t.owner)).length}
                                    </p>
                                </div>
                                <Activity className="text-purple-500" size={32} />
                            </div>
                        </div>
                        <div className="bg-white/90 backdrop-blur-sm rounded-xl p-4 border border-gray-100 shadow-md">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-500">Completed</p>
                                    <p className="text-2xl font-bold text-green-600">
                                        {tasks.filter(t => t.id && (t.description || t.owner) && t.status === 'completed').length}
                                    </p>
                                </div>
                                <CheckCircle className="text-green-500" size={32} />
                            </div>
                        </div>
                        <div className="bg-white/90 backdrop-blur-sm rounded-xl p-4 border border-gray-100 shadow-md">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-500">Events</p>
                                    <p className="text-2xl font-bold text-blue-600">{displayEvents.length}</p>
                                </div>
                                <TrendingUp className="text-blue-500" size={32} />
                            </div>
                        </div>
                        <div className="bg-white/90 backdrop-blur-sm rounded-xl p-4 border border-gray-100 shadow-md">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-500">Duration</p>
                                    <p className="text-2xl font-bold text-indigo-600">{getWorkflowDuration()}</p>
                                </div>
                                <Clock className="text-indigo-500" size={32} />
                            </div>
                        </div>
                    </div>
                )}

                {/* Two Column Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Tasks Panel */}
                    <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-gray-100">
                        <h2 className="text-lg font-semibold mb-4 flex items-center justify-between">
                            <div className="flex items-center">
                                <Activity className="mr-2 text-orange-600" size={20} />
                                <span>Tasks ({tasks.filter(t => t.id && (t.description || t.owner) && t.status === 'completed').length}/{tasks.filter(t => t.id && (t.description || t.owner)).length})</span>
                            </div>
                        </h2>

                        <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
                            {tasks.filter(t => t.id && (t.description || t.owner)).length === 0 ? (
                                <div className="text-center text-gray-400 py-12">
                                    <Circle size={48} className="mx-auto mb-3 opacity-50" />
                                    <p className="font-medium">No tasks yet</p>
                                    <p className="text-sm mt-1">Start a workflow to see tasks</p>
                                </div>
                            ) : (
                                <AnimatePresence>
                                    {tasks.filter(t => t.id && (t.description || t.owner)).map((task, index) => (
                                        <motion.div
                                            key={task.id}
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: index * 0.1 }}
                                            className={`p-4 border-2 rounded-xl transition-all ${task.status === 'completed' ? 'bg-green-50 border-green-200 shadow-sm' :
                                                task.status === 'in_progress' ? 'bg-blue-50 border-blue-200 shadow-md' :
                                                    task.status === 'failed' ? 'bg-red-50 border-red-200' :
                                                        'bg-gray-50 border-gray-200'
                                                }`}
                                        >
                                            <div className="flex items-start space-x-3">
                                                <div className="mt-0.5">
                                                    {getTaskIcon(task.status)}
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <p className="text-sm font-medium text-gray-800 mb-2">
                                                        {task.description || 'Loading task details...'}
                                                    </p>
                                                    <div className="flex items-center flex-wrap gap-2">
                                                        {task.owner && (
                                                            <span className="inline-flex items-center px-2 py-1 bg-white rounded-md text-xs font-medium border border-gray-200">
                                                                {getAgentIcon(task.owner)}
                                                                <span className="ml-1">{task.owner.replace('_', ' ')}</span>
                                                            </span>
                                                        )}
                                                        <span className={`px-2 py-1 rounded-md text-xs font-medium ${task.status === 'completed' ? 'bg-green-100 text-green-700' :
                                                            task.status === 'in_progress' ? 'bg-blue-100 text-blue-700' :
                                                                task.status === 'failed' ? 'bg-red-100 text-red-700' :
                                                                    'bg-gray-100 text-gray-600'
                                                            }`}>
                                                            {task.status}
                                                        </span>
                                                    </div>
                                                    {task.result && (
                                                        <p className="mt-2 text-xs text-gray-600 italic bg-white/50 p-2 rounded">
                                                            {task.result}
                                                        </p>
                                                    )}
                                                </div>
                                            </div>
                                        </motion.div>
                                    ))}
                                </AnimatePresence>
                            )}
                        </div>
                    </div>

                    {/* Events Stream Panel */}
                    <div className="lg:col-span-2 bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-gray-100">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold flex items-center">
                                <Users className="mr-2 text-blue-600" size={20} />
                                Live Event Stream
                            </h2>
                            <button
                                onClick={() => setExpandedEvents(!expandedEvents)}
                                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                            >
                                {expandedEvents ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                            </button>
                        </div>

                        {expandedEvents && (
                            <div className="space-y-2 max-h-[600px] overflow-y-auto bg-gradient-to-b from-gray-50 to-white rounded-xl p-4 border border-gray-100">
                                {displayEvents.length === 0 && !thinkingAgent ? (
                                    <div className="text-center text-gray-400 py-12">
                                        <Activity size={48} className="mx-auto mb-3 opacity-50" />
                                        <p className="font-medium">No activity yet</p>
                                        <p className="text-sm mt-1">Start a workflow to see agent communication</p>
                                    </div>
                                ) : (
                                    <AnimatePresence>
                                        {displayEvents.map((event, index) => (
                                            <motion.div
                                                key={index}
                                                initial={{ opacity: 0, y: 10 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                exit={{ opacity: 0, scale: 0.95 }}
                                                transition={{ duration: 0.2 }}
                                                className="bg-white border-2 border-gray-200 rounded-xl p-4 hover:shadow-lg hover:border-purple-200 transition-all"
                                            >
                                                <div className="flex items-start space-x-3">
                                                    <div className="p-2 bg-gradient-to-br from-purple-100 to-indigo-100 rounded-lg">
                                                        <span className={getAgentColor(event.data?.agent)}>
                                                            {getAgentIcon(event.data?.agent)}
                                                        </span>
                                                    </div>
                                                    <div className="flex-1 min-w-0">
                                                        <div className="flex items-center justify-between mb-1">
                                                            <span className={`text-sm font-bold ${getAgentColor(event.data?.agent)}`}>
                                                                {event.data?.agent?.replace('_AGENT', '').replace('_', ' ') || 'System'}
                                                            </span>
                                                            <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded-full">
                                                                {new Date(event.timestamp).toLocaleTimeString()}
                                                            </span>
                                                        </div>
                                                        <p className="text-sm text-gray-700 leading-relaxed">
                                                            {formatEventMessage(event.data?.message || 'Processing...')}
                                                        </p>
                                                    </div>
                                                </div>
                                            </motion.div>
                                        ))}

                                        {/* Thinking Indicator */}
                                        {thinkingAgent && (
                                            <motion.div
                                                initial={{ opacity: 0, y: 10 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-4"
                                            >
                                                <div className="flex items-start space-x-3">
                                                    <Brain className="text-blue-500 animate-pulse" size={28} />
                                                    <div className="flex-1">
                                                        <span className={`text-sm font-bold ${getAgentColor(thinkingAgent)}`}>
                                                            {thinkingAgent.replace('_AGENT', '').replace('_', ' ')}
                                                        </span>
                                                        <div className="flex items-center space-x-2 mt-1">
                                                            <span className="text-sm text-gray-600">thinking</span>
                                                            <motion.span
                                                                animate={{ opacity: [0.4, 1, 0.4] }}
                                                                transition={{ duration: 1.5, repeat: Infinity }}
                                                                className="text-blue-500 font-bold text-lg"
                                                            >
                                                                ...
                                                            </motion.span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                )}
                                <div ref={eventsEndRef} />
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default WorkflowPage;
