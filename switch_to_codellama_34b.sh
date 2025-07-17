#!/bin/bash

# Script to switch to CodeLlama 34B model
echo "🔄 Switching to CodeLlama 34B model..."

# Check if the model file exists
MODEL_PATH="models/codellama-34b-instruct.Q4_K_M.gguf"
if [ ! -f "$MODEL_PATH" ]; then
    echo "❌ Model file not found at $MODEL_PATH"
    echo "📥 Checking download progress..."
    
    # Check if download is in progress
    if [ -d "models/models--TheBloke--CodeLlama-34B-Instruct-GGUF" ]; then
        echo "📥 Download in progress. Current size:"
        du -sh models/models--TheBloke--CodeLlama-34B-Instruct-GGUF/
        echo "⏳ Please wait for download to complete..."
        exit 1
    else
        echo "❌ Download directory not found. Please start the download first."
        exit 1
    fi
fi

echo "✅ Model file found!"

# Stop the current backend
echo "🛑 Stopping current backend..."
pkill -f "uvicorn.*backend.main:app" || echo "No backend process found"

# Set environment variables for CodeLlama 34B
echo "🔧 Setting environment variables for CodeLlama 34B..."
export MODEL_PATH="models/codellama-34b-instruct.Q4_K_M.gguf"
export MODEL_TYPE="llama"
export GPU_LAYERS="4"  # Adjust based on your GPU memory
export MAX_NEW_TOKENS="1024"
export CONTEXT_LENGTH="8192"  # Larger context for 34B model

# Start the backend with new model
echo "🚀 Starting backend with CodeLlama 34B..."
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
export MODEL_PATH="models/codellama-34b-instruct.Q4_K_M.gguf" && \
export MODEL_TYPE="llama" && \
export CONTEXT_LENGTH="8192" && \
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8010 > logs/backend.log 2>&1 &

echo "✅ Backend started with CodeLlama 34B!"
echo "📝 Check logs with: tail -f logs/backend.log"
echo "🌐 Access the chatbot at: http://localhost:8010" 