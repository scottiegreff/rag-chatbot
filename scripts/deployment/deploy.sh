#!/bin/bash

# AI Chatbot Docker Deployment Script
# Supports both M1 Mac development and cloud VM production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="ai-chatbot"
BACKUP_DIR="backups"
DATE=$(date +"%Y%m%d_%H%M%S")

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to detect environment
detect_environment() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # Check if it's Apple Silicon
        if [[ $(uname -m) == "arm64" ]]; then
            ENVIRONMENT="m1-mac"
            print_status "Detected M1 Mac environment"
        else
            ENVIRONMENT="intel-mac"
            print_status "Detected Intel Mac environment"
        fi
    else
        ENVIRONMENT="cloud-vm"
        print_status "Detected cloud VM environment"
    fi
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if models directory exists
    if [ ! -d "models" ]; then
        print_warning "Models directory not found. Creating..."
        mkdir -p models
    fi
    
    # Check if model files exist
    if [ ! -f "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf" ]; then
        print_warning "Model files not found in models/ directory"
        echo "Please copy your GGUF model files to the models/ directory"
        echo "Example: cp /path/to/your/models/*.gguf ./models/"
    fi
    
    print_success "Prerequisites check completed"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [dev|prod|stop|logs|clean|status|backup|restore-postgres|restore-weaviate]"
    echo ""
    echo "Commands:"
    echo "  dev     - Start development environment (M1 Mac optimized)"
    echo "  prod    - Start production environment (Cloud VM optimized)"
    echo "  stop    - Stop all services"
    echo "  logs    - Show logs from all services"
    echo "  clean   - Stop and remove all containers, volumes, and images"
    echo "  status  - Show status of all services"
    echo "  backup  - Create full backup"
    echo "  restore-postgres - Restore PostgreSQL database (requires backup file)"
    echo "  restore-weaviate - Restore Weaviate data (requires backup file)"
    echo ""
    echo "Environment Detection:"
    echo "  The script automatically detects your environment:"
    echo "  - M1 Mac: Uses Metal acceleration and development settings"
    echo "  - Cloud VM: Uses CPU-only and production settings"
    echo ""
    echo "Examples:"
    echo "  $0 dev     # Start development environment"
    echo "  $0 prod    # Start production environment"
    echo "  $0 stop    # Stop all services"
    echo "  $0 logs    # View logs"
    echo "  $0 backup  # Create full backup"
    echo "  $0 restore-postgres backups/postgres_backup_20231201_120000.sql"
}

# Function to start development environment
start_dev() {
    print_status "Starting development environment..."
    
    if [[ $ENVIRONMENT == "m1-mac" ]]; then
        print_status "Using M1 Mac configuration with Metal acceleration"
        docker-compose --env-file env.m1-mac up --build
    else
        print_status "Using development configuration"
        docker-compose --env-file env.cloud-vm up --build
    fi
}

# Function to start production environment
start_prod() {
    print_status "Starting production environment..."
    
    if [[ $ENVIRONMENT == "m1-mac" ]]; then
        print_warning "Production mode on M1 Mac - using cloud VM settings"
    fi
    
    docker-compose --env-file env.cloud-vm -f docker-compose.yml -f docker-compose.prod.yml up -d --build
    
    print_success "Production environment started!"
    echo ""
    echo "Services:"
    echo "  Frontend: http://localhost:8000"
    echo "  API: http://localhost:8000/api"
    echo "  Database: localhost:5432"
    echo ""
    echo "To view logs: $0 logs"
    echo "To stop: $0 stop"
}

# Function to stop services
stop_services() {
    print_status "Stopping all services..."
    docker-compose down
    print_success "Services stopped"
}

# Function to show logs
show_logs() {
    print_status "Showing logs from all services..."
    docker-compose logs -f
}

# Function to clean everything
clean_all() {
    print_status "Cleaning up all containers, volumes, and images..."
    docker-compose down -v --rmi all
    print_success "Cleanup completed"
}

# Function to show status
show_status() {
    print_status "Service status:"
    docker-compose ps
    
    echo ""
    print_status "Resource usage:"
    docker stats --no-stream
    
    echo ""
    print_status "Volume information:"
    docker volume ls | grep ai-chatbot
}

# Function to backup data
backup_data() {
    print_status "Creating backup..."
    
    create_backup_dir
    
    # Backup PostgreSQL database
    backup_postgres
    
    # Backup Weaviate data
    backup_weaviate
    
    # Backup application files
    backup_app
    
    print_success "Backup completed"
}

# Function to create backup directory
create_backup_dir() {
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        print_success "Created backup directory: $BACKUP_DIR"
    fi
}

# Function to backup PostgreSQL database
backup_postgres() {
    print_status "Creating PostgreSQL backup..."
    create_backup_dir
    
    if docker-compose ps postgres | grep -q "Up"; then
        docker-compose exec -T postgres pg_dump -U postgres ai_chatbot > "$BACKUP_DIR/postgres_backup_$DATE.sql"
        print_success "PostgreSQL backed up to $BACKUP_DIR/postgres_backup_$DATE.sql"
    else
        print_warning "PostgreSQL container not running, skipping backup"
    fi
}

# Function to backup Weaviate data
backup_weaviate() {
    print_status "Creating Weaviate backup..."
    create_backup_dir
    
    if docker volume ls | grep -q "ai-chatbot_weaviate_data"; then
    docker run --rm -v ai-chatbot_weaviate_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/weaviate_backup_$DATE.tar.gz -C /data .
        print_success "Weaviate backed up to $BACKUP_DIR/weaviate_backup_$DATE.tar.gz"
    else
        print_warning "Weaviate volume not found, skipping backup"
    fi
}

# Function to backup application files
backup_app() {
    print_status "Creating application backup..."
    create_backup_dir
    
    tar -czf "$BACKUP_DIR/app_backup_$DATE.tar.gz" \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='backups' \
        --exclude='logs' \
        .
    
    print_success "Application backed up to $BACKUP_DIR/app_backup_$DATE.tar.gz"
}

# Function to restore PostgreSQL database
restore_postgres() {
    local backup_file=$1
    if [ -z "$backup_file" ]; then
        print_error "Please specify a backup file to restore"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    print_status "Restoring PostgreSQL from $backup_file..."
    
    if docker-compose ps postgres | grep -q "Up"; then
        docker-compose exec -T postgres psql -U postgres -d ai_chatbot -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker-compose exec -T postgres psql -U postgres ai_chatbot < "$backup_file"
        print_success "PostgreSQL restored successfully"
    else
        print_error "PostgreSQL container not running"
        exit 1
    fi
}

# Function to restore Weaviate data
restore_weaviate() {
    local backup_file=$1
    if [ -z "$backup_file" ]; then
        print_error "Please specify a backup file to restore"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    print_status "Restoring Weaviate from $backup_file..."
    
    if docker volume ls | grep -q "ai-chatbot_weaviate_data"; then
    docker run --rm -v ai-chatbot_weaviate_data:/data -v $(pwd):/backup alpine tar xzf "/backup/$backup_file" -C /data
        print_success "Weaviate restored successfully"
    else
        print_error "Weaviate volume not found"
        exit 1
    fi
}

# Main script logic
main() {
    echo "🚀 AI Chatbot Docker Deployment"
    echo "================================"
    
    # Detect environment
    detect_environment
    
    # Check prerequisites
    check_prerequisites
    
    case "${1:-}" in
        "dev")
            start_dev
            ;;
        "prod")
            start_prod
            ;;
        "stop")
            stop_services
            ;;
        "logs")
            show_logs
            ;;
        "clean")
            clean_all
            ;;
        "status")
            show_status
            ;;
        "backup")
            backup_data
            ;;
        "restore-postgres")
            restore_postgres "$2"
            ;;
        "restore-weaviate")
            restore_weaviate "$2"
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 