# FCI Chatbot Terraform Variables - Personalized Configuration for Scott Greff

# AWS Configuration
aws_region = "ca-central-1"  # Calgary, Canada

# Project Configuration
project_name = "fci-chatbot"
environment  = "production"

# Personal Information
owner_name = "Scott Greff"
contact_email = "scottiegreff@gmail.com"
company_name = "Scott Greff Development"

# Network Configuration
vpc_cidr = "10.0.0.0/16"
availability_zones = ["ca-central-1a", "ca-central-1b"]

# Instance Configuration
instance_type = "t3.medium"  # 2 vCPU, 4 GB RAM - good for Docker
key_pair_name = "fci-chatbot-key"

# Database Configuration
# Secure password generated for PostgreSQL
db_password = "FCI_Chatbot_2024_Secure_Pass!"

# Application Configuration
# No domain name provided - will use IP address
# domain_name = "your-domain.com"  # If you get a domain later
# ssl_certificate_arn = "arn:aws:acm:ca-central-1:123456789012:certificate/xxx"  # If you get an SSL certificate

# Resource Tags
tags = {
  Owner       = "Scott Greff"
  Contact     = "scottiegreff@gmail.com"
  Company     = "Scott Greff Development"
  Project     = "FCI-Chatbot"
  Environment = "production"
  ManagedBy   = "Terraform"
} 