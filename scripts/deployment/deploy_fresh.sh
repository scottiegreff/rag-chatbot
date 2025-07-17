#!/bin/bash
set -e

echo "🚀 Starting fresh AI Chatbot deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "main.tf" ]; then
    print_error "main.tf not found. Please run this script from the Terraform directory."
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    print_error "AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

print_step "Step 1: Cleanup existing infrastructure"
read -p "Do you want to cleanup existing infrastructure first? (yes/no): " cleanup_choice

if [ "$cleanup_choice" = "yes" ]; then
    if [ -f "cleanup_terraform.sh" ]; then
        print_status "Running cleanup script..."
        ./cleanup_terraform.sh
    else
        print_warning "Cleanup script not found. Running manual cleanup..."
        if [ -d ".terraform" ]; then
            terraform destroy -auto-approve || true
            rm -rf .terraform
            rm -f .terraform.lock.hcl
            rm -f terraform.tfstate*
        fi
    fi
else
    print_status "Skipping cleanup..."
fi

print_step "Step 2: Initialize Terraform"
print_status "Initializing Terraform..."
terraform init

print_step "Step 3: Validate Terraform configuration"
print_status "Validating configuration..."
terraform validate

print_step "Step 4: Plan deployment"
print_status "Creating deployment plan..."
terraform plan

print_step "Step 5: Deploy infrastructure"
read -p "Do you want to proceed with deployment? (yes/no): " deploy_choice

if [ "$deploy_choice" != "yes" ]; then
    print_warning "Deployment cancelled by user."
    exit 0
fi

print_status "Deploying infrastructure..."
terraform apply -auto-approve

if [ $? -eq 0 ]; then
    print_status "✅ Infrastructure deployed successfully!"
else
    print_error "❌ Infrastructure deployment failed!"
    exit 1
fi

print_step "Step 6: Get deployment information"
print_status "Getting deployment outputs..."

# Get the ALB DNS name
ALB_DNS=$(terraform output -raw alb_dns_name 2>/dev/null || echo "N/A")
RDS_ENDPOINT=$(terraform output -raw rds_endpoint 2>/dev/null || echo "N/A")

echo ""
print_status "🎉 Deployment completed successfully!"
echo ""
echo "📋 Deployment Information:"
echo "   Load Balancer URL: http://$ALB_DNS"
echo "   RDS Endpoint: $RDS_ENDPOINT"
echo ""
echo "⏳ The application will take 5-10 minutes to fully start up."
echo "   You can monitor the deployment by checking the EC2 instance logs."
echo ""
echo "🔍 To check deployment status:"
echo "   1. SSH into the EC2 instance"
echo "   2. Check logs: tail -f /var/log/app_deployment.log"
echo "   3. Check containers: sudo docker ps"
echo "   4. Test locally: curl http://localhost:8010/"
echo ""
echo "🌐 Once ready, access your chatbot at: http://$ALB_DNS" 