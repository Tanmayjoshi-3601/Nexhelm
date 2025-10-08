/**
 * Backend Systems Dashboard
 * Shows real-time state of all simulated backend systems
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';
import {
    Database,
    Users,
    FileText,
    Download,
    RefreshCw,
    CheckCircle,
    XCircle,
    Building
} from 'lucide-react';

// Backend URL
const BACKEND_URL = 'http://localhost:8002';

// TypeScript Interfaces
interface Account {
    account_number: string;
    client_id: string;
    account_type: string;
    status: string;
    created_at: string;
}

interface Client {
    client_id: string;
    name: string;
    age: number;
    email: string;
    income: number;
    existing_accounts: string[];
}

interface SystemsData {
    accounts: {
        total: number;
        data: Account[];
    };
    crm: {
        total: number;
        data: Client[];
    };
    documents: {
        total: number;
        data: { [clientId: string]: { [docType: string]: any } };
    };
}

const SystemsPage: React.FC = () => {
    const [systemsData, setSystemsData] = useState<SystemsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [autoRefresh, setAutoRefresh] = useState(false);
    const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

    // Fetch all systems data
    const fetchSystemsData = async () => {
        try {
            const response = await axios.get(`${BACKEND_URL}/api/workflow/systems/all`);
            setSystemsData(response.data);
            setLastUpdated(new Date());
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch systems data:', error);
            toast.error('Failed to load systems data');
            setLoading(false);
        }
    };

    // Auto-refresh effect
    useEffect(() => {
        fetchSystemsData();

        if (autoRefresh) {
            const interval = setInterval(fetchSystemsData, 5000); // Refresh every 5 seconds
            return () => clearInterval(interval);
        }
    }, [autoRefresh]);

    // Export data as JSON
    const exportData = () => {
        if (!systemsData) return;

        const dataStr = JSON.stringify(systemsData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `nexhelm_systems_${new Date().toISOString()}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        toast.success('📥 Systems data exported successfully!');
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <RefreshCw className="animate-spin mx-auto mb-4 text-purple-600" size={48} />
                    <p className="text-gray-600 text-lg">Loading systems data...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-6">
                    <div className="flex justify-between items-center">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-800 flex items-center space-x-3">
                                <Database className="text-purple-600" size={36} />
                                <span>Backend Systems Dashboard</span>
                            </h1>
                            <p className="text-gray-600 mt-2">
                                Real-time view of all simulated backend systems
                            </p>
                        </div>
                        <div className="flex items-center space-x-3">
                            <button
                                onClick={() => {
                                    setAutoRefresh(!autoRefresh);
                                    toast.success(autoRefresh ? '⏸️ Auto-refresh paused' : '▶️ Auto-refresh enabled');
                                }}
                                className={`px-4 py-2 rounded-xl font-medium transition-all flex items-center space-x-2 ${autoRefresh
                                        ? 'bg-green-500 text-white hover:bg-green-600'
                                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                    }`}
                            >
                                <RefreshCw className={autoRefresh ? 'animate-spin' : ''} size={18} />
                                <span>{autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}</span>
                            </button>
                            <button
                                onClick={fetchSystemsData}
                                className="px-4 py-2 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-all flex items-center space-x-2"
                            >
                                <RefreshCw size={18} />
                                <span>Refresh Now</span>
                            </button>
                            <button
                                onClick={exportData}
                                className="px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all flex items-center space-x-2"
                            >
                                <Download size={18} />
                                <span>Export JSON</span>
                            </button>
                        </div>
                    </div>
                    <p className="text-sm text-gray-500 mt-2">
                        Last updated: {lastUpdated.toLocaleTimeString()}
                    </p>
                </div>

                {/* Account System Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className="bg-white/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 shadow-lg mb-6"
                >
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-2xl font-bold text-gray-800 flex items-center space-x-2">
                            <Building className="text-blue-600" size={28} />
                            <span>Account System</span>
                        </h2>
                        <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold">
                            {systemsData?.accounts.total || 0} accounts
                        </span>
                    </div>

                    {systemsData?.accounts.data.length === 0 ? (
                        <p className="text-gray-500 text-center py-8">No accounts created yet</p>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="min-w-full">
                                <thead>
                                    <tr className="border-b border-gray-200">
                                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Account Number</th>
                                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Type</th>
                                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Client ID</th>
                                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
                                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Created At</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {systemsData?.accounts.data.map((account, index) => (
                                        <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                                            <td className="px-4 py-3 text-sm font-mono text-blue-600">{account.account_number}</td>
                                            <td className="px-4 py-3 text-sm capitalize">{account.account_type.replace('_', ' ')}</td>
                                            <td className="px-4 py-3 text-sm text-gray-600">{account.client_id}</td>
                                            <td className="px-4 py-3 text-sm">
                                                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${account.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                                                    }`}>
                                                    {account.status}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 text-sm text-gray-600">{account.created_at}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </motion.div>

                {/* CRM System Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: 0.1 }}
                    className="bg-white/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 shadow-lg mb-6"
                >
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-2xl font-bold text-gray-800 flex items-center space-x-2">
                            <Users className="text-purple-600" size={28} />
                            <span>CRM Database</span>
                        </h2>
                        <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-semibold">
                            {systemsData?.crm.total || 0} clients
                        </span>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="min-w-full">
                            <thead>
                                <tr className="border-b border-gray-200">
                                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Client ID</th>
                                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Name</th>
                                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Age</th>
                                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Email</th>
                                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Income</th>
                                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Existing Accounts</th>
                                </tr>
                            </thead>
                            <tbody>
                                {systemsData?.crm.data.map((client, index) => (
                                    <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                                        <td className="px-4 py-3 text-sm font-mono text-purple-600">{client.client_id}</td>
                                        <td className="px-4 py-3 text-sm font-semibold">{client.name}</td>
                                        <td className="px-4 py-3 text-sm">{client.age}</td>
                                        <td className="px-4 py-3 text-sm text-gray-600">{client.email}</td>
                                        <td className="px-4 py-3 text-sm font-semibold text-green-600">
                                            ${client.income.toLocaleString()}
                                        </td>
                                        <td className="px-4 py-3 text-sm">
                                            {client.existing_accounts.length === 0 ? (
                                                <span className="text-gray-400">None</span>
                                            ) : (
                                                <span className="text-gray-700">
                                                    {client.existing_accounts.join(', ')}
                                                </span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </motion.div>

                {/* Document Store Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: 0.2 }}
                    className="bg-white/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 shadow-lg"
                >
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-2xl font-bold text-gray-800 flex items-center space-x-2">
                            <FileText className="text-green-600" size={28} />
                            <span>Document Store</span>
                        </h2>
                        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
                            {systemsData?.documents.total || 0} documents
                        </span>
                    </div>

                    {systemsData?.documents.data && Object.entries(systemsData.documents.data).map(([clientId, docs]) => (
                        <div key={clientId} className="mb-6 last:mb-0">
                            <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center space-x-2">
                                <Users size={20} className="text-gray-600" />
                                <span>{clientId}</span>
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                                {Object.entries(docs).map(([docType, docData]: [string, any]) => (
                                    <div
                                        key={docType}
                                        className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                                    >
                                        <div className="flex items-start justify-between mb-2">
                                            <h4 className="font-semibold text-gray-800 text-sm capitalize">
                                                {docType.replace(/_/g, ' ')}
                                            </h4>
                                            {docData.status === 'valid' || docData.verified ? (
                                                <CheckCircle className="text-green-500" size={20} />
                                            ) : (
                                                <XCircle className="text-red-500" size={20} />
                                            )}
                                        </div>
                                        <div className="space-y-1">
                                            {Object.entries(docData).map(([key, value]: [string, any]) => (
                                                <p key={key} className="text-xs text-gray-600">
                                                    <span className="font-medium capitalize">{key.replace(/_/g, ' ')}:</span>{' '}
                                                    {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value)}
                                                </p>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </motion.div>
            </div>
        </div>
    );
};

export default SystemsPage;

