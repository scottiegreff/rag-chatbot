# Quick Start Guide - Scott's FCI Chatbot AWS Deployment

## 🚀 Ready to Deploy!

Your personalized Terraform configuration is ready for deployment to AWS Calgary (Canada Central) region.

### What's Been Configured:

✅ **Personal Information**: Scott Greff, scottiegreff@gmail.com, Scott Greff Development  
✅ **Region**: Calgary, Canada (ca-central-1)  
✅ **Instance**: t3.medium (2 vCPU, 4 GB RAM) - perfect for your Docker app  
✅ **Database**: Secure password generated  
✅ **Security**: IAM users, roles, and policies configured  
✅ **Network**: VPC with public/private subnets  

### Prerequisites Check:

Before deploying, make sure you have:

1. **AWS Account** - You have a brand new AWS account
2. **AWS CLI** - Install and configure with your root credentials
3. **Terraform** - Install on your Mac
4. **SSH Key** - Will be generated automatically if needed

### Step 1: Install Prerequisites

```bash
# Install AWS CLI (if not already installed)
brew install awscli

# Install Terraform (if not already installed)
brew install terraform

# Verify installations
aws --version
terraform version
```

### Step 2: Configure AWS CLI

```bash
# Configure AWS CLI with your root credentials
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key  
# Enter region: ca-central-1
# Enter output format: json
```

### Step 3: Deploy to AWS

```bash
# Navigate to terraform directory
cd terraform

# Run the automated deployment script
./deploy.sh
```

The script will:
- Check all prerequisites
- Initialize Terraform
- Show you what will be created
- Deploy your infrastructure
- Give you connection details

### Step 4: Deploy Your Application

After infrastructure is deployed:

```bash
# SSH into your instance (use the command from terraform output)
ssh -i ~/.ssh/id_rsa ec2-user@YOUR_INSTANCE_IP

# Navigate to application directory
cd /opt/fci-chatbot

# Clone your repository (replace with your actual repo)
git clone https://github.com/yourusername/FCI-Chatbot.git .

# Or copy files manually
# scp -r ./your-local-files ec2-user@YOUR_INSTANCE_IP:/opt/fci-chatbot/

# Run setup
./setup.sh
```

### Step 5: Access Your Application

Your chatbot will be available at:
```
http://YOUR_INSTANCE_IP:8000
```

### What Gets Created:

- **IAM User**: `fci-chatbot-terraform-user` (for Terraform operations)
- **VPC**: `fci-chatbot-vpc` with public/private subnets
- **EC2 Instance**: `fci-chatbot-instance` with Elastic IP
- **Security Groups**: Configured for your application ports
- **Key Pair**: `fci-chatbot-key` for SSH access

### Security Notes:

- All resources are tagged with your information
- Database password is securely generated
- SSH access is currently open (restrict this for production)
- Consider setting up SSL/TLS for production use

### Cost Estimate:

- **EC2 t3.medium**: ~$30-40/month
- **EBS Storage**: ~$5-10/month  
- **NAT Gateway**: ~$45/month
- **Data Transfer**: Minimal for testing
- **Total**: ~$80-100/month

### Next Steps After Deployment:

1. **Secure the instance** (restrict SSH access to your IP)
2. **Set up monitoring** (CloudWatch)
3. **Configure backups** (EBS snapshots)
4. **Set up CI/CD** (GitHub Actions)
5. **Add domain and SSL** (when ready)

### Support:

If you encounter issues:
1. Check the deployment logs
2. Review AWS CloudTrail
3. Check instance status in AWS Console
4. SSH into the instance to debug

### Cleanup:

To avoid charges when not using:
```bash
cd terraform
terraform destroy
```

---

**Ready to deploy? Run `./deploy.sh` in the terraform directory!** 