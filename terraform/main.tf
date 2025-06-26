# Configure the AWS Provider
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Optional: Use S3 backend for state management (recommended for production)
  # backend "s3" {
  #   bucket = "fci-chatbot-terraform-state"
  #   key    = "terraform.tfstate"
  #   region = "ca-central-1"
  # }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "FCI-Chatbot"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ca-central-1"  # Calgary, Canada
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "fci-chatbot"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["ca-central-1a", "ca-central-1b"]  # Calgary availability zones
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"  # 2 vCPU, 4 GB RAM - good for Docker
}

variable "key_pair_name" {
  description = "Name of the EC2 key pair"
  type        = string
  default     = "fci-chatbot-key"
} 