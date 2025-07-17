# Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs (Web Tier)"
  value       = aws_subnet.public[*].id
}

output "private_app_subnet_ids" {
  description = "Private app subnet IDs (Application Tier)"
  value       = aws_subnet.private_app[*].id
}

output "private_db_subnet_ids" {
  description = "Private database subnet IDs (Database Tier)"
  value       = aws_subnet.private_db[*].id
}

output "load_balancer_dns" {
  description = "Load balancer DNS name"
  value       = var.create_load_balancer ? aws_lb.app[0].dns_name : null
}

output "bastion_public_ip" {
  description = "Bastion host public IP"
  value       = var.create_bastion ? aws_instance.bastion[0].public_ip : null
}

output "efs_id" {
  description = "EFS file system ID"
  value       = aws_efs_file_system.efs.id
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = var.create_rds ? aws_db_instance.postgres[0].endpoint : null
}
