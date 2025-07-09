#!/bin/bash

echo "🚀 Switching to LOCAL M1 GPU setup..."

# Stop Docker backend (keep frontend, postgres, weaviate)
echo "🛑 Stopping Docker backend..."
docker-compose stop backend

# Kill any existing native backend
echo "🛑 Killing existing native backend..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start native backend with Metal acceleration
echo "⚡ Starting native backend with M1 Metal acceleration..."
source venv/bin/activate && \
export CT_METAL=1 && \
export GPU_LAYERS=4 && \
export DB_HOST=localhost && \
export DB_PORT=5433 && \
export DB_PASSWORD=password1234 && \
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Test the backend
if curl -s http://localhost:8000/test > /dev/null; then
    echo "✅ Native backend started successfully with Metal acceleration!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"
    echo "⚡ GPU: M1 Metal acceleration enabled"
else
    echo "❌ Failed to start native backend"
    exit 1
fi 