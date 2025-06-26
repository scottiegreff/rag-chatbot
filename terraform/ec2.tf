# EC2 Instance for FCI Chatbot

# Data source for latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Create EC2 key pair
resource "aws_key_pair" "main" {
  key_name   = var.key_pair_name
  public_key = file("~/.ssh/id_rsa.pub")  # You'll need to create this SSH key

  tags = {
    Name = "${var.project_name}-key-pair"
  }
}

# Create EC2 instance
resource "aws_instance" "main" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.main.key_name
  vpc_security_group_ids = [aws_security_group.ec2.id]
  subnet_id              = aws_subnet.public[0].id
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
    encrypted   = true

    tags = {
      Name = "${var.project_name}-root-volume"
    }
  }

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    project_name = var.project_name
  }))

  tags = {
    Name = "${var.project_name}-instance"
  }

  depends_on = [aws_internet_gateway.main]
}

# Create Elastic IP for the instance
resource "aws_eip" "instance" {
  domain = "vpc"
  instance = aws_instance.main.id

  tags = {
    Name = "${var.project_name}-instance-eip"
  }

  depends_on = [aws_internet_gateway.main]
}

# Outputs
output "instance_id" {
  value = aws_instance.main.id
}

output "instance_public_ip" {
  value = aws_eip.instance.public_ip
}

output "instance_private_ip" {
  value = aws_instance.main.private_ip
}

output "ssh_command" {
  value = "ssh -i ~/.ssh/id_rsa ec2-user@${aws_eip.instance.public_ip}"
}

output "application_url" {
  value = "http://${aws_eip.instance.public_ip}:8000"
} 