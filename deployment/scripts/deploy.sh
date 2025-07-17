#!/bin/bash

# AI Chatbot Deployment Script for Oracle Cloud
# This script deploys the application on Oracle Cloud Infrastructure

set -e

# Configuration
APP_NAME="ai-chatbot"
APP_DIR="/opt/ai-chatbot"
BACKUP_DIR="/opt/ai-chatbot/backups"
LOG_DIR="/opt/ai-chatbot/logs"
DATE=$(date +"%Y%m%d_%H%M%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Print functions
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

# Install system dependencies
install_dependencies() {
    print_info "Installing system dependencies..."
    
    # Update package list
    apt-get update
    
    # Install required packages
    apt-get install -y \
        curl \
        wget \
        git \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        python3 \
        python3-pip \
        python3-venv \
        nginx \
        postgresql-client \
        docker.io \
        docker-compose
    
    print_success "System dependencies installed"
}

# Install Docker
install_docker() {
    print_info "Installing Docker..."
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Update and install Docker
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    print_success "Docker installed and started"
}

# Create application directory
create_app_directory() {
    print_info "Creating application directory..."
    
    mkdir -p "$APP_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p models logs
    
    print_success "Application directory created"
}

# Clone or update repository
setup_repository() {
    print_info "Setting up repository..."
    
    if [ -d "$APP_DIR/.git" ]; then
        cd "$APP_DIR"
        git pull origin main
        print_success "Repository updated"
    else
        # Clone repository (replace with actual repository URL)
        git clone https://github.com/your-username/ai-chatbot.git "$APP_DIR"
        print_success "Repository cloned"
    fi
}

# Set up environment
setup_environment() {
    print_info "Setting up environment..."
    
    cd "$APP_DIR"
    
    # Copy environment template
    if [ ! -f .env ]; then
        cp env_template.txt .env
        print_info "Environment file created. Please edit .env with your configuration."
    fi
    
    # Set proper permissions
    chown -R root:root "$APP_DIR"
    chmod -R 755 "$APP_DIR"
    
    print_success "Environment setup complete"
}

# Install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."
    
    cd "$APP_DIR"
    
    # Create virtual environment
    python3 -m venv venv-py311
    source venv-py311/bin/activate
    
    # Install dependencies
    pip install --upgrade pip
    pip install ctransformers weaviate-client sentence-transformers PyPDF2 python-docx
    
    print_success "Python dependencies installed"
}

# Set up PostgreSQL
setup_postgres() {
    print_info "Setting up PostgreSQL..."
    
    # Install PostgreSQL
    apt-get install -y postgresql postgresql-contrib
    
    # Start PostgreSQL
    systemctl start postgresql
    systemctl enable postgresql
    
    # Create database and user
    sudo -u postgres psql -c "CREATE DATABASE ai_chatbot;"
    sudo -u postgres psql -c "CREATE USER postgres WITH PASSWORD 'postgres_password';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_chatbot TO postgres;"
    
    print_success "PostgreSQL setup complete"
}

# Set up Weaviate
setup_weaviate() {
    print_info "Setting up Weaviate..."
    
    cd "$APP_DIR"
    
    # Create Weaviate data directory
    mkdir -p weaviate_data
    
    # Start Weaviate with Docker
    docker run -d \
        --name weaviate \
        --restart unless-stopped \
        -p 8080:8080 \
        -p 50051:50051 \
        -v "$APP_DIR/weaviate_data:/var/lib/weaviate" \
        -e QUERY_DEFAULTS_LIMIT=25 \
        -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
        -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
        -e DEFAULT_VECTORIZER_MODULE=none \
        -e ENABLE_MODULES=text2vec-transformers \
        -e CLUSTER_HOSTNAME=node1 \
        -e GRPC_PORT=50051 \
        semitechnologies/weaviate:1.24.9
    
    print_success "Weaviate setup complete"
}

# Set up Nginx
setup_nginx() {
    print_info "Setting up Nginx..."
    
    # Copy Nginx configuration
    cp "$APP_DIR/deployment/nginx/ai-chatbot.conf" /etc/nginx/sites-available/ai-chatbot
    
    # Enable site
    ln -sf /etc/nginx/sites-available/ai-chatbot /etc/nginx/sites-enabled/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    nginx -t
    
    # Restart Nginx
    systemctl restart nginx
    systemctl enable nginx
    
    print_success "Nginx setup complete"
}

# Set up systemd service
setup_systemd() {
    print_info "Setting up systemd service..."
    
    # Copy service file
    cp "$APP_DIR/deployment/systemd/ai-chatbot.service" /etc/systemd/system/
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable service
    systemctl enable ai-chatbot
    
    print_success "Systemd service setup complete"
}

# Create backup
create_backup() {
    print_info "Creating backup..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup PostgreSQL
    if systemctl is-active --quiet postgresql; then
        sudo -u postgres pg_dump ai_chatbot > "$BACKUP_DIR/postgres_backup_$DATE.sql"
        print_success "PostgreSQL backed up"
    else
        print_warning "PostgreSQL not running, skipping backup"
    fi
    
    # Backup Weaviate
    if docker ps | grep -q weaviate; then
        docker run --rm -v "$APP_DIR/weaviate_data:/data" -v "$BACKUP_DIR:/backup" alpine tar czf "/backup/weaviate_backup_$DATE.tar.gz" -C /data .
        print_success "Weaviate backed up"
    else
        print_warning "Weaviate not running, skipping backup"
    fi
    
    # Backup application
    tar -czf "$BACKUP_DIR/app_backup_$DATE.tar.gz" \
        --exclude='.git' \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='backups' \
        --exclude='logs' \
        "$APP_DIR"
    
    print_success "Application backed up"
    
    # Clean old backups (keep 30 days)
    find "$BACKUP_DIR" -name "*.sql" -mtime +30 -delete 2>/dev/null || true
    find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete 2>/dev/null || true
}

# Start application
start_application() {
    print_info "Starting application..."
    
    cd "$APP_DIR"
    
    # Start with Docker Compose
    docker-compose up -d
    
    # Wait for services to be ready
    sleep 30
    
    # Check service status
    if docker-compose ps | grep -q "Up"; then
        print_success "Application started successfully!"
        print_info "Application is available at: http://$(hostname -I | awk '{print $1}')"
    else
        print_error "Application failed to start. Check logs with: docker-compose logs"
        exit 1
    fi
}

# Show status
show_status() {
    print_info "Service Status:"
    
    echo "Docker services:"
    docker-compose ps
    
    echo ""
    echo "System services:"
    systemctl status nginx --no-pager -l
    systemctl status postgresql --no-pager -l
    systemctl status ai-chatbot --no-pager -l
    
    echo ""
    echo "Resource usage:"
    docker stats --no-stream
}

# Show logs
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$service"
    fi
}

# Stop application
stop_application() {
    print_info "Stopping application..."
    
    cd "$APP_DIR"
    docker-compose down
    
    print_success "Application stopped"
}

# Restart application
restart_application() {
    print_info "Restarting application..."
    
    stop_application
    start_application
    
    print_success "Application restarted"
}

# Show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install     - Full installation (run once)"
    echo "  start       - Start the application"
    echo "  stop        - Stop the application"
    echo "  restart     - Restart the application"
    echo "  status      - Show service status"
    echo "  logs        - Show logs"
    echo "  backup      - Create backup"
    echo "  update      - Update application"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install  # First-time installation"
    echo "  $0 start    # Start application"
    echo "  $0 status   # Check status"
    echo "  $0 logs     # View logs"
}

# Main script logic
case "${1:-help}" in
    install)
        check_root
        install_dependencies
        install_docker
        create_app_directory
        setup_repository
        setup_environment
        install_python_deps
        setup_postgres
        setup_weaviate
        setup_nginx
        setup_systemd
        start_application
        print_success "Installation completed successfully!"
        ;;
    start)
        start_application
        ;;
    stop)
        stop_application
        ;;
    restart)
        restart_application
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    backup)
        create_backup
        ;;
    update)
        check_root
        create_backup
        setup_repository
        restart_application
        print_success "Update completed successfully!"
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac 