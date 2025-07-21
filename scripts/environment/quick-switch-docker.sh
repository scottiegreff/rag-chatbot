#!/bin/bash

echo "🐳 Quick Switch to Docker (CPU) Environment..."

# Kill any existing backend processes
echo "🛑 Killing existing backend processes..."
pkill -f "uvicorn backend.main:app" 2>/dev/null || true

# Start Docker backend
echo "⚡ Starting Docker backend..."
./switch-to-docker.sh

echo "✅ Docker environment ready!"
echo "🌐 Backend: http://localhost:8000"
echo "🔍 Test with: curl -s http://localhost:8000/test" 