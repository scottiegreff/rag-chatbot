#!/bin/bash

# Script to check download progress of CodeLlama 34B model
echo "📥 Checking CodeLlama 34B download progress..."

DOWNLOAD_DIR="models/models--TheBloke--CodeLlama-34B-Instruct-GGUF"
TARGET_FILE="models/codellama-34b-instruct.Q4_K_M.gguf"

# Check if download directory exists
if [ ! -d "$DOWNLOAD_DIR" ]; then
    echo "❌ Download directory not found. Download may not have started."
    exit 1
fi

# Check current download size
echo "📊 Current download size:"
du -sh "$DOWNLOAD_DIR"

# Check if target file exists
if [ -f "$TARGET_FILE" ]; then
    echo "✅ Download complete! Model file found at: $TARGET_FILE"
    echo "📏 File size: $(du -h "$TARGET_FILE" | cut -f1)"
    echo "🚀 You can now run: ./switch_to_codellama_34b.sh"
else
    echo "⏳ Download in progress..."
    echo "📁 Checking download directory contents:"
    ls -la "$DOWNLOAD_DIR"/blobs/
    
    # Check if we can find the GGUF file in the cache
    GGUF_FILES=$(find "$DOWNLOAD_DIR" -name "*.gguf" 2>/dev/null)
    if [ -n "$GGUF_FILES" ]; then
        echo "✅ Found GGUF file in cache:"
        echo "$GGUF_FILES"
        echo "📏 Size: $(du -h "$GGUF_FILES" | cut -f1)"
    else
        echo "⏳ Still downloading... Please wait."
    fi
fi 