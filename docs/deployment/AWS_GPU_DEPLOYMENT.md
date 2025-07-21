# 🚀 AWS GPU Deployment Guide for AI Chatbot

This guide will help you deploy your AI Chatbot to AWS with GPU acceleration for optimal performance.

## 📋 Prerequisites

### 1. AWS Account Setup
- AWS account with billing enabled
- AWS CLI installed and configured
- Appropriate permissions for EC2, IAM, and VPC

### 2. Local Requirements
- Docker and Docker Compose (for testing)
- Git
- SSH client

## 🎯 Recommended AWS Instance Types

| Instance Type | vCPU | RAM | GPU | GPU Memory | Cost/Hour* | Use Case |
|---------------|------|-----|-----|------------|------------|----------|
| `g4dn.xlarge` | 4 | 16GB | 1x T4 | 16GB | ~$0.50 | Development/Testing |
| `g5.xlarge` | 4 | 16GB | 1x A10G | 24GB | ~$1.00 | Production |
| `p3.2xlarge` | 8 | 61GB | 1x V100 | 16GB | ~$3.00 | High Performance |
| `p4d.24xlarge` | 96 | 400GB | 8x A100 | 320GB | ~$32.00 | Enterprise |

*Costs are approximate and vary by region

## 🚀 Quick Deployment

### Option 1: Automated Deployment Script

```bash
# Clone your repository
git clone https://github.com/scottiegreff/rag-chatbot.git
cd rag-chatbot

# Configure AWS CLI (if not already done)
aws configure

# Run the deployment script
./deploy-aws-gpu.sh
```

### Option 2: Manual Deployment

```bash
# 1. Launch GPU instance manually
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --count 1 \
    --instance-type g4dn.xlarge \
    --key-name your-key-name \
    --security-group-ids sg-xxxxxxxxx

# 2. SSH into instance and run setup
ssh -i your-key.pem ubuntu@your-instance-ip
```

## ⚙️ Configuration Files

### Environment Configuration (`env.aws-gpu`)
```bash
# GPU Configuration
CT_CUDA=1
GPU_LAYERS=35
CONTEXT_LENGTH=4096

# Performance Settings
MEMORY_LIMIT=12G
CPU_LIMIT=6.0
```

### Docker Compose Override (`docker-compose.aws-gpu.yml`)
```yaml
services:
  backend:
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
```

## 🔧 Manual Setup Steps

### 1. Launch GPU Instance
```bash
# Use AWS Console or CLI to launch a GPU instance
# Recommended: g4dn.xlarge or g5.xlarge
```

### 2. Install Dependencies
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install NVIDIA Docker runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Deploy Application
```bash
# Clone repository
git clone https://github.com/scottiegreff/rag-chatbot.git
cd rag-chatbot

# Download model file
mkdir -p models
# Download your model file to models/ directory

# Start with GPU configuration
docker-compose -f docker-compose.yml -f docker-compose.aws-gpu.yml up -d
```

## 🔍 Verification and Monitoring

### Check GPU Status
```bash
# Verify NVIDIA drivers
nvidia-smi

# Check Docker GPU access
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

### Monitor Application
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f backend

# Check GPU usage
watch -n 1 nvidia-smi
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/test

# API test
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the total revenue?", "session_id": "test"}'
```

## 🔒 Security Configuration

### Security Groups
- **SSH (22)**: Your IP only
- **HTTP (80)**: 0.0.0.0/0 (or specific IPs)
- **HTTPS (443)**: 0.0.0.0/0 (or specific IPs)
- **Frontend (3000)**: 0.0.0.0/0 (or specific IPs)
- **Backend (8000)**: 0.0.0.0/0 (or specific IPs)

### Environment Variables
```bash
# Production security
DEBUG=false
ENABLE_INTERNET_SEARCH=true
CORS_ORIGINS=https://yourdomain.com
```

## 📊 Performance Optimization

### GPU Memory Management
```bash
# Monitor GPU memory usage
nvidia-smi -l 1

# Adjust GPU layers based on available memory
GPU_LAYERS=35  # For 16GB GPU memory
GPU_LAYERS=50  # For 24GB GPU memory
```

### Resource Limits
```yaml
# docker-compose.aws-gpu.yml
deploy:
  resources:
    limits:
      memory: 12G
      cpus: 6.0
    reservations:
      memory: 8G
      cpus: 4.0
```

## 🚨 Troubleshooting

### Common Issues

#### 1. GPU Not Detected
```bash
# Check NVIDIA drivers
nvidia-smi

# Verify Docker GPU runtime
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

#### 2. Out of Memory
```bash
# Reduce GPU layers
GPU_LAYERS=20  # Instead of 35

# Increase swap space
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 3. Slow Performance
```bash
# Check CPU and memory usage
htop

# Monitor disk I/O
iotop

# Check network latency
ping google.com
```

### Log Analysis
```bash
# Backend logs
docker-compose logs backend

# GPU logs
dmesg | grep nvidia

# System logs
journalctl -u docker.service
```

## 💰 Cost Optimization

### Instance Scheduling
```bash
# Stop instance when not in use
aws ec2 stop-instances --instance-ids i-1234567890abcdef0

# Start instance when needed
aws ec2 start-instances --instance-ids i-1234567890abcdef0
```

### Spot Instances
```bash
# Use spot instances for cost savings (up to 90% discount)
# Modify deployment script to use spot instances
```

## 🔄 Updates and Maintenance

### Application Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.yml -f docker-compose.aws-gpu.yml down
docker-compose -f docker-compose.yml -f docker-compose.aws-gpu.yml up -d --build
```

### System Updates
```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Update Docker
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use AWS ECS/EKS for container orchestration
- Implement load balancer for multiple instances
- Use RDS for database scaling

### Vertical Scaling
- Upgrade instance type for more resources
- Add more GPU memory for larger models
- Increase storage for more data

## 🎯 Next Steps

1. **Deploy to Production**: Use the automated script
2. **Set up Monitoring**: Configure CloudWatch alerts
3. **Implement CI/CD**: Set up automated deployments
4. **Add SSL**: Configure HTTPS with Let's Encrypt
5. **Backup Strategy**: Set up automated backups
6. **Load Testing**: Test performance under load

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review Docker and AWS logs
- Monitor GPU usage and system resources
- Consider upgrading instance type if needed

---

**Happy Deploying! 🚀** 