#!/bin/bash

echo "=== AWS Orphaned Resources Cleanup Script ==="
echo "This script will check for orphaned resources and optionally delete them."
echo ""

# Function to check for orphaned EBS volumes
check_ebs_volumes() {
    echo "=== Checking for orphaned EBS volumes ==="
    ORPHANED_VOLUMES=$(aws ec2 describe-volumes --filters "Name=status,Values=available" --query 'Volumes[*].VolumeId' --output text)
    
    if [ -z "$ORPHANED_VOLUMES" ]; then
        echo "No orphaned EBS volumes found."
    else
        echo "Found orphaned EBS volumes:"
        echo "$ORPHANED_VOLUMES"
        read -p "Delete these volumes? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            for volume in $ORPHANED_VOLUMES; do
                echo "Deleting volume: $volume"
                aws ec2 delete-volume --volume-id "$volume"
            done
        fi
    fi
    echo ""
}

# Function to check for orphaned network interfaces
check_network_interfaces() {
    echo "=== Checking for orphaned network interfaces ==="
    ORPHANED_ENIS=$(aws ec2 describe-network-interfaces --filters "Name=attachment.status,Values=detached" --query 'NetworkInterfaces[*].NetworkInterfaceId' --output text)
    
    if [ -z "$ORPHANED_ENIS" ]; then
        echo "No orphaned network interfaces found."
    else
        echo "Found orphaned network interfaces:"
        echo "$ORPHANED_ENIS"
        read -p "Delete these network interfaces? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            for eni in $ORPHANED_ENIS; do
                echo "Deleting network interface: $eni"
                aws ec2 delete-network-interface --network-interface-id "$eni"
            done
        fi
    fi
    echo ""
}

# Function to check for orphaned security groups
check_security_groups() {
    echo "=== Checking for orphaned security groups ==="
    ORPHANED_SGS=$(aws ec2 describe-security-groups --query 'SecurityGroups[?length(ReferencedSecurityGroupIds)==`0` && length(IpPermissions)==`0` && length(IpPermissionsEgress)==`0`].GroupId' --output text)
    
    if [ -z "$ORPHANED_SGS" ]; then
        echo "No orphaned security groups found."
    else
        echo "Found orphaned security groups:"
        echo "$ORPHANED_SGS"
        read -p "Delete these security groups? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            for sg in $ORPHANED_SGS; do
                echo "Deleting security group: $sg"
                aws ec2 delete-security-group --group-id "$sg"
            done
        fi
    fi
    echo ""
}

# Function to check for orphaned load balancers
check_load_balancers() {
    echo "=== Checking for load balancers ==="
    LBS=$(aws elbv2 describe-load-balancers --query 'LoadBalancers[*].[LoadBalancerArn,LoadBalancerName]' --output table)
    
    if [ -z "$LBS" ]; then
        echo "No load balancers found."
    else
        echo "Found load balancers:"
        echo "$LBS"
        read -p "Delete these load balancers? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            aws elbv2 describe-load-balancers --query 'LoadBalancers[*].LoadBalancerArn' --output text | while read lb_arn; do
                echo "Deleting load balancer: $lb_arn"
                aws elbv2 delete-load-balancer --load-balancer-arn "$lb_arn"
            done
        fi
    fi
    echo ""
}

# Function to check for orphaned auto scaling groups
check_auto_scaling_groups() {
    echo "=== Checking for auto scaling groups ==="
    ASGS=$(aws autoscaling describe-auto-scaling-groups --query 'AutoScalingGroups[*].[AutoScalingGroupName,DesiredCapacity]' --output table)
    
    if [ -z "$ASGS" ]; then
        echo "No auto scaling groups found."
    else
        echo "Found auto scaling groups:"
        echo "$ASGS"
        read -p "Delete these auto scaling groups? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            aws autoscaling describe-auto-scaling-groups --query 'AutoScalingGroups[*].AutoScalingGroupName' --output text | while read asg_name; do
                echo "Deleting auto scaling group: $asg_name"
                aws autoscaling delete-auto-scaling-group --auto-scaling-group-name "$asg_name" --force-delete
            done
        fi
    fi
    echo ""
}

# Function to check for orphaned launch templates
check_launch_templates() {
    echo "=== Checking for launch templates ==="
    LTS=$(aws ec2 describe-launch-templates --query 'LaunchTemplates[*].[LaunchTemplateId,LaunchTemplateName]' --output table)
    
    if [ -z "$LTS" ]; then
        echo "No launch templates found."
    else
        echo "Found launch templates:"
        echo "$LTS"
        read -p "Delete these launch templates? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            aws ec2 describe-launch-templates --query 'LaunchTemplates[*].LaunchTemplateId' --output text | while read lt_id; do
                echo "Deleting launch template: $lt_id"
                aws ec2 delete-launch-template --launch-template-id "$lt_id"
            done
        fi
    fi
    echo ""
}

# Function to check for orphaned EFS file systems
check_efs_file_systems() {
    echo "=== Checking for EFS file systems ==="
    EFS_SYSTEMS=$(aws efs describe-file-systems --query 'FileSystems[*].[FileSystemId,Name,LifeCycleState]' --output table)
    
    if [ -z "$EFS_SYSTEMS" ]; then
        echo "No EFS file systems found."
    else
        echo "Found EFS file systems:"
        echo "$EFS_SYSTEMS"
        read -p "Delete these EFS file systems? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            aws efs describe-file-systems --query 'FileSystems[*].FileSystemId' --output text | while read fs_id; do
                echo "Deleting EFS file system: $fs_id"
                aws efs delete-file-system --file-system-id "$fs_id"
            done
        fi
    fi
    echo ""
}

# Main execution
echo "Starting cleanup process..."
echo ""

check_ebs_volumes
check_network_interfaces
check_security_groups
check_load_balancers
check_auto_scaling_groups
check_launch_templates
check_efs_file_systems

echo "=== Cleanup complete ==="
echo "You can now run 'terraform destroy' to remove Terraform-managed resources." 