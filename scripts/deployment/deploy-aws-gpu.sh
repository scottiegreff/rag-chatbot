#!/bin/bash

# AWS GPU Deployment Script for AI Chatbot
# This script sets up a GPU-enabled AWS instance and deploys the chatbot

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTANCE_TYPE=${INSTANCE_TYPE:-"g4dn.xlarge"}  # GPU instance type
REGION=${REGION:-"us-east-1"}
KEY_NAME=${KEY_NAME:-"ai-chatbot-key"}
SECURITY_GROUP_NAME=${SECURITY_GROUP_NAME:-"ai-chatbot-sg"}
VOLUME_SIZE=${VOLUME_SIZE:-"50"}  # GB

echo -e "${BLUE}🚀 AWS GPU Deployment Script for AI Chatbot${NC}"
echo -e "${YELLOW}Instance Type: ${INSTANCE_TYPE}${NC}"
echo -e "${YELLOW}Region: ${REGION}${NC}"
echo ""

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is authenticated
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

print_status "AWS CLI is configured and authenticated"

# Create security group
print_status "Creating security group..."
aws ec2 create-security-group \
    --group-name "$SECURITY_GROUP_NAME" \
    --description "Security group for AI Chatbot" \
    --region "$REGION" || print_warning "Security group may already exist"

# Get security group ID
SG_ID=$(aws ec2 describe-security-groups \
    --group-names "$SECURITY_GROUP_NAME" \
    --region "$REGION" \
    --query 'SecurityGroups[0].GroupId' \
    --output text)

# Add security group rules
print_status "Configuring security group rules..."
aws ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 \
    --region "$REGION" || print_warning "SSH rule may already exist"

aws ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0 \
    --region "$REGION" || print_warning "HTTP rule may already exist"

aws ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0 \
    --region "$REGION" || print_warning "HTTPS rule may already exist"

aws ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" \
    --protocol tcp \
    --port 3000 \
    --cidr 0.0.0.0/0 \
    --region "$REGION" || print_warning "Frontend rule may already exist"

aws ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" \
    --protocol tcp \
    --port 8000 \
    --cidr 0.0.0.0/0 \
    --region "$REGION" || print_warning "Backend rule may already exist"

# Create or get key pair
print_status "Setting up key pair..."
aws ec2 create-key-pair \
    --key-name "$KEY_NAME" \
    --region "$REGION" \
    --query 'KeyMaterial' \
    --output text > "$KEY_NAME.pem" || print_warning "Key pair may already exist"

chmod 400 "$KEY_NAME.pem"
print_status "Key pair saved as $KEY_NAME.pem"

# Get latest Ubuntu AMI with GPU support
print_status "Finding latest Ubuntu AMI..."
AMI_ID=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*" "Name=state,Values=available" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text \
    --region "$REGION")

# Validate AMI ID
if [ "$AMI_ID" = "None" ] || [ -z "$AMI_ID" ]; then
    print_error "Failed to find a valid Ubuntu AMI. Trying alternative approach..."
    # Try a more specific filter
    AMI_ID=$(aws ec2 describe-images \
        --owners 099720109477 \
        --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-20231207" "Name=state,Values=available" \
        --query 'Images[0].ImageId' \
        --output text \
        --region "$REGION")
fi

if [ "$AMI_ID" = "None" ] || [ -z "$AMI_ID" ]; then
    print_error "Still cannot find a valid Ubuntu AMI. Please check your AWS region and permissions."
    exit 1
fi

print_status "Using AMI: $AMI_ID"

# Create user data script
cat > user-data.sh << 'EOF'
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
mkdir -p /opt/ai-chatbot
cd /opt/ai-chatbot

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
cat > /etc/systemd/system/ai-chatbot.service << 'SERVICE_EOF'
[Unit]
Description=AI Chatbot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/ai-chatbot
ExecStart=/usr/local/bin/docker-compose -f docker-compose.yml -f docker-compose.aws-gpu.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.yml -f docker-compose.aws-gpu.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
SERVICE_EOF

systemctl enable ai-chatbot.service
systemctl start ai-chatbot.service
EOF

# Launch instance
print_status "Launching GPU instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id "$AMI_ID" \
    --count 1 \
    --instance-type "$INSTANCE_TYPE" \
    --key-name "$KEY_NAME" \
    --security-group-ids "$SG_ID" \
    --block-device-mappings "[{\"DeviceName\":\"/dev/sda1\",\"Ebs\":{\"VolumeSize\":$VOLUME_SIZE,\"VolumeType\":\"gp3\"}}]" \
    --user-data file://user-data.sh \
    --region "$REGION" \
    --query 'Instances[0].InstanceId' \
    --output text)

print_status "Instance launched: $INSTANCE_ID"

# Wait for instance to be running
print_status "Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID" --region "$REGION"

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --region "$REGION" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

print_status "Instance is running!"
echo ""
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo ""
echo -e "${BLUE}Instance Details:${NC}"
echo -e "  Instance ID: ${YELLOW}$INSTANCE_ID${NC}"
echo -e "  Public IP: ${YELLOW}$PUBLIC_IP${NC}"
echo -e "  Instance Type: ${YELLOW}$INSTANCE_TYPE${NC}"
echo -e "  Region: ${YELLOW}$REGION${NC}"
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo -e "  Frontend: ${GREEN}http://$PUBLIC_IP:3000${NC}"
echo -e "  Backend API: ${GREEN}http://$PUBLIC_IP:8000${NC}"
echo -e "  Health Check: ${GREEN}http://$PUBLIC_IP:8000/test${NC}"
echo ""
echo -e "${BLUE}SSH Access:${NC}"
echo -e "  ssh -i $KEY_NAME.pem ubuntu@$PUBLIC_IP"
echo ""
echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo -e "  1. The instance is still starting up (may take 5-10 minutes)"
echo -e "  2. Download your model file to /opt/ai-chatbot/models/"
echo -e "  3. Check logs: docker-compose logs -f"
echo -e "  4. Monitor GPU usage: nvidia-smi"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo -e "  1. Wait for startup to complete"
echo -e "  2. SSH into the instance to check status"
echo -e "  3. Download your model file"
echo -e "  4. Test the application"
echo ""

# Save deployment info
cat > deployment-info.txt << EOF
AWS GPU Deployment Information
=============================

Instance ID: $INSTANCE_ID
Public IP: $PUBLIC_IP
Instance Type: $INSTANCE_TYPE
Region: $REGION
Key File: $KEY_NAME.pem

Access URLs:
- Frontend: http://$PUBLIC_IP:3000
- Backend API: http://$PUBLIC_IP:8000
- Health Check: http://$PUBLIC_IP:8000/test

SSH Access:
ssh -i $KEY_NAME.pem ubuntu@$PUBLIC_IP

Deployment Date: $(date)
EOF

print_status "Deployment information saved to deployment-info.txt" 