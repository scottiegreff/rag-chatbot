# Docker Deployment Guide for AI Chatbot

## Overview

This guide covers deploying the AI Chatbot using Docker Compose across different environments:
- **Local Development**: M1 Mac with Metal acceleration
- **Cloud Production**: AWS, OCI, Azure, GCP VMs

## Prerequisites

### For All Environments
- Docker Desktop (for local) or Docker Engine (for cloud)
- Docker Compose
- At least 4GB RAM available
- Model files in `./models/` directory

### For M1 Mac Development
- Docker Desktop with Apple Silicon support
- macOS 12+ (for Metal acceleration)

### For Cloud VMs
- Linux VM with Docker Engine installed
- Minimum 4GB RAM, 2 vCPUs recommended
- 50GB+ storage for models and database

## Quick Start

### 1. Local Development (M1 Mac)

```bash
# Clone and setup
git clone <your-repo>
cd ai-chatbot

# Copy your model files to models/ directory
cp /path/to/your/models/* ./models/

# Start development environment
docker-compose --env-file env.m1-mac up --build
```

**Access your app:**
- Web UI: http://localhost:8010
- API: http://localhost:8010/api

### 2. Cloud Production

```bash
# On your cloud VM
git clone <your-repo>
cd ai-chatbot

# Copy model files
scp -r /path/to/models/* user@vm-ip:~/ai-chatbot/models/

# Start production environment
docker-compose --env-file env.cloud-vm -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Environment Configuration

### M1 Mac Development (`env.m1-mac`)
```bash
# Optimized for M1 Mac with Metal acceleration
CT_METAL=1
GPU_LAYERS=1
RAG_USE_CPU=true  # Use Metal for RAG
DEBUG=true
MEMORY_LIMIT=8G
```

### Cloud VM Production (`env.cloud-vm`)
```bash
# Optimized for cloud VMs (CPU-only)
CT_METAL=0
GPU_LAYERS=0
RAG_USE_CPU=true  # Force CPU for RAG
DEBUG=false
MEMORY_LIMIT=4G
```

## Deployment Commands

### Development (M1 Mac)
```bash
# Start development environment
docker-compose --env-file env.m1-mac up --build

# Start with hot reload
docker-compose --env-file env.m1-mac up --build

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Production (Cloud VMs)
```bash
# Start production environment
docker-compose --env-file env.cloud-vm -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Update and restart
docker-compose --env-file env.cloud-vm -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

## Platform-Specific Considerations

### M1 Mac Development

**Advantages:**
- Metal acceleration for faster inference
- Local development with hot reload
- No network latency

**Configuration:**
```bash
# Enable Metal acceleration
CT_METAL=1
GPU_LAYERS=1
RAG_USE_CPU=true
```

**Performance Tips:**
- Use smaller models for faster iteration
- Enable RAG with Metal for better performance
- Monitor memory usage with Activity Monitor

### Cloud VM Production

**Advantages:**
- Scalable infrastructure
- 24/7 availability
- Cost-effective for production

**Configuration:**
```bash
# CPU-only for maximum compatibility
CT_METAL=0
GPU_LAYERS=0
RAG_USE_CPU=true
```

**Resource Recommendations:**
- **Minimum**: 4GB RAM, 2 vCPUs
- **Recommended**: 8GB RAM, 4 vCPUs
- **High Performance**: 16GB RAM, 8 vCPUs

## Model Management

### Model Files
Place your GGUF model files in the `./models/` directory:
```
models/
├── tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
└── mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### Model Configuration
Update the model path in your environment file:
```bash
# For TinyLlama (faster, smaller)
MODEL_PATH=./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# For Mistral (better quality, larger)
MODEL_PATH=./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

## Database Management

### PostgreSQL Data
Database data is persisted in Docker volumes:
```bash
# View volume information
docker volume ls

# Backup database
docker exec ai-chatbot-postgres pg_dump -U postgres ai_chatbot > backup.sql

# Restore database
docker exec -i ai-chatbot-postgres psql -U postgres ai_chatbot < backup.sql
```

### Weaviate Data
Vector database is persisted in `weaviate_data` volume:
```bash
# Backup Weaviate
docker run --rm -v ai-chatbot_weaviate_data:/data -v $(pwd):/backup alpine tar czf /backup/weaviate_backup.tar.gz -C /data .

# Restore Weaviate
docker run --rm -v ai-chatbot_weaviate_data:/data -v $(pwd):/backup alpine tar xzf /backup/weaviate_backup.tar.gz -C /data
```

## Monitoring and Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Health Checks
```bash
# Check service status
docker-compose ps

# Test API endpoint
curl http://localhost:8010/test

# Check database connection
docker exec ai-chatbot-postgres pg_isready -U postgres
```

### Resource Monitoring
```bash
# Container resource usage
docker stats

# Disk usage
docker system df
```

## Troubleshooting

### Common Issues

**1. Model Loading Errors**
```bash
# Check model file exists
ls -la models/

# Check model file permissions
chmod 644 models/*.gguf

# Verify model path in environment
echo $MODEL_PATH
```

**2. Memory Issues**
```bash
# Check available memory
free -h

# Increase memory limit in environment file
MEMORY_LIMIT=8G
```

**3. Port Conflicts**
```bash
# Check port usage
lsof -i :8010
lsof -i :5432

# Use different ports
docker-compose up -p 8010  # Use port 8000instead
```

**4. Permission Issues**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod -R 755 .

# Fix Docker volume permissions
docker-compose down
sudo chown -R $USER:$USER ~/.docker/volumes/
```

### Performance Optimization

**For M1 Mac:**
```bash
# Enable Metal acceleration
CT_METAL=1
GPU_LAYERS=1

# Use smaller models for development
MODEL_PATH=./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

**For Cloud VMs:**
```bash
# CPU-only configuration
CT_METAL=0
GPU_LAYERS=0
RAG_USE_CPU=true

# Conservative resource limits
MEMORY_LIMIT=4G
CPU_LIMIT=2.0
```

## Security Considerations

### Production Security
```bash
# Use strong passwords
POSTGRES_PASSWORD=password1234

# Disable internet search in production
ENABLE_INTERNET_SEARCH=false

# Restrict CORS origins
CORS_ORIGINS=https://yourdomain.com
```

### Network Security
```bash
# Use internal networks
docker network create ai-internal

# Expose only necessary ports
ports:
  - "8010:8010"  # API only
```

## Backup and Recovery

### Automated Backup Script
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"

mkdir -p $BACKUP_DIR

# Backup database
docker exec ai-chatbot-postgres pg_dump -U postgres ai_chatbot > $BACKUP_DIR/db_$DATE.sql

# Backup Weaviate
docker run --rm -v ai-chatbot_weaviate_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/weaviate_$DATE.tar.gz -C /data .

# Clean old backups (keep 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### Recovery
```bash
# Restore database
docker exec -i ai-chatbot-postgres psql -U postgres ai_chatbot < backups/db_20231201_120000.sql

# Restore Weaviate
docker run --rm -v ai-chatbot_weaviate_data:/data -v $(pwd)/backups:/backup alpine tar xzf /backup/weaviate_20231201_120000.tar.gz -C /data
```

## Scaling Considerations

### Horizontal Scaling
For high-traffic deployments, consider:
- Load balancer (nginx, haproxy)
- Multiple backend instances
- Database clustering
- Redis for session management

### Vertical Scaling
Increase VM resources:
- More CPU cores
- More RAM
- SSD storage
- GPU instances (if available)

## Cost Optimization

### Cloud VM Sizing
- **Development**: 2 vCPU, 4GB RAM
- **Production**: 4 vCPU, 8GB RAM
- **High Traffic**: 8 vCPU, 16GB RAM

### Storage Optimization
- Use smaller models (TinyLlama vs Mistral)
- Regular cleanup of old data
- Compress backups
- Use object storage for models

## Next Steps

1. **Test locally** on M1 Mac with `env.m1-mac`
2. **Deploy to cloud** with `env.cloud-vm`
3. **Configure monitoring** and alerts
4. **Set up automated backups**
5. **Implement CI/CD** pipeline
6. **Add SSL certificates** for production

## Support

For issues specific to:
- **M1 Mac**: Check Metal acceleration and memory usage
- **Cloud VMs**: Verify resource limits and network connectivity
- **Docker**: Ensure Docker Engine is properly installed
- **Models**: Verify model files are compatible and accessible 