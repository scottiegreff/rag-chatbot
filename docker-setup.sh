#!/bin/bash

# FCI Chatbot Docker Setup Script

set -e

echo "🚀 FCI Chatbot Docker Setup"
echo "============================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if model files exist
if [ ! -f "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf" ]; then
    echo "⚠️  Warning: Model file not found at models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    echo "   Please ensure you have the model files in the models/ directory"
    echo "   You can download them from Hugging Face or use your existing models"
fi

# Check if database schema files exist
if [ ! -f "ecommerce_schema.sql" ]; then
    echo "⚠️  Warning: ecommerce_schema.sql not found"
    echo "   The database will be created with basic tables only"
fi

echo ""
echo "✅ Prerequisites check completed"
echo ""

# Function to show usage
show_usage() {
    echo "Usage:"
    echo "  $0 [dev|prod|stop|clean|logs]"
    echo ""
    echo "Commands:"
    echo "  dev     - Start development environment (with hot reload)"
    echo "  prod    - Start production environment"
    echo "  stop    - Stop all containers"
    echo "  clean   - Stop and remove all containers, volumes, and images"
    echo "  logs    - Show logs from all services"
    echo ""
    echo "Examples:"
    echo "  $0 dev     # Start development environment"
    echo "  $0 prod    # Start production environment"
    echo "  $0 stop    # Stop all services"
    echo "  $0 clean   # Clean up everything"
}

# Function to start development environment
start_dev() {
    echo "🔧 Starting development environment..."
    docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build
}

# Function to start production environment
start_prod() {
    echo "🚀 Starting production environment..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
    echo ""
    echo "✅ Production environment started!"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   Database: localhost:5432"
    echo ""
    echo "To view logs: $0 logs"
    echo "To stop: $0 stop"
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping all services..."
    docker-compose down
    echo "✅ Services stopped"
}

# Function to clean everything
clean_all() {
    echo "🧹 Cleaning up all containers, volumes, and images..."
    docker-compose down -v --rmi all
    echo "✅ Cleanup completed"
}

# Function to show logs
show_logs() {
    echo "📋 Showing logs from all services..."
    docker-compose logs -f
}

# Main script logic
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
    "clean")
        clean_all
        ;;
    "logs")
        show_logs
        ;;
    *)
        show_usage
        ;;
esac 