#!/bin/bash

# User data script for FCI Chatbot EC2 instance
# This script runs when the instance starts

set -e

# Update system
yum update -y

# Install Docker
yum install -y docker
systemctl start docker
systemctl enable docker

# Add ec2-user to docker group
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Git
yum install -y git

# Create application directory
mkdir -p /opt/${project_name}
cd /opt/${project_name}

# Clone the application (you'll need to replace with your actual repository)
# git clone https://github.com/yourusername/FCI-Chatbot.git .

# For now, we'll create a simple setup script
cat > setup.sh << 'EOF'
#!/bin/bash

# Create docker-compose.yml for production
cat > docker-compose.prod.yml << 'DOCKER_COMPOSE_EOF'
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: fci-chatbot-postgres
    environment:
      POSTGRES_DB: fci_chatbot
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-password1234}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./ecommerce_schema.sql:/docker-entrypoint-initdb.d/01-schema.sql:ro
      - ./ecommerce_dummy_data.sql:/docker-entrypoint-initdb.d/02-data.sql:ro
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Weaviate Vector Database
  weaviate:
    image: semitechnologies/weaviate:1.25.4
    container_name: fci-chatbot-weaviate
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'none'
      ENABLE_MODULES: ''
      ENABLE_GRPC: 'true'
      CLUSTER_HOSTNAME: 'node1'
    volumes:
      - weaviate_data:/var/lib/weaviate
    ports:
      - "8080:8080"
      - "50051:50051"
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:8080/v1/"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Backend API
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: fci-chatbot-backend
    environment:
      # Database Configuration
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: fci_chatbot
      DB_USER: postgres
      DB_PASSWORD: ${POSTGRES_PASSWORD:-password1234}
      
      # Weaviate Configuration
      WEAVIATE_URL: http://weaviate:8080
      
      # LLM Configuration
      MODEL_PATH: /models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
      MODEL_TYPE: llama
      GPU_LAYERS: 0
      CONTEXT_LENGTH: 4096
      
      # RAG Configuration
      ENABLE_RAG: true
      RAG_USE_CPU: true
      CHUNK_SIZE: 500
      OVERLAP: 50
      
      # API Configuration
      HOST: 0.0.0.0
      PORT: 8000
      DEBUG: false
      CORS_ORIGINS: "*"
      
      # Performance Configuration
      MAX_HISTORY_MESSAGES: 50
      RAG_CONTEXT_MESSAGES: 10
      ENABLE_INTERNET_SEARCH: false
      
      # Platform-specific optimizations
      CT_METAL: 0
      CT_CUDA: 0
      
      # HuggingFace Cache Configuration
      HF_HOME: /root/.cache/huggingface
      TRANSFORMERS_CACHE: /root/.cache/huggingface
      HF_DATASETS_CACHE: /root/.cache/huggingface
    volumes:
      - ./models:/models:ro
      - ./backend:/app/backend:ro
      - ./frontend:/app/frontend:ro
      - sentence_transformer_cache:/root/.cache/huggingface
      - llm_cache:/root/.cache/llama-cpp
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/database/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    depends_on:
      postgres:
        condition: service_healthy
      weaviate:
        condition: service_started
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local
  weaviate_data:
    driver: local
  sentence_transformer_cache:
    driver: local
  llm_cache:
    driver: local
DOCKER_COMPOSE_EOF

# Create environment file
cat > .env << 'ENV_EOF'
# Production Environment Configuration
POSTGRES_PASSWORD=your_secure_password_here
ENV_EOF

# Download the TinyLlama model if not present
mkdir -p models
if [ ! -f "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf" ]; then
    echo "Downloading TinyLlama model..."
    # You'll need to download this from HuggingFace or your preferred source
    # wget -O models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
fi

# Start the application
docker-compose -f docker-compose.prod.yml up -d

echo "FCI Chatbot setup complete!"
echo "Application will be available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
EOF

chmod +x setup.sh

# Create a systemd service for the application
cat > /etc/systemd/system/fci-chatbot.service << 'EOF'
[Unit]
Description=FCI Chatbot Application
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/${project_name}
ExecStart=/opt/${project_name}/setup.sh
ExecStop=/usr/local/bin/docker-compose -f /opt/${project_name}/docker-compose.prod.yml down

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
systemctl enable fci-chatbot.service
systemctl start fci-chatbot.service

# Create a simple health check script
cat > /opt/${project_name}/health_check.sh << 'EOF'
#!/bin/bash

# Check if the application is running
if curl -f http://localhost:8000/api/database/health > /dev/null 2>&1; then
    echo "Application is healthy"
    exit 0
else
    echo "Application is not responding"
    exit 1
fi
EOF

chmod +x /opt/${project_name}/health_check.sh

# Set up log rotation
cat > /etc/logrotate.d/fci-chatbot << 'EOF'
/opt/${project_name}/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 ec2-user ec2-user
}
EOF

echo "User data script completed successfully!" 