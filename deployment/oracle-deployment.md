# Oracle Cloud Infrastructure (OCI) Deployment Guide

## Overview
This guide covers deploying the FCI Chatbot on Oracle Cloud Infrastructure with Apache Tomcat and WebLogic environments.

## Architecture Options

### Option 1: Standalone Python Service (Recommended)
Deploy the FastAPI backend as a standalone Python service running alongside your Java applications.

**Advantages:**
- No changes to existing Java applications
- Independent scaling and management
- Can use different Python versions and dependencies
- Easier debugging and maintenance

**Architecture:**
```
OCI Instance:
├── WebLogic/Tomcat (Port 8080) - Your existing Java apps
├── FastAPI Backend (Port 8000) - FCI Chatbot API
├── PostgreSQL Database (Port 5432)
└── Nginx Reverse Proxy (Port 80/443) - Routes traffic
```

### Option 2: Java Bridge Application
Create a Java application that bridges between WebLogic and your Python service.

### Option 3: Python Web Application
Convert your FastAPI app to run within Tomcat using Jython (not recommended due to performance).

## Recommended Deployment: Option 1

### 1. Server Requirements

**Minimum Specifications:**
- **CPU**: 4 cores (for LLM inference)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB+ (for models and database)
- **OS**: Oracle Linux 8 or Ubuntu 20.04+

**Recommended Specifications:**
- **CPU**: 8 cores
- **RAM**: 32GB
- **Storage**: 100GB SSD
- **GPU**: Optional (for faster LLM inference)

### 2. Installation Steps

#### Step 1: Prepare the OCI Instance
```bash
# Update system
sudo yum update -y  # Oracle Linux
# or
sudo apt update && sudo apt upgrade -y  # Ubuntu

# Install required packages
sudo yum install -y python3 python3-pip git curl wget
# or
sudo apt install -y python3 python3-pip git curl wget
```

#### Step 2: Install PostgreSQL
```bash
# Oracle Linux
sudo yum install -y postgresql postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Ubuntu
sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

#### Step 3: Setup Database
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE fci_chatbot;
CREATE USER fci_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE fci_chatbot TO fci_user;
\q

# Configure PostgreSQL for remote connections
sudo nano /var/lib/pgsql/data/postgresql.conf
# Add: listen_addresses = '*'

sudo nano /var/lib/pgsql/data/pg_hba.conf
# Add: host fci_chatbot fci_user 0.0.0.0/0 md5

sudo systemctl restart postgresql
```

#### Step 4: Deploy Application
```bash
# Clone your application
cd /opt
sudo git clone <your-repo-url> fci-chatbot
sudo chown -R $USER:$USER fci-chatbot
cd fci-chatbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install ctransformers weaviate-client sentence-transformers PyPDF2 python-docx

# Create application directories
mkdir -p /opt/fci-chatbot/models
mkdir -p /opt/fci-chatbot/weaviate_data
mkdir -p /opt/fci-chatbot/logs
```

#### Step 5: Configure Environment
```bash
# Copy and edit environment file
cp env_template.txt .env
nano .env
```

**Environment Configuration:**
```bash
# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=fci_chatbot
DB_USER=postgres
DB_PASSWORD=your_secure_password

# LLM Configuration
MODEL_PATH=/opt/fci-chatbot/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
MODEL_TYPE=llama
GPU_LAYERS=0
CONTEXT_LENGTH=2048

# RAG Configuration
WEAVIATE_URL=http://weaviate:8080
ENABLE_RAG=true
RAG_USE_CPU=true
CHUNK_SIZE=500
OVERLAP=50

# API Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
CORS_ORIGINS=*

# Performance Configuration
MAX_HISTORY_MESSAGES=50
RAG_CONTEXT_MESSAGES=10
ENABLE_INTERNET_SEARCH=false
```

#### Step 6: Setup Systemd Service
```bash
sudo nano /etc/systemd/system/fci-chatbot.service
```

**Service Configuration:**
```ini
[Unit]
Description=FCI Chatbot FastAPI Application
After=network.target postgresql.service

[Service]
Type=simple
User=fci-user
Group=fci-user
WorkingDirectory=/opt/fci-chatbot
Environment=PATH=/opt/fci-chatbot/venv/bin
ExecStart=/opt/fci-chatbot/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Create service user
sudo useradd -r -s /bin/false fci-user
sudo chown -R fci-user:fci-user /opt/fci-chatbot

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable fci-chatbot
sudo systemctl start fci-chatbot
```

#### Step 7: Configure Nginx Reverse Proxy
```bash
# Install Nginx
sudo yum install -y nginx  # Oracle Linux
# or
sudo apt install -y nginx  # Ubuntu

# Configure Nginx
sudo nano /etc/nginx/conf.d/fci-chatbot.conf
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    # Frontend static files
    location / {
        root /opt/fci-chatbot/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Handle streaming responses
        proxy_buffering off;
        proxy_cache off;
        
        # Timeout settings for long-running requests
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Static files
    location /static/ {
        alias /opt/fci-chatbot/frontend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Test and restart Nginx
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx
```

#### Step 8: Configure Firewall
```bash
# Oracle Linux
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# Ubuntu
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000
sudo ufw enable
```

### 3. Integration with WebLogic/Tomcat

#### Option A: Separate Ports (Recommended)
- WebLogic/Tomcat: Port 8080 (existing applications)
- FCI Chatbot: Port 8000 (new application)
- Nginx: Port 80 (routes traffic)

#### Option B: Subdomain Routing
```nginx
# WebLogic applications
server {
    listen 80;
    server_name app.your-domain.com;
    proxy_pass http://localhost:8080;
}

# FCI Chatbot
server {
    listen 80;
    server_name chatbot.your-domain.com;
    # ... FCI chatbot configuration
}
```

#### Option C: Path-based Routing
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # WebLogic applications
    location / {
        proxy_pass http://localhost:8080;
    }

    # FCI Chatbot
    location /chatbot/ {
        proxy_pass http://localhost:8000/;
    }
}
```

### 4. Monitoring and Logging

#### Setup Log Rotation
```bash
sudo nano /etc/logrotate.d/fci-chatbot
```

```conf
/opt/fci-chatbot/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 fci-user fci-user
    postrotate
        systemctl reload fci-chatbot
    endscript
}
```

#### Setup Monitoring
```bash
# Install monitoring tools
sudo yum install -y htop iotop  # Oracle Linux
# or
sudo apt install -y htop iotop  # Ubuntu

# Create monitoring script
nano /opt/fci-chatbot/monitor.sh
```

```bash
#!/bin/bash
# Monitor script for FCI Chatbot

echo "=== FCI Chatbot Status ==="
echo "Service Status:"
systemctl status fci-chatbot --no-pager

echo -e "\nMemory Usage:"
free -h

echo -e "\nDisk Usage:"
df -h

echo -e "\nRecent Logs:"
tail -20 /opt/fci-chatbot/logs/app.log
```

### 5. Security Considerations

#### SSL/TLS Configuration
```bash
# Install Certbot for Let's Encrypt
sudo yum install -y certbot python3-certbot-nginx  # Oracle Linux
# or
sudo apt install -y certbot python3-certbot-nginx  # Ubuntu

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com
```

#### Security Hardening
```bash
# Disable root SSH login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

# Configure fail2ban
sudo yum install -y fail2ban  # Oracle Linux
# or
sudo apt install -y fail2ban  # Ubuntu

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 6. Backup Strategy

#### Database Backup
```bash
# Create backup script
nano /opt/fci-chatbot/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -h localhost -U fci_user fci_chatbot > $BACKUP_DIR/db_backup_$DATE.sql

# Backup application data
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz /opt/fci-chatbot/weaviate_data /opt/fci-chatbot/models

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
# Make executable and add to crontab
chmod +x /opt/fci-chatbot/backup.sh
crontab -e
# Add: 0 2 * * * /opt/fci-chatbot/backup.sh
```

### 7. Troubleshooting

#### Common Issues

**1. Service won't start:**
```bash
# Check logs
sudo journalctl -u fci-chatbot -f

# Check permissions
ls -la /opt/fci-chatbot/
```

**2. Database connection issues:**
```bash
# Test database connection
psql -h localhost -U fci_user -d fci_chatbot

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

**3. Model loading issues:**
```bash
# Check model file exists
ls -la /opt/fci-chatbot/models/

# Check disk space
df -h
```

**4. Memory issues:**
```bash
# Monitor memory usage
htop

# Check if swap is needed
free -h
```

### 8. Performance Optimization

#### For Production
1. **Use larger models only if needed**
2. **Enable RAG only when required**
3. **Configure proper memory limits**
4. **Use SSD storage for database**
5. **Consider using Oracle Database instead of PostgreSQL**

#### Oracle Database Integration
If you want to use Oracle Database instead of PostgreSQL:

```bash
# Install Oracle Instant Client
sudo yum install -y oracle-instantclient-basic oracle-instantclient-devel

# Install cx_Oracle
pip install cx_Oracle

# Update database.py to use Oracle
```

## Next Steps

1. **Choose your deployment option** (recommended: Option 1)
2. **Prepare your OCI instance** with the required specifications
3. **Follow the installation steps** in order
4. **Test the deployment** thoroughly
5. **Configure monitoring and backups**
6. **Set up SSL certificates** for production

Would you like me to help you with any specific part of this deployment process? 