#!/bin/bash

echo "📊 Current Setup Status"
echo "========================"

# Check if native backend is running
if lsof -i:8000 | grep -i python > /dev/null; then
    echo "🔧 Backend: Native (M1 GPU)"
    echo "⚡ GPU: Metal acceleration enabled"
    echo "🐍 Python: $(ps aux | grep uvicorn | grep -v grep | head -1 | awk '{print $11}')"
else
    echo "🔧 Backend: Not running natively"
fi

# Check if Docker backend is running
if docker ps | grep ai-chatbot-backend > /dev/null; then
    echo "🐳 Backend: Docker (CPU)"
    echo "💻 CPU: Container mode"
    echo "📦 Container: $(docker ps | grep ai-chatbot-backend | awk '{print $1}')"
else
    echo "🐳 Backend: Not running in Docker"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "🌐 Frontend: Running on http://localhost:3000"
else
    echo "🌐 Frontend: Not accessible"
fi

# Check database
if docker ps | grep ai-chatbot-postgres > /dev/null; then
    echo "🗄️ Database: PostgreSQL running in Docker"
else
    echo "🗄️ Database: PostgreSQL not running"
fi

# Check vector DB
if docker ps | grep ai-chatbot-weaviate > /dev/null; then
    echo "🔍 Vector DB: Weaviate running in Docker"
else
    echo "🔍 Vector DB: Weaviate not running"
fi

echo ""
echo "🚀 Quick Commands:"
echo "  ./switch-to-local.sh  - Switch to M1 GPU"
echo "  ./switch-to-docker.sh - Switch to Docker CPU"
echo "  ./status.sh           - Check current status" 