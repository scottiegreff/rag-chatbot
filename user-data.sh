#!/bin/bash
set -e

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install NVIDIA Docker runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list

apt-get update
apt-get install -y nvidia-docker2
systemctl restart docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Git
apt-get install -y git

# Create application directory
mkdir -p /opt/fci-chatbot
cd /opt/fci-chatbot

# Clone repository (replace with your actual repo)
git clone https://github.com/scottiegreff/rag-chatbot.git .

# Download model if not present
if [ ! -f "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf" ]; then
    mkdir -p models
    # Add model download command here
    echo "Please download the model file manually"
fi

# Start the application
docker-compose -f docker-compose.yml -f docker-compose.aws-gpu.yml up -d

# Create systemd service for auto-start
cat > /etc/systemd/system/fci-chatbot.service << 'SERVICE_EOF'
[Unit]
Description=FCI Chatbot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/fci-chatbot
ExecStart=/usr/local/bin/docker-compose -f docker-compose.yml -f docker-compose.aws-gpu.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.yml -f docker-compose.aws-gpu.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
SERVICE_EOF

systemctl enable fci-chatbot.service
systemctl start fci-chatbot.service
