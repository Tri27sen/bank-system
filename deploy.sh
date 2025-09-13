#!/bin/bash

# Bank API Deployment Script
set -e

echo "🚀 Starting Bank API deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

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

# Parse command line arguments
ENVIRONMENT=${1:-production}

case $ENVIRONMENT in
    "dev"|"development")
        print_status "Deploying in DEVELOPMENT mode..."
        COMPOSE_FILE="docker-compose.dev.yml"
        ;;
    "prod"|"production")
        print_status "Deploying in PRODUCTION mode..."
        COMPOSE_FILE="docker-compose.prod.yml"
        
        # Check if .env file exists for production
        if [ ! -f .env ]; then
            print_warning "No .env file found. Creating from .env.example..."
            cp .env.example .env
            print_warning "Please edit .env file with your production settings!"
        fi
        ;;
    *)
        print_error "Invalid environment: $ENVIRONMENT"
        echo "Usage: $0 [dev|development|prod|production]"
        exit 1
        ;;
esac

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f $COMPOSE_FILE down 2>/dev/null || true

# Build the application
print_status "Building Docker images..."
docker-compose -f $COMPOSE_FILE build

# Start the application
print_status "Starting containers..."
docker-compose -f $COMPOSE_FILE up -d

# Wait for application to start
print_status "Waiting for application to start..."
sleep 10

# Health check
print_status "Performing health check..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "✅ Application is running successfully!"
    print_status "🌐 API available at: http://localhost:8000"
    print_status "🔍 GraphQL Playground at: http://localhost:8000/gql"
    print_status "📊 Health check: http://localhost:8000/health"
else
    print_error "❌ Application failed to start properly"
    print_status "Checking logs..."
    docker-compose -f $COMPOSE_FILE logs bank-api
    exit 1
fi

# Show running containers
print_status "Running containers:"
docker-compose -f $COMPOSE_FILE ps

print_status "🎉 Deployment completed successfully!"

# Provide helpful commands
echo ""
echo "Useful commands:"
echo "  View logs:     docker-compose -f $COMPOSE_FILE logs -f"
echo "  Stop app:      docker-compose -f $COMPOSE_FILE down"
echo "  Restart:       docker-compose -f $COMPOSE_FILE restart"
echo "  Shell access:  docker-compose -f $COMPOSE_FILE exec bank-api /bin/bash"