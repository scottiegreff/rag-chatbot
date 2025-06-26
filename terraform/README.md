# FCI Chatbot AWS Deployment Guide

This guide will walk you through deploying your FCI Chatbot Docker application to AWS using Terraform, starting from a brand new AWS account.

## Prerequisites

1. **AWS Account**: You have a brand new AWS account
2. **Terraform**: Install Terraform on your local machine
3. **AWS CLI**: Install AWS CLI and configure it
4. **SSH Key**: Generate an SSH key pair for EC2 access

## Step 1: Initial AWS Setup

### 1.1 Create Root User Access Keys (Temporary)

1. Log into your AWS Console
2. Go to IAM → Users → Your root user
3. Create access keys (you'll only do this once)
4. Save the Access Key ID and Secret Access Key securely

### 1.2 Install and Configure AWS CLI

```bash
# Install AWS CLI (if not already installed)
# macOS: brew install awscli
# Linux: sudo apt-get install awscli

# Configure AWS CLI
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key
# Enter your region (e.g., us-east-1)
# Enter your output format (json)
```

### 1.3 Generate SSH Key Pair

```bash
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# Verify the key was created
ls -la ~/.ssh/id_rsa*
```

## Step 2: Install Terraform

### 2.1 Install Terraform

```bash
# macOS
brew install terraform

# Linux
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs)"
sudo apt-get update && sudo apt-get install terraform

# Verify installation
terraform version
```

## Step 3: Deploy Infrastructure

### 3.1 Initialize Terraform

```bash
cd terraform
terraform init
```

### 3.2 Review the Plan

```bash
terraform plan
```

This will show you what resources will be created:
- IAM users, groups, and policies
- VPC with public and private subnets
- Security groups
- EC2 instance with Elastic IP
- NAT Gateway (for private subnet internet access)

### 3.3 Deploy the Infrastructure

```bash
terraform apply
```

When prompted, type `yes` to confirm.

### 3.4 Save Important Outputs

After deployment, Terraform will output important information:

```bash
terraform output
```

Save these outputs:
- `terraform_user_access_key` - Access key for the Terraform user
- `terraform_user_secret_key` - Secret key for the Terraform user
- `instance_public_ip` - Public IP of your EC2 instance
- `ssh_command` - SSH command to connect to your instance
- `application_url` - URL where your application will be available

## Step 4: Configure Terraform User (Security Best Practice)

### 4.1 Update AWS CLI Configuration

```bash
# Configure a new profile for the Terraform user
aws configure --profile terraform
# Enter the terraform_user_access_key
# Enter the terraform_user_secret_key
# Enter your region
# Enter json for output format
```

### 4.2 Update Terraform Configuration

Edit `main.tf` and add the profile:

```hcl
provider "aws" {
  region  = var.aws_region
  profile = "terraform"  # Add this line
  
  default_tags {
    tags = {
      Project     = "FCI-Chatbot"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
```

### 4.3 Remove Root User Access Keys

1. Go to IAM → Users → Your root user
2. Delete the access keys you created earlier
3. This is a security best practice

## Step 5: Deploy Your Application

### 5.1 Upload Your Application Code

You have several options:

#### Option A: Use Git (Recommended)
1. Push your code to a Git repository (GitHub, GitLab, etc.)
2. Update the user_data.sh script with your repository URL
3. Redeploy the infrastructure

#### Option B: Use S3
1. Create an S3 bucket for your application
2. Upload your application files to S3
3. Update the user_data.sh script to download from S3

#### Option C: Manual Upload
1. SSH into your EC2 instance
2. Manually copy your application files

### 5.2 SSH into Your Instance

```bash
# Use the SSH command from terraform output
ssh -i ~/.ssh/id_rsa ec2-user@YOUR_INSTANCE_IP
```

### 5.3 Deploy Your Application

```bash
# Navigate to the application directory
cd /opt/fci-chatbot

# Clone your repository (if using Git)
git clone https://github.com/yourusername/FCI-Chatbot.git .

# Or copy your files manually
# scp -r ./your-local-files ec2-user@YOUR_INSTANCE_IP:/opt/fci-chatbot/

# Run the setup script
./setup.sh
```

## Step 6: Verify Deployment

### 6.1 Check Application Status

```bash
# SSH into your instance
ssh -i ~/.ssh/id_rsa ec2-user@YOUR_INSTANCE_IP

# Check if containers are running
docker ps

# Check application logs
docker logs fci-chatbot-backend

# Test the application
curl http://localhost:8000/api/database/health
```

### 6.2 Access Your Application

Open your browser and go to:
```
http://YOUR_INSTANCE_IP:8000
```

## Step 7: Security Hardening

### 7.1 Update Security Groups

1. Go to EC2 → Security Groups
2. Find your security group
3. Restrict SSH access to your IP only
4. Consider using a bastion host for production

### 7.2 Set Up SSL/TLS

1. Register a domain name
2. Set up Route 53 for DNS
3. Request an SSL certificate from AWS Certificate Manager
4. Configure a load balancer with HTTPS

### 7.3 Set Up Monitoring

1. Enable CloudWatch monitoring
2. Set up CloudWatch alarms
3. Configure log aggregation

## Step 8: Production Considerations

### 8.1 Use RDS for Database

For production, consider using AWS RDS instead of containerized PostgreSQL:

```hcl
# Add to your Terraform configuration
resource "aws_db_instance" "postgres" {
  identifier           = "${var.project_name}-postgres"
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  storage_encrypted    = true
  
  db_name  = "fci_chatbot"
  username = "postgres"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  tags = {
    Name = "${var.project_name}-postgres"
  }
}
```

### 8.2 Use ECS/EKS for Container Orchestration

For better scalability and management, consider using ECS or EKS instead of Docker Compose on EC2.

### 8.3 Set Up CI/CD Pipeline

1. Use GitHub Actions or AWS CodePipeline
2. Automate testing and deployment
3. Set up blue-green deployments

## Troubleshooting

### Common Issues

1. **SSH Connection Failed**
   - Check security group rules
   - Verify key pair is correct
   - Check instance status

2. **Application Not Starting**
   - Check Docker logs: `docker logs fci-chatbot-backend`
   - Check system logs: `journalctl -u fci-chatbot.service`
   - Verify environment variables

3. **Database Connection Issues**
   - Check PostgreSQL container status
   - Verify database credentials
   - Check network connectivity

### Useful Commands

```bash
# Check instance status
aws ec2 describe-instances --instance-ids YOUR_INSTANCE_ID

# View CloudWatch logs
aws logs describe-log-groups
aws logs get-log-events --log-group-name /aws/ec2/fci-chatbot

# Update security group
aws ec2 authorize-security-group-ingress --group-id sg-xxx --protocol tcp --port 22 --cidr YOUR_IP/32
```

## Cleanup

To avoid charges, destroy the infrastructure when not needed:

```bash
terraform destroy
```

**Warning**: This will delete all resources and data!

## Next Steps

1. Set up monitoring and alerting
2. Implement backup strategies
3. Set up CI/CD pipeline
4. Configure domain and SSL
5. Implement auto-scaling
6. Set up disaster recovery

## Support

If you encounter issues:
1. Check AWS CloudTrail for API errors
2. Review Terraform logs
3. Check application logs
4. Consult AWS documentation
5. Consider AWS Support for production workloads 