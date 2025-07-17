# Terraform Infrastructure Improvements

## 🎯 Overview
This document outlines the improvements made to the AI Chatbot Terraform infrastructure to ensure a clean, automated deployment with no port conflicts or manual dependencies.

## ✅ Issues Fixed

### 1. **Port Conflicts Resolved**
- **Problem**: Flask test server and Docker backend both tried to use port 8010
- **Solution**: 
  - Health server now runs on port 8081 (different from main app)
  - Proper port cleanup before starting Docker containers
  - Port conflict detection and resolution

### 2. **Dependencies Fully Automated**
- **Problem**: Manual installation of Python, Docker, Docker Compose
- **Solution**:
  - Specific Python 3.9 installation with alternatives
  - Latest Docker Compose installation via GitHub API
  - All dependencies installed automatically in user_data script

### 3. **Improved Startup Sequence**
- **Problem**: Race conditions and unclear startup process
- **Solution**:
  - Structured startup script with proper error handling
  - Health check endpoints for monitoring
  - Service readiness detection
  - Comprehensive logging

### 4. **Configuration Management**
- **Problem**: Hardcoded values and inflexible configuration
- **Solution**:
  - Added variables for ports, Python version, Git repository
  - Configurable desired capacity (default: 1 instance)
  - Environment-specific settings

## 🚀 New Features

### 1. **Automated Cleanup Script** (`cleanup_terraform.sh`)
- Comprehensive infrastructure cleanup
- Orphaned resource detection and removal
- Interactive confirmation prompts
- Colored output for better UX

### 2. **Fresh Deployment Script** (`deploy_fresh.sh`)
- End-to-end deployment automation
- Infrastructure validation
- Deployment monitoring
- Post-deployment information

### 3. **Enhanced User Data Script**
- Port conflict detection and resolution
- Service readiness monitoring
- Proper Docker Compose management
- Comprehensive logging

## 📋 Configuration Variables

| Variable | Description | Default | Type |
|----------|-------------|---------|------|
| `desired_capacity` | Number of EC2 instances | 1 | number |
| `app_port` | Application backend port | 8010 | number |
| `health_port` | Health check server port | 8081 | number |
| `git_repository` | Git repository URL | GitHub repo | string |
| `python_version` | Python version to install | 3.9 | string |

## 🔧 Usage

### Clean Deployment
```bash
# Run the fresh deployment script
./deploy_fresh.sh
```

### Manual Cleanup
```bash
# Run the cleanup script
./cleanup_terraform.sh
```

### Manual Deployment
```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply changes
terraform apply -auto-approve
```

## 📊 Infrastructure Components

### 1. **EC2 Instances**
- Auto Scaling Group with 1 instance (configurable)
- t3.medium instance type
- Private subnet placement
- SSM access for management

### 2. **Load Balancer**
- Application Load Balancer
- Health checks on `/api/database/health`
- Port 8010 target group
- Public access

### 3. **Database**
- RDS PostgreSQL instance
- Private subnet placement
- Multi-AZ deployment
- Automated backups

### 4. **Storage**
- EFS file system for persistent storage
- Mount targets in all availability zones
- NFS access from app servers

## 🔍 Monitoring and Debugging

### Health Checks
- **Health Server**: `http://localhost:8081/`
- **Main App**: `http://localhost:8010/`
- **Database Health**: `http://localhost:8010/api/database/health`

### Log Files
- **Deployment Log**: `/var/log/app_deployment.log`
- **Health Server Log**: `/var/log/health_server.log`
- **Docker Logs**: `sudo docker logs <container_name>`

### SSH Access
```bash
# Connect via SSM
aws ssm start-session --target <instance-id>

# Or via SSH (if key pair configured)
ssh -i your-key.pem ec2-user@<instance-ip>
```

## 🛡️ Security

### Security Groups
- **ALB**: HTTP/HTTPS from internet
- **App**: Port 8010 from ALB, SSH from specified CIDR
- **RDS**: PostgreSQL from app servers
- **EFS**: NFS from app servers

### IAM Roles
- SSM managed instance core policy
- Minimal required permissions

## 📈 Scaling

### Auto Scaling
- Minimum: 1 instance
- Maximum: 3 instances
- Desired: 1 instance (configurable)
- Health check grace period: 300 seconds

### Manual Scaling
```bash
# Scale to 2 instances
aws autoscaling set-desired-capacity --auto-scaling-group-name app-asg --desired-capacity 2

# Scale back to 1 instance
aws autoscaling set-desired-capacity --auto-scaling-group-name app-asg --desired-capacity 1
```

## 🔄 Updates and Maintenance

### Updating the Application
1. Push changes to the Git repository
2. Terminate EC2 instances (ASG will recreate them)
3. New instances will pull latest code automatically

### Infrastructure Updates
1. Modify Terraform configuration
2. Run `terraform plan` to review changes
3. Run `terraform apply` to apply changes

## 🚨 Troubleshooting

### Common Issues

1. **Port 8010 in use**
   - Check for existing processes: `sudo lsof -i :8010`
   - Kill conflicting processes: `sudo pkill -f test_server.py`

2. **Docker permission issues**
   - Add user to Docker group: `sudo usermod -a -G docker ec2-user`
   - Restart session or use: `newgrp docker`

3. **Container startup failures**
   - Check logs: `sudo docker logs ai-chatbot-backend`
   - Restart containers: `sudo docker-compose restart`

4. **Load balancer health check failures**
   - Verify backend is running: `curl http://localhost:8010/api/database/health`
   - Check security group rules
   - Verify target group configuration

### Debug Commands
```bash
# Check container status
sudo docker ps

# Check application logs
tail -f /var/log/app_deployment.log

# Test local endpoints
curl http://localhost:8010/
curl http://localhost:8081/

# Check system resources
df -h
free -h
top
```

## 📝 Notes

- The deployment takes 5-10 minutes to complete
- Model download may take additional time depending on network speed
- All logs are preserved for debugging
- Infrastructure is designed for production use with proper security
- Auto scaling ensures high availability 