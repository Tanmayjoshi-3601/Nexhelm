/**
 * Main App Component with Routing
 * Separates Opportunity Detection and Agentic Workflow systems
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { Brain, TrendingUp, Home, Database } from 'lucide-react';

// Import pages
import OpportunityDetectionPage from './pages/OpportunityDetectionPage';
import WorkflowPage from './pages/WorkflowPage';
import SystemsPage from './pages/SystemsPage';

// Navigation component
const Navigation: React.FC = () => {
    const location = useLocation();

    const isActive = (path: string) => {
        return location.pathname === path;
    };

    return (
        <nav className="bg-white border-b border-gray-200 shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex">
                        {/* Logo */}
                        <div className="flex-shrink-0 flex items-center">
                            <Home className="h-8 w-8 text-blue-600" />
                            <span className="ml-2 text-xl font-bold text-gray-900">Nexhelm AI</span>
                        </div>

                        {/* Navigation Links */}
                        <div className="ml-10 flex items-center space-x-4">
                            <Link
                                to="/"
                                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-2 ${isActive('/')
                                    ? 'bg-blue-100 text-blue-700'
                                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                                    }`}
                            >
                                <TrendingUp size={18} />
                                <span>Opportunity Detection</span>
                            </Link>

                            <Link
                                to="/workflow"
                                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-2 ${isActive('/workflow')
                                    ? 'bg-purple-100 text-purple-700'
                                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                                    }`}
                            >
                                <Brain size={18} />
                                <span>Agentic Workflow</span>
                            </Link>

                            <Link
                                to="/systems"
                                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center space-x-2 ${isActive('/systems')
                                    ? 'bg-green-100 text-green-700'
                                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                                    }`}
                            >
                                <Database size={18} />
                                <span>Backend Systems</span>
                            </Link>
                        </div>
                    </div>

                    {/* Right side info */}
                    <div className="flex items-center">
                        <div className="text-sm text-gray-500">
                            Multi-Agent AI System
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
};

// Main App with routing
const App: React.FC = () => {
    return (
        <Router>
            <div className="min-h-screen bg-gray-50">
                {/* Toast notifications (global) */}
                <Toaster position="top-right" />

                {/* Navigation */}
                <Navigation />

                {/* Routes */}
                <Routes>
                    <Route path="/" element={<OpportunityDetectionPage />} />
                    <Route path="/workflow" element={<WorkflowPage />} />
                    <Route path="/systems" element={<SystemsPage />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;

