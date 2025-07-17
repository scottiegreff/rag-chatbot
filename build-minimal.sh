#!/bin/bash

# Build minimal backend image
echo "🔨 Building minimal backend image..."

# Build the minimal image
docker build \
    -f Dockerfile.backend.minimal \
    -t ai-chatbot-backend:minimal \
    --target runtime \
    .

# Show image size comparison
echo ""
echo "📊 Image size comparison:"
echo "Current backend image:"
docker images | grep ai-chatbot-backend

echo ""
echo "✅ Minimal backend image built successfully!"
echo "Use 'docker-compose -f docker-compose.yml -f docker-compose.minimal.yml up -d' to run with minimal image" 