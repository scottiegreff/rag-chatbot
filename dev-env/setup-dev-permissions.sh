#!/bin/bash

# Development Environment Setup Script
# Run this as root or with sudo to set up proper permissions

set -e

echo "🔧 Setting up development permissions..."

# Get the username from the current user or default to ec2-user
DEV_USER=${1:-ec2-user}

echo "📝 Setting up user: $DEV_USER"

# Create user if it doesn't exist
if ! id "$DEV_USER" &>/dev/null; then
    echo "👤 Creating user $DEV_USER..."
    useradd -m -s /bin/bash "$DEV_USER"
fi

# Add user to docker group
echo "🐳 Adding $DEV_USER to docker group..."
usermod -aG docker "$DEV_USER"

# Set up project directory permissions
PROJECT_DIR="/opt/ai-chatbot"
if [ -d "$PROJECT_DIR" ]; then
    echo "📁 Setting permissions for $PROJECT_DIR..."
    chown -R "$DEV_USER:$DEV_USER" "$PROJECT_DIR"
    chmod -R 755 "$PROJECT_DIR"
    chmod -R u+w "$PROJECT_DIR"
fi

# Create logs directory with proper permissions
LOGS_DIR="/opt/ai-chatbot/logs"
if [ ! -d "$LOGS_DIR" ]; then
    echo "📝 Creating logs directory..."
    mkdir -p "$LOGS_DIR"
fi
chown -R "$DEV_USER:$DEV_USER" "$LOGS_DIR"
chmod -R 755 "$LOGS_DIR"

# Set up Docker socket permissions (if needed)
if [ -e /var/run/docker.sock ]; then
    echo "🔧 Setting Docker socket permissions..."
    chmod 666 /var/run/docker.sock
fi

echo "✅ Development permissions setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Switch to user: sudo su - $DEV_USER"
echo "2. Test Docker: docker ps"
echo "3. Navigate to project: cd /opt/ai-chatbot"
echo "4. Run containers: docker-compose up -d"
echo ""
echo "🔐 Note: You may need to log out and back in for group changes to take effect" 