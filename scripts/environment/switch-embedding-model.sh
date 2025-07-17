#!/bin/bash

# Script to switch between different embedding models
# Usage: ./switch-embedding-model.sh [e5-small|e5-large|minilm]

set -e

MODEL_TYPE=${1:-e5-small}

echo "🔄 Switching to embedding model: $MODEL_TYPE"

case $MODEL_TYPE in
    "e5-small")
        EMBEDDING_MODEL="intfloat/e5-small"
        echo "✅ Using intfloat/e5-small (fast, 134MB)"
        ;;
    "e5-large")
        EMBEDDING_MODEL="intfloat/e5-large"
        echo "✅ Using intfloat/e5-large (accurate, 438MB)"
        ;;
    "minilm")
        EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
        echo "✅ Using all-MiniLM-L6-v2 (balanced, 80MB)"
        ;;
    *)
        echo "❌ Invalid model type. Use: e5-small, e5-large, or minilm"
        exit 1
        ;;
esac

# Update .env file
if [ -f .env ]; then
    # Check if EMBEDDING_MODEL already exists in .env
    if grep -q "^EMBEDDING_MODEL=" .env; then
        # Update existing line
        sed -i.bak "s/^EMBEDDING_MODEL=.*/EMBEDDING_MODEL=$EMBEDDING_MODEL/" .env
    else
        # Add new line after RAG Configuration section
        sed -i.bak "/# RAG Configuration/a\\
# Embedding model: intfloat/e5-small (fast, 134MB), intfloat/e5-large (accurate, 438MB), sentence-transformers/all-MiniLM-L6-v2 (balanced, 80MB)\\
EMBEDDING_MODEL=$EMBEDDING_MODEL" .env
    fi
    echo "✅ Updated .env file with EMBEDDING_MODEL=$EMBEDDING_MODEL"
else
    echo "⚠️  .env file not found. Please create it from env_template.txt"
fi

echo ""
echo "🔄 To apply changes, restart your backend:"
echo "   Local: ./quick-switch-local.sh"
echo "   Docker: ./quick-switch-docker.sh"
echo ""
echo "🧪 Test the new model: python test_embedding_models.py" 