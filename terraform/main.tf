# main.tf

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Backend configuration should be static or passed via CLI
  backend "s3" {
    bucket         = "my-tfstate-bucket-12345"  # Static value
    key            = "terraform/main.tfstate"
    region         = "ca-central-1"             # Static value
    dynamodb_table = "terraform-lock"           # Static value
    encrypt        = true
  }
}

provider "aws" {
  region = var.region
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
  enable_dns_support   = true
  
  tags = { 
    Name = "main-vpc"
    Environment = var.environment
  }
}

# PUBLIC SUBNETS (Web Tier) - ALB, NAT Gateways, Bastion
resource "aws_subnet" "public" {
  count                   = var.subnet_count
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  
  tags = { 
    Name = "public-subnet-${data.aws_availability_zones.available.names[count.index]}"
    Tier = "web"
    Type = "public"
  }
}

# PRIVATE APP SUBNETS (Application Tier) - EC2 instances
resource "aws_subnet" "private_app" {
  count             = var.subnet_count
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_app_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = { 
    Name = "private-app-subnet-${data.aws_availability_zones.available.names[count.index]}"
    Tier = "application"
    Type = "private"
  }
}

# PRIVATE DB SUBNETS (Database Tier) - RDS, EFS
resource "aws_subnet" "private_db" {
  count             = var.subnet_count
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_db_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = { 
    Name = "private-db-subnet-${data.aws_availability_zones.available.names[count.index]}"
    Tier = "database"
    Type = "private"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "main-igw" }
}

# EIP & NAT Gateways (one per AZ for HA)
resource "aws_eip" "nat" {
  count      = var.subnet_count
  domain     = "vpc"
  depends_on = [aws_internet_gateway.igw]
  
  tags = { 
    Name = "nat-eip-${data.aws_availability_zones.available.names[count.index]}"
  }
}

resource "aws_nat_gateway" "nat" {
  count         = var.subnet_count
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  tags = { 
    Name = "nat-gateway-${data.aws_availability_zones.available.names[count.index]}"
  }
  
  depends_on = [aws_internet_gateway.igw]
}

# ROUTE TABLES

# Public Route Table (Web Tier)
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  
  tags = { 
    Name = "public-rt"
    Tier = "web"
  }
}

resource "aws_route_table_association" "public" {
  count          = var.subnet_count
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Private App Route Tables (Application Tier)
resource "aws_route_table" "private_app" {
  count  = var.subnet_count
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat[count.index].id
  }
  
  tags = { 
    Name = "private-app-rt-${data.aws_availability_zones.available.names[count.index]}"
    Tier = "application"
  }
}

resource "aws_route_table_association" "private_app" {
  count          = var.subnet_count
  subnet_id      = aws_subnet.private_app[count.index].id
  route_table_id = aws_route_table.private_app[count.index].id
}

# Private DB Route Tables (Database Tier) - No internet access
resource "aws_route_table" "private_db" {
  count  = var.subnet_count
  vpc_id = aws_vpc.main.id
  
  tags = { 
    Name = "private-db-rt-${data.aws_availability_zones.available.names[count.index]}"
    Tier = "database"
  }
}

resource "aws_route_table_association" "private_db" {
  count          = var.subnet_count
  subnet_id      = aws_subnet.private_db[count.index].id
  route_table_id = aws_route_table.private_db[count.index].id
}

# SECURITY GROUPS

# Application Load Balancer Security Group
resource "aws_security_group" "alb" {
  count       = var.create_load_balancer ? 1 : 0
  name        = "alb-sg"
  description = "Security group for ALB (Web Tier)"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "All outbound to app tier"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { 
    Name = "alb-sg"
    Tier = "web"
  }
}

# Application Tier Security Group
resource "aws_security_group" "app" {
  name        = "app-sg"
  description = "Security group for application servers (App Tier)"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Application port from ALB"
    from_port       = var.app_port
    to_port         = var.app_port
    protocol        = "tcp"
    security_groups = var.create_load_balancer ? [aws_security_group.alb[0].id] : []
    cidr_blocks     = var.create_load_balancer ? [] : [var.vpc_cidr]
  }
  
  ingress {
    description     = "SSH from bastion"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = var.create_bastion ? [aws_security_group.bastion[0].id] : []
    cidr_blocks     = var.create_bastion ? [] : [var.allowed_ssh_cidr]
  }
  
  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = { 
    Name = "app-sg"
    Tier = "application"
  }
}

# Database Tier Security Group
resource "aws_security_group" "rds" {
  name        = "rds-sg"
  description = "Security group for RDS database (Database Tier)"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL from app tier only"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }
  
  tags = { 
    Name = "rds-sg"
    Tier = "database"
  }
}

# EFS Security Group (Database Tier)
resource "aws_security_group" "efs" {
  name        = "efs-sg"
  description = "Security group for EFS (Database Tier)"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "NFS from app tier only"
    from_port       = 2049
    to_port         = 2049
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = { 
    Name = "efs-sg"
    Tier = "database"
  }
}

# Bastion Host Security Group
resource "aws_security_group" "bastion" {
  count       = var.create_bastion ? 1 : 0
  name        = "bastion-sg"
  description = "Security group for bastion host (Web Tier)"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH from allowed CIDR"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  egress {
    description = "SSH to app tier"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.private_app_subnet_cidrs
  }

  egress {
    description = "HTTPS for updates"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "HTTP for updates"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { 
    Name = "bastion-sg"
    Tier = "web"
  }
}

# EFS (Database Tier)
resource "aws_efs_file_system" "efs" {
  creation_token = "main-efs"
  encrypted      = true
  
  performance_mode = "generalPurpose"
  throughput_mode  = "provisioned"
  provisioned_throughput_in_mibps = 100
  
  tags = { 
    Name = "main-efs"
    Environment = var.environment
    Tier = "database"
  }
}

resource "aws_efs_mount_target" "efs_mt" {
  count           = var.subnet_count
  file_system_id  = aws_efs_file_system.efs.id
  subnet_id       = aws_subnet.private_db[count.index].id  # Database tier
  security_groups = [aws_security_group.efs.id]
}

# RDS Subnet Group (Database Tier)
resource "aws_db_subnet_group" "rds" {
  name       = "rds-subnet-group"
  subnet_ids = aws_subnet.private_db[*].id  # Database tier subnets
  
  tags = { 
    Name = "RDS subnet group"
    Tier = "database"
  }
}

# RDS Database (Database Tier)
resource "aws_db_instance" "postgres" {
  count                     = var.create_rds ? 1 : 0
  identifier                = "main-postgres-db"
  engine                    = "postgres"
  engine_version            = "15.4"
  instance_class            = var.db_instance_class
  allocated_storage         = var.db_allocated_storage
  storage_type              = "gp3"
  storage_encrypted         = true
  
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  
  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = true
  deletion_protection = false
  
  tags = {
    Name = "main-postgres-db"
    Environment = var.environment
    Tier = "database"
  }
}

# Launch Template (Application Tier)
resource "aws_launch_template" "app_lt" {
  name_prefix   = "app-lt-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type_app
  key_name      = var.key_name

  vpc_security_group_ids = [aws_security_group.app.id]

  # user_data = base64encode(templatefile("${path.module}/user_data.sh", {
  #   efs_id    = aws_efs_file_system.efs.id
  #   app_port  = var.app_port
  #   db_endpoint = var.create_rds ? aws_db_instance.postgres[0].endpoint : ""
  #   db_name     = var.db_name
  #   db_username = var.db_username
  #   db_password = var.db_password
  # }))

  tag_specifications {
    resource_type = "instance"
    tags = { 
      Name = "app-server"
      Environment = var.environment
      Tier = "application"
    }
  }
  
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"  # Require IMDSv2
  }
}

# Auto Scaling Group (Application Tier)
resource "aws_autoscaling_group" "app_asg" {
  name                = "app-asg"
  vpc_zone_identifier = aws_subnet.private_app[*].id  # Application tier subnets
  target_group_arns   = var.create_load_balancer ? [aws_lb_target_group.app[0].arn] : []
  health_check_type   = var.create_load_balancer ? "ELB" : "EC2"
  health_check_grace_period = 300
  min_size            = var.asg_min_size
  max_size            = var.asg_max_size
  desired_capacity    = var.asg_desired_capacity

  launch_template {
    id      = aws_launch_template.app_lt.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "app-asg"
    propagate_at_launch = false
  }

  tag {
    key                 = "Tier"
    value               = "application"
    propagate_at_launch = true
  }
}

# Application Load Balancer (Web Tier)
resource "aws_lb" "app" {
  count              = var.create_load_balancer ? 1 : 0
  name               = "app-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb[0].id]
  subnets            = aws_subnet.public[*].id  # Web tier subnets

  enable_deletion_protection = false

  tags = { 
    Name = "app-lb"
    Environment = var.environment
    Tier = "web"
  }
}

resource "aws_lb_target_group" "app" {
  count    = var.create_load_balancer ? 1 : 0
  name     = "app-tg"
  port     = var.app_port
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = var.health_check_path
    matcher             = "200"
    port                = "traffic-port"
    protocol            = "HTTP"
  }

  tags = {
    Name = "app-target-group"
    Environment = var.environment
    Tier = "web"
  }
}

resource "aws_lb_listener" "app" {
  count             = var.create_load_balancer ? 1 : 0
  load_balancer_arn = aws_lb.app[0].arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app[0].arn
  }
}

# Bastion Host (Web Tier)
resource "aws_instance" "bastion" {
  count                  = var.create_bastion ? 1 : 0
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.bastion_instance_type
  key_name               = var.key_name
  subnet_id              = aws_subnet.public[0].id  # Web tier subnet
  vpc_security_group_ids = [aws_security_group.bastion[0].id]
  
  associate_public_ip_address = true
  
  tags = {
    Name = "bastion-host"
    Environment = var.environment
    Tier = "web"
  }
}
