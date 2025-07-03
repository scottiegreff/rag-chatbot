#!/bin/bash
set -e

echo "🧹 Starting Terraform infrastructure cleanup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if Terraform is initialized
if [ ! -d ".terraform" ]; then
    print_warning "Terraform not initialized. This is normal for a fresh deployment."
    print_status "Proceeding with cleanup checks..."
else
    print_status "Terraform is initialized. Checking current state..."
fi

# Check if we're in the right directory
if [ ! -f "main.tf" ]; then
    print_error "main.tf not found. Please run this script from the Terraform directory."
    exit 1
fi

print_status "Checking current Terraform state..."

# List current resources (if Terraform is initialized)
if [ -d ".terraform" ]; then
    print_status "Current resources:"
    terraform state list 2>/dev/null || print_warning "No Terraform state found or no resources exist."
else
    print_status "Skipping Terraform state check (not initialized)."
fi

# Ask for confirmation
echo ""
read -p "Are you sure you want to destroy all infrastructure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    print_warning "Cleanup cancelled by user."
    exit 0
fi

print_status "Starting Terraform destroy..."

# Only run terraform destroy if Terraform is initialized
if [ -d ".terraform" ]; then
    # Destroy with auto-approve
    terraform destroy -auto-approve

    if [ $? -eq 0 ]; then
        print_status "✅ Terraform destroy completed successfully!"
    else
        print_error "❌ Terraform destroy failed!"
        exit 1
    fi
else
    print_status "Skipping Terraform destroy (not initialized)."
fi

# Clean up Terraform files
print_status "Cleaning up Terraform files..."
rm -rf .terraform
rm -f .terraform.lock.hcl
rm -f terraform.tfstate*
rm -f .terraform.tfstate*

print_status "Checking for orphaned resources..."

# Check for orphaned EBS volumes
print_status "Checking for orphaned EBS volumes..."
orphaned_volumes=$(aws ec2 describe-volumes --filters "Name=status,Values=available" --query 'Volumes[?Tags[?Key==`Name` && contains(Value, `app-server`)]].[VolumeId]' --output text 2>/dev/null || echo "")

if [ ! -z "$orphaned_volumes" ]; then
    print_warning "Found orphaned EBS volumes: $orphaned_volumes"
    read -p "Delete orphaned EBS volumes? (yes/no): " delete_volumes
    
    if [ "$delete_volumes" = "yes" ]; then
        for volume in $orphaned_volumes; do
            print_status "Deleting volume: $volume"
            aws ec2 delete-volume --volume-id $volume
        done
    fi
fi

# Check for orphaned security groups
print_status "Checking for orphaned security groups..."
orphaned_sgs=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=app-sg,alb-sg,rds-sg,efs-sg" --query 'SecurityGroups[?length(Attachments)==`0`].[GroupId]' --output text 2>/dev/null || echo "")

if [ ! -z "$orphaned_sgs" ]; then
    print_warning "Found orphaned security groups: $orphaned_sgs"
    read -p "Delete orphaned security groups? (yes/no): " delete_sgs
    
    if [ "$delete_sgs" = "yes" ]; then
        for sg in $orphaned_sgs; do
            print_status "Deleting security group: $sg"
            aws ec2 delete-security-group --group-id $sg
        done
    fi
fi

# Check for orphaned load balancers
print_status "Checking for orphaned load balancers..."
orphaned_lbs=$(aws elbv2 describe-load-balancers --query 'LoadBalancers[?contains(LoadBalancerName, `main-alb`)].LoadBalancerArn' --output text 2>/dev/null || echo "")

if [ ! -z "$orphaned_lbs" ]; then
    print_warning "Found orphaned load balancers: $orphaned_lbs"
    read -p "Delete orphaned load balancers? (yes/no): " delete_lbs
    
    if [ "$delete_lbs" = "yes" ]; then
        for lb in $orphaned_lbs; do
            print_status "Deleting load balancer: $lb"
            aws elbv2 delete-load-balancer --load-balancer-arn $lb
        done
    fi
fi

# Check for orphaned target groups
print_status "Checking for orphaned target groups..."
orphaned_tgs=$(aws elbv2 describe-target-groups --query 'TargetGroups[?contains(TargetGroupName, `app-tg`)].TargetGroupArn' --output text 2>/dev/null || echo "")

if [ ! -z "$orphaned_tgs" ]; then
    print_warning "Found orphaned target groups: $orphaned_tgs"
    read -p "Delete orphaned target groups? (yes/no): " delete_tgs
    
    if [ "$delete_tgs" = "yes" ]; then
        for tg in $orphaned_tgs; do
            print_status "Deleting target group: $tg"
            aws elbv2 delete-target-group --target-group-arn $tg
        done
    fi
fi

# Check for orphaned EFS file systems
print_status "Checking for orphaned EFS file systems..."
orphaned_efs=$(aws efs describe-file-systems --query 'FileSystems[?contains(Name, `main-efs`)].FileSystemId' --output text 2>/dev/null || echo "")

if [ ! -z "$orphaned_efs" ]; then
    print_warning "Found orphaned EFS file systems: $orphaned_efs"
    read -p "Delete orphaned EFS file systems? (yes/no): " delete_efs
    
    if [ "$delete_efs" = "yes" ]; then
        for efs in $orphaned_efs; do
            print_status "Deleting EFS file system: $efs"
            aws efs delete-file-system --file-system-id $efs
        done
    fi
fi

print_status "✅ Cleanup completed successfully!"
print_status "You can now run 'terraform init' and 'terraform apply' to create fresh infrastructure." 