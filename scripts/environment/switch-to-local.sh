#!/bin/bash

echo "🚀 Switching to LOCAL M1 GPU setup..."

# Stop Docker backend (keep frontend, postgres, weaviate)
echo "🛑 Stopping Docker backend..."
docker-compose stop backend

# Wait a moment for Docker to fully stop
echo "⏳ Waiting for Docker backend to fully stop..."
sleep 3

# Get port from environment or default to 8000
PORT=${PORT:-8000}
echo "🔧 Using port: $PORT"

# Kill any existing native backend
echo "🛑 Killing existing native backend..."
lsof -ti:$PORT | xargs kill -9 2>/dev/null || true

# Double-check port is free
echo "🔍 Checking if port $PORT is available..."
if lsof -i:$PORT > /dev/null 2>&1; then
    echo "❌ Port $PORT is still in use. Attempting to force stop..."
    docker-compose down backend
    sleep 2
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Start native backend with Metal acceleration
echo "🟢 Ensuring Postgres and Weaviate containers are running..."
docker-compose up -d postgres weaviate
echo "⚡ Starting native backend with M1 Metal acceleration..."
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"
source "$PROJECT_ROOT/venv/bin/activate" && \
export CT_METAL=1 && \
export GPU_LAYERS=4 && \
export DB_HOST=localhost && \
export DB_PORT=5432 && \
export DB_NAME=ai_chatbot && \
export DB_USER=postgres && \
export DB_PASSWORD=password1234 && \
export MAX_NEW_TOKENS=50 && \
nohup "$PROJECT_ROOT/venv/bin/python" -m uvicorn backend.main:app --reload --host 0.0.0.0 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start (up to 60 seconds)
echo "⏳ Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:$PORT/test > /dev/null; then
        echo "✅ Native backend started successfully with Metal acceleration!"
        echo "🌐 Frontend: http://localhost:3000"
        echo "🔧 Backend: http://localhost:$PORT"
        echo "⚡ GPU: M1 Metal acceleration enabled"
        echo "📝 Backend PID: $BACKEND_PID"
        exit 0
    fi
    sleep 2
done
echo "❌ Failed to start native backend"
echo "📋 Backend log (last 20 lines):"
tail -20 backend.log 2>/dev/null || echo "No log file found"
exit 1 