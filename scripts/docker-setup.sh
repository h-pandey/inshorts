#!/bin/bash

# Docker setup script for Contextual News API
# This script helps set up and manage the Docker environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Function to create .env file if it doesn't exist
create_env_file() {
    if [ ! -f .env ]; then
        print_status "Creating .env file from template..."
        cp env.example .env
        print_warning "Please update .env file with your OpenAI API key and other configuration"
        print_warning "At minimum, set: OPENAI_API_KEY=your_key_here"
    else
        print_success ".env file already exists"
    fi
}

# Function to build and start services
start_services() {
    local mode=${1:-production}
    
    print_status "Starting services in $mode mode..."
    
    if [ "$mode" = "development" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
    else
        docker-compose up --build -d
    fi
    
    print_success "Services started successfully"
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    docker-compose down
    print_success "Services stopped"
}

# Function to show logs
show_logs() {
    local service=${1:-app}
    print_status "Showing logs for $service service..."
    docker-compose logs -f "$service"
}

# Function to check service health
check_health() {
    print_status "Checking service health..."
    
    # Wait for services to be ready
    sleep 10
    
    # Check app health
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "Application is healthy"
    else
        print_error "Application health check failed"
    fi
    
    # Check MongoDB
    if docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')" &> /dev/null; then
        print_success "MongoDB is healthy"
    else
        print_error "MongoDB health check failed"
    fi
    
    # Check Redis
    if docker-compose exec redis redis-cli ping &> /dev/null; then
        print_success "Redis is healthy"
    else
        print_error "Redis health check failed"
    fi
}

# Function to show service URLs
show_urls() {
    print_status "Service URLs:"
    echo "  📊 Application: http://localhost:8000"
    echo "  📚 API Docs: http://localhost:8000/docs"
    echo "  🔍 Health Check: http://localhost:8000/health"
    echo "  🗄️  MongoDB Admin: http://localhost:8081 (admin/admin123)"
    echo "  🔴 Redis Admin: http://localhost:8082 (admin/admin123)"
    echo ""
    print_status "Database Connection Details:"
    echo "  MongoDB: mongodb://admin:password123@localhost:27017/news_db?authSource=admin"
    echo "  Redis: redis://:redis123@localhost:6379"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "Docker Setup Script for Contextual News API"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start [dev|prod]  Start services (default: prod)"
    echo "  stop             Stop services"
    echo "  restart          Restart services"
    echo "  logs [service]   Show logs (default: app)"
    echo "  health           Check service health"
    echo "  urls             Show service URLs"
    echo "  cleanup          Clean up Docker resources"
    echo "  help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start dev     Start in development mode"
    echo "  $0 logs mongodb  Show MongoDB logs"
    echo "  $0 health        Check all services"
}

# Main script logic
main() {
    case "${1:-help}" in
        "start")
            check_docker
            create_env_file
            start_services "${2:-production}"
            check_health
            show_urls
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            start_services "${2:-production}"
            check_health
            show_urls
            ;;
        "logs")
            show_logs "$2"
            ;;
        "health")
            check_health
            ;;
        "urls")
            show_urls
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"
