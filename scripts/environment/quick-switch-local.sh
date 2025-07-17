#!/bin/bash

echo "🚀 Quick Switch to Local (M1 GPU) Environment..."

# Kill any existing backend processes
echo "🛑 Killing existing backend processes..."
pkill -f "uvicorn backend.main:app" 2>/dev/null || true

# Set environment variables for local development
echo "🔧 Setting environment variables..."
export WEAVIATE_URL=http://localhost:8080
export PORT=8000

# Start local backend
echo "⚡ Starting local backend..."
./switch-to-local.sh

echo "✅ Local environment ready!"
echo "🌐 Backend: http://localhost:8000"
echo "🔍 Test with: curl -s http://localhost:8000/test" 