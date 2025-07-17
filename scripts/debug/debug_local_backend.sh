#!/bin/bash

echo "🔍 DEBUG: Starting local backend test..."

# Check current directory
echo "📁 Current directory: $(pwd)"

# Check if venv exists
echo "🔍 Checking virtual environments..."
if [ -d "/Users/scottgreff/Documents/AI-Chatbot/venv" ]; then
    echo "✅ Project venv exists: /Users/scottgreff/Documents/AI-Chatbot/venv"
else
    echo "❌ Project venv missing: /Users/scottgreff/Documents/AI-Chatbot/venv"
fi

if [ -d "/Users/scottgreff/Documents/venv" ]; then
    echo "✅ Global venv exists: /Users/scottgreff/Documents/venv"
else
    echo "❌ Global venv missing: /Users/scottgreff/Documents/venv"
fi

# Check if uvicorn is available in both venvs
echo "🔍 Checking uvicorn availability..."
if /Users/scottgreff/Documents/AI-Chatbot/venv/bin/python -c "import uvicorn; print('uvicorn available in project venv')" 2>/dev/null; then
    echo "✅ uvicorn available in project venv"
else
    echo "❌ uvicorn NOT available in project venv"
fi

if /Users/scottgreff/Documents/venv/bin/python -c "import uvicorn; print('uvicorn available in global venv')" 2>/dev/null; then
    echo "✅ uvicorn available in global venv"
else
    echo "❌ uvicorn NOT available in global venv"
fi

# Test backend startup
echo "🚀 Testing backend startup..."
PORT=8000
echo "🔧 Using port: $PORT"

# Kill any existing process on port 8000
echo "🛑 Killing existing process on port $PORT..."
lsof -ti:$PORT | xargs kill -9 2>/dev/null || echo "No process found on port $PORT"

# Try starting backend with project venv
echo "⚡ Starting backend with project venv..."
cd /Users/scottgreff/Documents/AI-Chatbot
export CT_METAL=1
export GPU_LAYERS=4
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=ai_chatbot
export DB_USER=postgres
export DB_PASSWORD=password1234
export MAX_NEW_TOKENS=50

# Start backend in background
nohup /Users/scottgreff/Documents/AI-Chatbot/venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT > debug_backend.log 2>&1 &
BACKEND_PID=$!
echo "📝 Backend PID: $BACKEND_PID"

# Wait and check
echo "⏳ Waiting for backend to start..."
for i in {1..15}; do
    echo "🔍 Attempt $i/15: Checking http://localhost:$PORT/test"
    if curl -s http://localhost:$PORT/test > /dev/null; then
        echo "✅ Backend started successfully!"
        echo "🌐 Backend URL: http://localhost:$PORT"
        echo "📝 PID: $BACKEND_PID"
        exit 0
    fi
    sleep 2
done

echo "❌ Backend failed to start"
echo "📋 Backend log (last 20 lines):"
tail -20 debug_backend.log 2>/dev/null || echo "No log file found"

# Kill the process
kill $BACKEND_PID 2>/dev/null || true
exit 1 