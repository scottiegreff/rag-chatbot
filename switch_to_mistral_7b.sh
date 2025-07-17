#!/bin/bash

# Script to switch to Mistral 7B model (optimal for M1 Mac)
echo "🔄 Switching to Mistral 7B model (optimal for M1 Mac)..."

# Check if the model file exists
MODEL_PATH="models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
if [ ! -f "$MODEL_PATH" ]; then
    echo "❌ Model file not found at $MODEL_PATH"
    exit 1
fi

echo "✅ Model file found!"

# Stop the current backend
echo "🛑 Stopping current backend..."
pkill -f "uvicorn.*backend.main:app" || echo "No backend process found"

# Set environment variables for Mistral 7B (optimized for M1)
echo "🔧 Setting environment variables for Mistral 7B..."
export MODEL_PATH="models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
export MODEL_TYPE="llama"
export GPU_LAYERS="4"  # Good for M1 GPU memory
export MAX_NEW_TOKENS="1024"
export CONTEXT_LENGTH="4096"  # Standard for 7B models

# Start the backend with Mistral 7B
echo "🚀 Starting backend with Mistral 7B..."
echo "📊 Model: $MODEL_PATH"
echo "🔧 GPU Layers: $GPU_LAYERS"
echo "📏 Context Length: $CONTEXT_LENGTH"
echo "🎯 Max Tokens: $MAX_NEW_TOKENS"

# Start backend in background
source venv/bin/activate && \
export MAX_NEW_TOKENS=1024 && \
export CT_METAL=1 && \
export GPU_LAYERS=4 && \
export DB_HOST=localhost && \
export DB_PORT=5433 && \
export DB_NAME=ai_chatbot && \
export DB_USER=postgres && \
export DB_PASSWORD=password1234 && \
export WEAVIATE_URL=http://localhost:8080 && \
export MODEL_PATH="models/mistral-7b-instruct-v0.2.Q4_K_M.gguf" && \
export MODEL_TYPE="llama" && \
export CONTEXT_LENGTH="4096" && \
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8010 > logs/backend.log 2>&1 &

echo "✅ Backend started with Mistral 7B!"
echo "📝 Check logs with: tail -f logs/backend.log"
echo "🌐 Access the chatbot at: http://localhost:8010"
echo ""
echo "🎯 Mistral 7B Benefits for M1 Mac:"
echo "   • Excellent reasoning and coding capabilities"
echo "   • Fits comfortably in M1 GPU memory"
echo "   • Good response times"
echo "   • Much better than TinyLlama 1.1B" 