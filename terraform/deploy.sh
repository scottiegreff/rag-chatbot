#!/bin/bash

# AI Chatbot AWS Deployment Script
# This script automates the initial deployment process

set -e

echo "🚀 Starting AI Chatbot AWS Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if Terraform is installed
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    # Check if SSH key exists
    if [ ! -f ~/.ssh/id_rsa ]; then
        print_warning "SSH key not found. Generating new key pair..."
        ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
        print_success "SSH key generated successfully"
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "All prerequisites met"
}

# Initialize Terraform
init_terraform() {
    print_status "Initializing Terraform..."
    
    if [ ! -d ".terraform" ]; then
        terraform init
        print_success "Terraform initialized"
    else
        print_status "Terraform already initialized"
    fi
}

# Plan Terraform deployment
plan_deployment() {
    print_status "Planning Terraform deployment..."
    
    terraform plan -out=tfplan
    
    print_success "Terraform plan created"
    print_warning "Review the plan above. Press Enter to continue or Ctrl+C to abort..."
    read -r
}

# Apply Terraform deployment
apply_deployment() {
    print_status "Applying Terraform deployment..."
    
    terraform apply tfplan
    
    print_success "Infrastructure deployed successfully"
}

# Get deployment outputs
get_outputs() {
    print_status "Getting deployment outputs..."
    
    echo ""
    echo "=== DEPLOYMENT OUTPUTS ==="
    echo ""
    
    # Get instance IP
    INSTANCE_IP=$(terraform output -raw instance_public_ip)
    echo "Instance Public IP: $INSTANCE_IP"
    
    # Get SSH command
    SSH_CMD=$(terraform output -raw ssh_command)
    echo "SSH Command: $SSH_CMD"
    
    # Get application URL
    APP_URL=$(terraform output -raw application_url)
    echo "Application URL: $APP_URL"
    
    # Get Terraform user credentials
    TF_USER=$(terraform output -raw terraform_user_name)
    echo "Terraform User: $TF_USER"
    
    echo ""
    echo "=== NEXT STEPS ==="
    echo "1. SSH into your instance: $SSH_CMD"
    echo "2. Deploy your application code"
    echo "3. Access your application at: $APP_URL"
    echo ""
    echo "=== SECURITY NOTES ==="
    echo "1. Update security groups to restrict SSH access"
    echo "2. Change default passwords"
    echo "3. Set up SSL/TLS for production"
    echo ""
}

# Main deployment function
main() {
    echo "=========================================="
    echo "AI Chatbot AWS Deployment"
    echo "=========================================="
    echo ""
    
    # Check if we're in the right directory
    if [ ! -f "main.tf" ]; then
        print_error "Please run this script from the terraform directory"
        exit 1
    fi
    
    # Run deployment steps
    check_prerequisites
    init_terraform
    plan_deployment
    apply_deployment
    get_outputs
    
    print_success "Deployment completed successfully!"
    echo ""
    print_status "Remember to:"
    echo "  - Secure your instance (restrict SSH access)"
    echo "  - Set up monitoring and backups"
    echo "  - Configure SSL/TLS for production use"
    echo "  - Set up CI/CD pipeline"
}

# Run main function
main "$@" 