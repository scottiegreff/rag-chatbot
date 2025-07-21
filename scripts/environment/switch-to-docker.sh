#!/bin/bash

echo "🐳 Switching to DOCKER CPU setup..."

# Kill native backend
echo "🛑 Killing native backend..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start Docker backend (CPU mode)
echo "🐳 Starting Docker backend with CPU..."
docker-compose up backend -d

# Wait for backend to start
echo "⏳ Waiting for Docker backend to start..."
sleep 10

# Test the backend
if curl -s http://localhost:8000/test > /dev/null; then
    echo "✅ Docker backend started successfully!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"
    echo "💻 CPU: Docker container mode"
else
    echo "❌ Failed to start Docker backend"
    exit 1
fi 