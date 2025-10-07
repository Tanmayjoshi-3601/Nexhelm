#!/bin/bash

# Nexhelm Agentic Workflow Installation Script
# Run this script to install all dependencies for the new workflow system

echo "🚀 Installing Nexhelm Agentic Workflow Dependencies..."
echo "======================================================"
echo ""

# Check if conda environment is active
if [[ "$CONDA_DEFAULT_ENV" != "nexhelm" ]]; then
    echo "⚠️  Please activate the nexhelm conda environment first:"
    echo "   conda activate nexhelm"
    echo ""
    exit 1
fi

echo "✅ Conda environment 'nexhelm' is active"
echo ""

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install sse-starlette==1.6.5
if [ $? -eq 0 ]; then
    echo "✅ Backend dependencies installed successfully"
else
    echo "❌ Failed to install backend dependencies"
    exit 1
fi
echo ""

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd ../frontend
npm install react-router-dom@^6.22.0
if [ $? -eq 0 ]; then
    echo "✅ Frontend dependencies installed successfully"
else
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi
echo ""

# Success message
echo "======================================================"
echo "🎉 Installation Complete!"
echo "======================================================"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Start Redis Server:"
echo "   redis-server"
echo ""
echo "2. Start Backend (in new terminal):"
echo "   conda activate nexhelm"
echo "   cd backend"
echo "   python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload"
echo ""
echo "3. Start Frontend (in new terminal):"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "4. Open browser:"
echo "   http://localhost:3000"
echo ""
echo "5. Navigate to 'Agentic Workflow' tab and start a workflow!"
echo ""
echo "📖 For more details, see: AGENTIC_WORKFLOW_SETUP.md"
echo ""

