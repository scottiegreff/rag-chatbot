# IAM Resources for FCI Chatbot

# Create IAM user for Terraform operations
resource "aws_iam_user" "terraform_user" {
  name = "${var.project_name}-terraform-user"
  path = "/system/"

  tags = {
    Name        = "Terraform User"
    Description = "User for Terraform operations"
  }
}

# Create IAM group for administrators
resource "aws_iam_group" "administrators" {
  name = "${var.project_name}-administrators"
}

# Create IAM group for developers
resource "aws_iam_group" "developers" {
  name = "${var.project_name}-developers"
}

# Add terraform user to administrators group
resource "aws_iam_user_group_membership" "terraform_admin" {
  user   = aws_iam_user.terraform_user.name
  groups = [aws_iam_group.administrators.name]
}

# Create access keys for Terraform user
resource "aws_iam_access_key" "terraform_user_key" {
  user = aws_iam_user.terraform_user.name
}

# IAM Policy for Terraform operations
resource "aws_iam_policy" "terraform_policy" {
  name        = "${var.project_name}-terraform-policy"
  description = "Policy for Terraform operations"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:*",
          "vpc:*",
          "iam:*",
          "rds:*",
          "elasticache:*",
          "s3:*",
          "cloudwatch:*",
          "logs:*",
          "ecs:*",
          "ecr:*",
          "application-autoscaling:*",
          "elasticloadbalancing:*",
          "autoscaling:*",
          "route53:*",
          "acm:*",
          "secretsmanager:*",
          "ssm:*",
          "cloudformation:*"
        ]
        Resource = "*"
      }
    ]
  })
}

# IAM Policy for developers (more restricted)
resource "aws_iam_policy" "developer_policy" {
  name        = "${var.project_name}-developer-policy"
  description = "Policy for developers"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:Describe*",
          "vpc:Describe*",
          "rds:Describe*",
          "elasticache:Describe*",
          "s3:Get*",
          "s3:List*",
          "cloudwatch:Get*",
          "logs:Get*",
          "logs:Describe*",
          "ecs:Describe*",
          "ecr:Get*",
          "ecr:Describe*",
          "elasticloadbalancing:Describe*",
          "autoscaling:Describe*",
          "route53:Get*",
          "route53:List*",
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "arn:aws:s3:::${var.project_name}-*/*"
        ]
      }
    ]
  })
}

# Attach policies to groups
resource "aws_iam_group_policy_attachment" "terraform_policy_attachment" {
  group      = aws_iam_group.administrators.name
  policy_arn = aws_iam_policy.terraform_policy.arn
}

resource "aws_iam_group_policy_attachment" "developer_policy_attachment" {
  group      = aws_iam_group.developers.name
  policy_arn = aws_iam_policy.developer_policy.arn
}

# IAM Role for EC2 instances
resource "aws_iam_role" "ec2_role" {
  name = "${var.project_name}-ec2-role"

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

# IAM Policy for EC2 instances
resource "aws_iam_policy" "ec2_policy" {
  name        = "${var.project_name}-ec2-policy"
  description = "Policy for EC2 instances"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "arn:aws:s3:::${var.project_name}-*/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach EC2 policy to EC2 role
resource "aws_iam_role_policy_attachment" "ec2_policy_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.ec2_policy.arn
}

# Create EC2 instance profile
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.project_name}-ec2-profile"
  role = aws_iam_role.ec2_role.name
}

# Output the access keys (you'll need these for Terraform)
output "terraform_user_access_key" {
  value     = aws_iam_access_key.terraform_user_key.id
  sensitive = true
}

output "terraform_user_secret_key" {
  value     = aws_iam_access_key.terraform_user_key.secret
  sensitive = true
}

output "terraform_user_name" {
  value = aws_iam_user.terraform_user.name
} 