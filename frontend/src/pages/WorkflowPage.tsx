/**
 * Agentic Workflow Page
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
    Activity
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
    const [clientId, setClientId] = useState('john_smith_123');
    const [scenarios, setScenarios] = useState<WorkflowScenario[]>([]);
    const [workflowStatus, setWorkflowStatus] = useState<string>('idle');
    const [progress, setProgress] = useState(0);
    const [thinkingAgent, setThinkingAgent] = useState<string | null>(null);

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

        // Clear previous state
        setEvents([]);
        setTasks([]);
        setIsRunning(true);
        setWorkflowStatus('running');
        setProgress(0);

        // Create EventSource for SSE
        const url = `${BACKEND_URL}/api/workflow/stream?request_type=${selectedScenario}&client_id=${clientId}&client_name=John Smith&initiator=web_ui`;
        const eventSource = new EventSource(url);
        eventSourceRef.current = eventSource;

        // Handle workflow start
        eventSource.addEventListener('workflow_start', (e) => {
            const data = JSON.parse(e.data);
            const event: WorkflowEvent = {
                type: 'workflow_start',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);
            toast.success('Workflow started!', { icon: '🚀' });
        });

        // Handle agent messages
        eventSource.addEventListener('agent_message', (e) => {
            const data = JSON.parse(e.data);
            const event: WorkflowEvent = {
                type: 'agent_message',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);

            // Extract task info from messages like "Marked task 'task_1' as completed"
            const message = data.message || '';
            if (message.includes('Marked task') && message.includes('as')) {
                const taskIdMatch = message.match(/task[_'](\w+)['"]/);
                const statusMatch = message.match(/as (\w+)/);

                if (taskIdMatch && statusMatch) {
                    const taskId = `task_${taskIdMatch[1]}`;
                    const status = statusMatch[1];

                    setTasks(prev => {
                        const existing = prev.find(t => t.id === taskId);
                        if (existing) {
                            return prev.map(t =>
                                t.id === taskId ? { ...t, status: status as any } : t
                            );
                        }
                        return prev;
                    });
                }
            }

            // Create tasks from "Workflow plan created with X tasks" message
            if (message.includes('plan created with') && message.includes('tasks')) {
                const tasksMatch = message.match(/(\d+) tasks/);
                if (tasksMatch) {
                    const taskCount = parseInt(tasksMatch[1]);
                    const newTasks: Task[] = [];
                    for (let i = 1; i <= taskCount; i++) {
                        newTasks.push({
                            id: `task_${i}`,
                            description: `Task ${i}`,
                            status: 'pending',
                            owner: 'SYSTEM'
                        });
                    }
                    setTasks(newTasks);
                }
            }
        });

        // Handle LLM calls - show thinking indicator
        eventSource.addEventListener('llm_call', (e) => {
            const data = JSON.parse(e.data);
            const event: WorkflowEvent = {
                type: 'llm_call',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);

            // Set thinking state
            if (data.agent) {
                setThinkingAgent(data.agent);
            }
        });

        // Handle tool execution - show as activity
        eventSource.addEventListener('tool_execution', (e) => {
            const data = JSON.parse(e.data);
            const event: WorkflowEvent = {
                type: 'tool_execution',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);

            // Clear thinking, show action
            setThinkingAgent(null);
        });

        // Handle routing
        eventSource.addEventListener('routing', (e) => {
            const data = JSON.parse(e.data);
            const event: WorkflowEvent = {
                type: 'routing',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);
        });

        // Handle task updates
        eventSource.addEventListener('task_update', (e) => {
            const data = JSON.parse(e.data);
            const event: WorkflowEvent = {
                type: 'task_update',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);

            // Update tasks list
            if (data.task_id) {
                setTasks(prev => {
                    const existing = prev.find(t => t.id === data.task_id);
                    if (existing) {
                        return prev.map(t =>
                            t.id === data.task_id
                                ? {
                                    ...t,
                                    description: data.description || t.description,
                                    status: data.status as any,
                                    result: data.result,
                                    owner: data.owner || t.owner
                                }
                                : t
                        );
                    } else {
                        return [...prev, {
                            id: data.task_id!,
                            description: data.description || `Task ${data.task_id}`,
                            status: data.status as any || 'pending',
                            owner: data.owner || 'SYSTEM',
                            result: data.result
                        }];
                    }
                });
            }
        });

        // Handle success events - clear thinking indicator
        eventSource.addEventListener('success', (e) => {
            const data = JSON.parse(e.data);
            const event: WorkflowEvent = {
                type: 'success',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);

            // Clear thinking state
            setThinkingAgent(null);
        });

        // Handle notifications
        eventSource.addEventListener('notification', (e) => {
            const data = JSON.parse(e.data);
            const event: WorkflowEvent = {
                type: 'notification',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);
        });

        // Handle logs
        eventSource.addEventListener('log', (e) => {
            const data = JSON.parse(e.data);
            const event: WorkflowEvent = {
                type: 'log',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);
        });

        // Handle completion
        eventSource.addEventListener('workflow_complete', (e) => {
            const data = JSON.parse(e.data);
            const event: WorkflowEvent = {
                type: 'workflow_complete',
                data: data,
                timestamp: new Date().toISOString()
            };
            setEvents(prev => [...prev, event]);
            setWorkflowStatus('completed');
            setIsRunning(false);
            setProgress(100);
            setThinkingAgent(null);
            toast.success('Workflow completed successfully!', { icon: '🎉' });
            eventSource.close();
        });

        // Handle errors
        eventSource.addEventListener('error', (e: any) => {
            try {
                const data = e.data ? JSON.parse(e.data) : { agent: 'SYSTEM', message: 'Unknown error' };
                const event: WorkflowEvent = {
                    type: 'error',
                    data: data,
                    timestamp: new Date().toISOString()
                };
                setEvents(prev => [...prev, event]);
            } catch (err) {
                // Parsing failed, create basic error event
                const event: WorkflowEvent = {
                    type: 'error',
                    data: { agent: 'SYSTEM', message: 'Connection error' },
                    timestamp: new Date().toISOString()
                };
                setEvents(prev => [...prev, event]);
            }
            setWorkflowStatus('error');
            setIsRunning(false);
            setThinkingAgent(null);
            toast.error('Workflow failed');
            eventSource.close();
        });

        // Connection opened
        eventSource.onopen = () => {
            console.log('SSE connection established');
        };

        // Connection error
        eventSource.onerror = (error) => {
            console.error('SSE error:', error);
            if (eventSource.readyState === EventSource.CLOSED) {
                setIsRunning(false);
            }
        };

        // Update progress based on tasks
        const progressInterval = setInterval(() => {
            setTasks(currentTasks => {
                if (currentTasks.length > 0) {
                    const completed = currentTasks.filter(t => t.status === 'completed').length;
                    const newProgress = (completed / currentTasks.length) * 100;
                    setProgress(newProgress);
                }
                return currentTasks;
            });
        }, 500);

        // Cleanup interval when workflow stops
        return () => clearInterval(progressInterval);
    };

    // Stop workflow
    const stopWorkflow = () => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }
        setIsRunning(false);
        setWorkflowStatus('stopped');
        toast('Workflow stopped', { icon: '⏹️' });
    };

    // Get icon for event type
    const getEventIcon = (type: string) => {
        switch (type) {
            case 'agent_message': return '🤖';
            case 'llm_call': return '🔗';
            case 'tool_execution': return '🔧';
            case 'routing': return '🔄';
            case 'task_update': return '📋';
            case 'success': return '✅';
            case 'notification': return '📧';
            case 'workflow_start': return '🚀';
            case 'workflow_complete': return '🎉';
            case 'error': return '❌';
            default: return '📝';
        }
    };

    // Get agent color
    const getAgentColor = (agent?: string) => {
        if (!agent) return 'text-gray-600';
        const agentUpper = agent.toUpperCase();
        if (agentUpper.includes('ORCHESTRATOR')) return 'text-purple-600';
        if (agentUpper.includes('ADVISOR')) return 'text-blue-600';
        if (agentUpper.includes('OPERATIONS')) return 'text-orange-600';
        if (agentUpper.includes('ROUTING')) return 'text-green-600';
        return 'text-gray-600';
    };

    // Get task status icon
    const getTaskIcon = (status: string) => {
        switch (status) {
            case 'completed': return <CheckCircle className="text-green-500" size={20} />;
            case 'in_progress': return <Loader className="text-blue-500 animate-spin" size={20} />;
            case 'failed': return <Circle className="text-red-500" size={20} />;
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

    // Get filtered events for display
    const displayEvents = events.filter(shouldDisplayEvent);

    return (
        <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <Brain className="text-purple-600" size={32} />
                        <div>
                            <h1 className="text-2xl font-bold text-gray-800">Agentic Workflow System</h1>
                            <p className="text-sm text-gray-500">Multi-Agent LLM-Powered Automation</p>
                        </div>
                    </div>

                    <div className="flex items-center space-x-4">
                        <div className={`px-3 py-1 rounded-full text-sm font-medium ${workflowStatus === 'running' ? 'bg-blue-100 text-blue-700' :
                            workflowStatus === 'completed' ? 'bg-green-100 text-green-700' :
                                workflowStatus === 'error' ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                            }`}>
                            {workflowStatus === 'running' ? '🔄 Running' :
                                workflowStatus === 'completed' ? '✅ Completed' :
                                    workflowStatus === 'error' ? '❌ Error' :
                                        '⚪ Idle'}
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="p-6">
                {/* Control Panel */}
                <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
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
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100"
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
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:bg-gray-100"
                            />
                        </div>

                        <div className="flex items-end">
                            {!isRunning ? (
                                <button
                                    onClick={startWorkflow}
                                    className="w-full px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center space-x-2"
                                >
                                    <Play size={20} />
                                    <span>Start Workflow</span>
                                </button>
                            ) : (
                                <button
                                    onClick={stopWorkflow}
                                    className="w-full px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center space-x-2"
                                >
                                    <Square size={20} />
                                    <span>Stop Workflow</span>
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Progress Bar */}
                    {isRunning && (
                        <div className="mt-4">
                            <div className="flex justify-between text-sm text-gray-600 mb-2">
                                <span>Progress</span>
                                <span>{Math.round(progress)}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                                <motion.div
                                    className="bg-purple-600 h-2 rounded-full"
                                    initial={{ width: 0 }}
                                    animate={{ width: `${progress}%` }}
                                    transition={{ duration: 0.3 }}
                                />
                            </div>
                        </div>
                    )}
                </div>

                {/* Two Column Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Tasks Panel */}
                    <div className="bg-white rounded-xl shadow-lg p-6">
                        <h2 className="text-lg font-semibold mb-4 flex items-center">
                            <Activity className="mr-2 text-orange-600" size={20} />
                            Tasks ({tasks.filter(t => t.status === 'completed').length}/{tasks.length})
                        </h2>

                        <div className="space-y-3 max-h-[600px] overflow-y-auto">
                            {tasks.length === 0 ? (
                                <div className="text-center text-gray-400 py-8">
                                    <Circle size={48} className="mx-auto mb-3 opacity-50" />
                                    <p>No tasks yet</p>
                                    <p className="text-sm">Start a workflow to see tasks</p>
                                </div>
                            ) : (
                                <AnimatePresence>
                                    {tasks.map((task, index) => (
                                        <motion.div
                                            key={task.id}
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: index * 0.1 }}
                                            className={`p-3 border rounded-lg ${task.status === 'completed' ? 'bg-green-50 border-green-200' :
                                                task.status === 'in_progress' ? 'bg-blue-50 border-blue-200' :
                                                    'bg-gray-50 border-gray-200'
                                                }`}
                                        >
                                            <div className="flex items-start space-x-3">
                                                <div className="mt-0.5">
                                                    {getTaskIcon(task.status)}
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <p className="text-sm font-medium text-gray-800 mb-1">
                                                        {task.description}
                                                    </p>
                                                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                                                        <span className="px-2 py-0.5 bg-white rounded">
                                                            {task.owner.replace('_', ' ')}
                                                        </span>
                                                        <span>{task.status}</span>
                                                    </div>
                                                    {task.result && (
                                                        <p className="mt-2 text-xs text-gray-600 italic">
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
                    <div className="lg:col-span-2 bg-white rounded-xl shadow-lg p-6">
                        <h2 className="text-lg font-semibold mb-4 flex items-center">
                            <Users className="mr-2 text-blue-600" size={20} />
                            Live Event Stream
                        </h2>

                        <div className="space-y-2 max-h-[600px] overflow-y-auto bg-gray-50 rounded-lg p-4">
                            {displayEvents.length === 0 && !thinkingAgent ? (
                                <div className="text-center text-gray-400 py-12">
                                    <Activity size={48} className="mx-auto mb-3 opacity-50" />
                                    <p>No activity yet</p>
                                    <p className="text-sm">Start a workflow to see agent communication</p>
                                </div>
                            ) : (
                                <AnimatePresence>
                                    {displayEvents.map((event, index) => (
                                        <motion.div
                                            key={index}
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ duration: 0.2 }}
                                            className="bg-white border border-gray-200 rounded-lg p-3 hover:shadow-md transition-shadow"
                                        >
                                            <div className="flex items-start space-x-3">
                                                <span className="text-2xl">{getEventIcon(event.type)}</span>
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center justify-between mb-1">
                                                        <span className={`text-sm font-semibold ${getAgentColor(event.data?.agent)}`}>
                                                            {event.data?.agent?.replace('_AGENT', '').replace('_', ' ') || 'System'}
                                                        </span>
                                                        <span className="text-xs text-gray-400">
                                                            {new Date(event.timestamp).toLocaleTimeString()}
                                                        </span>
                                                    </div>
                                                    <p className="text-sm text-gray-700">
                                                        {event.data?.message || 'Processing...'}
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
                                            className="bg-blue-50 border border-blue-200 rounded-lg p-3"
                                        >
                                            <div className="flex items-start space-x-3">
                                                <Brain className="text-blue-500 animate-pulse" size={24} />
                                                <div className="flex-1">
                                                    <span className={`text-sm font-semibold ${getAgentColor(thinkingAgent)}`}>
                                                        {thinkingAgent.replace('_AGENT', '').replace('_', ' ')}
                                                    </span>
                                                    <div className="flex items-center space-x-1 mt-1">
                                                        <span className="text-sm text-gray-600">thinking</span>
                                                        <motion.span
                                                            animate={{ opacity: [0.4, 1, 0.4] }}
                                                            transition={{ duration: 1.5, repeat: Infinity }}
                                                            className="text-blue-500"
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
                    </div>
                </div>
            </main>
        </div>
    );
};

export default WorkflowPage;

