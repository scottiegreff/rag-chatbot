terraform {
  required_version = ">= 1.0"

 backend "s3" {
    bucket         = "my-tfstate-bucket-12345"
    key            = "terraform/main.tfstate"
    region         = "ca-central-1"
    dynamodb_table = "terraform-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.region
}

# Variables
variable "region" {
  description = "AWS region"
  type        = string
  default     = "ca-central-1"
}

variable "state_bucket" {
  description = "S3 bucket for Terraform state"
  type        = string
}

variable "state_table" {
  description = "DynamoDB table for state locking"
  type        = string
  default     = "terraform-lock"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "List of public subnet CIDRs"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "List of private subnet CIDRs"
  type        = list(string)
  default     = ["10.0.3.0/24", "10.0.4.0/24"]
}

variable "availability_zones" {
  description = "AZs to deploy into"
  type        = list(string)
  default     = ["ca-central-1a", "ca-central-1b"]
}

variable "nat_az" {
  description = "AZ for NAT Gateway"
  type        = string
  default     = "ca-central-1a"
}

variable "instance_type_app" {
  description = "EC2 instance type for app servers"
  type        = string
  default     = "t3.medium"
}

variable "key_name" {
  description = "Key pair name for SSH access"
  type        = string
  default     = "scotts-keypair"
}

variable "allowed_ssh_cidr" {
  description = "CIDR block for SSH access"
  type        = string
  default     = "24.80.179.233/32"
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS listener"
  type        = string
}

variable "db_password" {
  description = "Password for Postgres admin user"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "desired_capacity" {
  description = "Desired number of EC2 instances in the Auto Scaling Group"
  type        = number
  default     = 1
}

variable "app_port" {
  description = "Port for the application backend"
  type        = number
  default     = 8000
}

variable "health_port" {
  description = "Port for the health check server"
  type        = number
  default     = 8081
}

variable "git_repository" {
  description = "Git repository URL for the application"
  type        = string
  default     = "https://github.com/scottiegreff/rag-chatbot.git"
}

variable "python_version" {
  description = "Python version to install"
  type        = string
  default     = "3.9"
}

# Data Sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  tags = { Name = "main-vpc" }
}

# Subnets
resource "aws_subnet" "public" {
  count                   = length(var.availability_zones)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true
  tags = { Name = "public-subnet-${var.availability_zones[count.index]}" }
}

resource "aws_subnet" "private" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]
  tags = { Name = "private-subnet-${var.availability_zones[count.index]}" }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "main-igw" }
}

# EIP for NAT
resource "aws_eip" "nat" {
  domain = "vpc"
  depends_on = [aws_internet_gateway.igw]
}

# NAT Gateway
resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id
  tags          = { Name = "main-nat-gateway" }
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = { Name = "public-rt" }
}

resource "aws_route_table_association" "public" {
  count          = length(var.availability_zones)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }

  tags = { Name = "private-rt" }
}

resource "aws_route_table_association" "private" {
  count          = length(var.availability_zones)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# Security Groups
resource "aws_security_group" "alb" {
  name        = "alb-sg"
  description = "Allow HTTP/HTTPS"
  vpc_id      = aws_vpc.main.id

  ingress {
    description      = "HTTP"
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  ingress {
    description      = "HTTPS"
    from_port        = 443
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "alb-sg" }
}

resource "aws_security_group" "app" {
  name        = "app-sg"
  description = "Allow ALB and SSH"
  vpc_id      = aws_vpc.main.id

  ingress {
    description      = "From ALB"
    from_port        = 8000
    to_port          = 8000
    protocol         = "tcp"
    security_groups  = [aws_security_group.alb.id]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "app-sg" }
}

resource "aws_security_group" "rds" {
  name        = "rds-sg"
  description = "Allow Postgres from app servers"
  vpc_id      = aws_vpc.main.id

  ingress {
    description      = "Postgres"
    from_port        = 5432
    to_port          = 5432
    protocol         = "tcp"
    security_groups  = [aws_security_group.app.id]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "rds-sg" }
}

resource "aws_security_group" "efs" {
  name        = "efs-sg"
  description = "Allow NFS from app servers"
  vpc_id      = aws_vpc.main.id

  ingress {
    description      = "NFS"
    from_port        = 2049
    to_port          = 2049
    protocol         = "tcp"
    security_groups  = [aws_security_group.app.id]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "efs-sg" }
}

# Application Load Balancer
resource "aws_lb" "alb" {
  name               = "main-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  tags = { Name = "main-alb" }
}

resource "aws_lb_target_group" "app" {
  name     = "app-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/api/database/health"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  tags = { Name = "app-tg" }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# EFS Configuration
resource "aws_efs_file_system" "efs" {
  creation_token = "main-efs"
  tags           = { Name = "main-efs" }
}

resource "aws_efs_mount_target" "efs_mt" {
  count          = length(var.availability_zones)
  file_system_id = aws_efs_file_system.efs.id
  subnet_id      = aws_subnet.private[count.index].id
  security_groups = [aws_security_group.efs.id]
}

# Launch Template for App Servers
resource "aws_launch_template" "app_lt" {
  name_prefix   = "app-lt-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type_app
  key_name      = var.key_name

  iam_instance_profile {
    name = aws_iam_instance_profile.ssm_profile.name
  }

  network_interfaces {
    associate_public_ip_address = false
    subnet_id                   = aws_subnet.private[0].id
    security_groups             = [aws_security_group.app.id]
  }

  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size = 32
      volume_type = "gp3"
      delete_on_termination = true
    }
  }

  user_data = base64encode(
    <<-EOF
#!/bin/bash
set -e

# Update system
yum update -y

# Install Python 3.9 (specific version for compatibility)
yum install -y python3.9 python3.9-pip python3.9-devel
alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.9 1

# Install Docker
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose (latest version)
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d" -f4)
curl -L "https://github.com/docker/compose/releases/download/$${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install additional tools
yum install -y git wget curl jq

# Create application directory
mkdir -p /opt/fci-chatbot
cd /opt/fci-chatbot

# Clone the application
git clone https://github.com/scottiegreff/rag-chatbot.git .

# Create a startup script that handles the transition properly
cat > /opt/fci-chatbot/startup.sh << 'STARTUP_EOF'
#!/bin/bash
set -e

echo "Starting FCI Chatbot deployment..."

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        echo "Port $port is in use, stopping process..."
        lsof -ti :$port | xargs kill -9
        sleep 2
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local max_attempts=30
    local attempt=1
    
    echo "Waiting for service at $url..."
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s $url > /dev/null 2>&1; then
            echo "Service is ready!"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts - Service not ready yet..."
        sleep 10
        attempt=$((attempt + 1))
    done
    echo "Service failed to start within expected time"
    return 1
}

# Create production environment file
cat > .env << 'ENV_EOF'
# Production Environment Configuration
POSTGRES_PASSWORD=FCI_Chatbot_2024_Secure_Pass!
DB_HOST=main-postgres.cb4my0e6eoxp.ca-central-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=appdb
DB_USER=adminuser
WEAVIATE_URL=http://localhost:8080
MODEL_PATH=/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
MODEL_TYPE=llama
GPU_LAYERS=0
CONTEXT_LENGTH=4096
ENABLE_RAG=true
RAG_USE_CPU=true
CHUNK_SIZE=500
OVERLAP=50
HOST=0.0.0.0
PORT=8000
DEBUG=false
CORS_ORIGINS=*
MAX_HISTORY_MESSAGES=50
ENABLE_INTERNET_SEARCH=false
CT_METAL=0
CT_CUDA=0
ENV_EOF

# Download the TinyLlama model if not present
mkdir -p models
if [ ! -f "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf" ]; then
    echo "Downloading TinyLlama model..."
    wget -O models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
fi

# Stop any existing processes on port 8000
check_port 8000

# Start Docker Compose
echo "Starting Docker Compose..."
/usr/local/bin/docker-compose down || true
/usr/local/bin/docker-compose up -d

# Wait for backend to be ready
wait_for_service "http://localhost:8000/api/database/health"

echo "FCI Chatbot deployment complete!"
echo "Application is available at: http://localhost:8000"
echo "Health check: http://localhost:8000/api/database/health"
STARTUP_EOF

chmod +x /opt/fci-chatbot/startup.sh

# Create a simple health check endpoint (different port to avoid conflicts)
cat > /opt/fci-chatbot/health_server.py << 'HEALTH_EOF'
from flask import Flask
app = Flask(__name__)

@app.route('/')
def health():
    return {"status": "deploying", "message": "FCI Chatbot is being deployed..."}

@app.route('/ready')
def ready():
    return {"status": "ready", "message": "FCI Chatbot is ready!"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
HEALTH_EOF

# Install Flask for health server
pip3 install flask

# Start health server on port 8081 (different from main app)
nohup python3 /opt/fci-chatbot/health_server.py > /var/log/health_server.log 2>&1 &

# Start the main application deployment
nohup /opt/fci-chatbot/startup.sh > /var/log/app_deployment.log 2>&1 &

echo "FCI Chatbot deployment initiated!"
echo "Health server available at: http://localhost:8081"
echo "Main application will be available at: http://localhost:8000"
echo "Check logs: tail -f /var/log/app_deployment.log"
EOF
  )

  tag_specifications {
    resource_type = "instance"
    tags = { Name = "app-server" }
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "app_asg" {
  name                      = "app-asg"
  desired_capacity          = var.desired_capacity
  max_size                  = 3
  min_size                  = 1

  launch_template {
    id      = aws_launch_template.app_lt.id
    version = "$Latest"
  }

  vpc_zone_identifier       = aws_subnet.private[*].id
  target_group_arns         = [aws_lb_target_group.app.arn]
  health_check_type         = "ELB"
  health_check_grace_period = 300

  tag {
    key                 = "Name"
    value               = "app-server"
    propagate_at_launch = true
  }
}

# RDS Configuration
resource "aws_db_subnet_group" "rds_subnets" {
  name       = "rds-subnet-group"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_db_instance" "postgres" {
  identifier              = "main-postgres"
  engine                  = "postgres"
  instance_class          = var.db_instance_class
  allocated_storage       = 20
  db_name                 = "appdb"
  username                = "adminuser"
  password                = var.db_password
  publicly_accessible     = false
  multi_az                = true
  vpc_security_group_ids  = [aws_security_group.rds.id]
  db_subnet_group_name    = aws_db_subnet_group.rds_subnets.name
  skip_final_snapshot     = true

  tags = { Name = "main-rds" }
}

# IAM Role for Systems Manager
resource "aws_iam_role" "ssm_role" {
  name = "ssm-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ssm_policy" {
  role       = aws_iam_role.ssm_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ssm_profile" {
  name = "ssm-profile"
  role = aws_iam_role.ssm_role.name
}

# Outputs
output "alb_dns_name" {
  description = "URL of the Application Load Balancer"
  value       = aws_lb.alb.dns_name
}

output "rds_endpoint" {
  description = "Postgres endpoint"
  value       = aws_db_instance.postgres.address
}
