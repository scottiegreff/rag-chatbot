
# terraform.tfvars
region                    = "ca-central-1"
environment               = "dev"
instance_type_app         = "t3.medium"
key_name                  = "scotts-keypair"
allowed_ssh_cidr          = "24.80.179.233/32"
app_port                  = 8000
create_load_balancer      = true
asg_min_size              = 1
asg_max_size              = 3
asg_desired_capacity      = 2
health_check_path         = "/"
create_rds                = true
db_instance_class         = "db.t3.micro"
db_allocated_storage      = 20
db_name                   = "appdb"
db_username               = "dbadmin"
db_password               = "YourSecurePassword123!"  # Change this!
create_bastion            = true
bastion_instance_type     = "t3.micro"