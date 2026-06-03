#!/bin/bash

# AlgoSentinel - Local Development Startup Script

echo "🚀 Starting AlgoSentinel Development Environment..."
echo ""

# Check if Redis is running
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️  Redis CLI not found. Make sure Redis is running on localhost:6379"
else
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running"
    else
        echo "❌ Redis is not running. Please start Redis:"
        echo "   brew services start redis  # macOS"
        echo "   sudo service redis-server start  # Linux"
        exit 1
    fi
fi

echo ""
echo "📦 Environment:"
echo "   Python: $(python3 --version)"
echo "   Node: $(node --version)"
echo "   NPM: $(npm --version)"
echo ""

# Start API
echo "🔧 Starting FastAPI Backend..."
cd api
python3 -m venv venv 2>/dev/null
source venv/bin/activate
pip install -q -r requirements.txt
python3 main.py &
API_PID=$!
echo "   API PID: $API_PID (http://localhost:8000)"

# Wait for API to start
sleep 2

cd ..

# Start Frontend
echo "⚙️  Starting React Frontend..."
cd frontend
npm install -q 2>/dev/null
npm run dev &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID (http://localhost:3000)"

cd ..

echo ""
echo "✅ Services are starting..."
echo ""
echo "📍 Access points:"
echo "   • Frontend:    http://localhost:3000"
echo "   • API:         http://localhost:8000"
echo "   • API Docs:    http://localhost:8000/docs"
echo "   • Redis:       localhost:6379"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait $API_PID $FRONTEND_PID
