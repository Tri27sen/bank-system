# Makefile for Bank API Docker operations

.PHONY: help build run stop clean dev prod test logs shell

# Default target
help:
	@echo "Available commands:"
	@echo "  build     - Build the Docker image"
	@echo "  run       - Run the application in production mode"
	@echo "  dev       - Run the application in development mode"
	@echo "  stop      - Stop all containers"
	@echo "  clean     - Stop containers and remove images"
	@echo "  test      - Run tests in container"
	@echo "  logs      - Show application logs"
	@echo "  shell     - Open shell in running container"

# Build the Docker image
build:
	docker-compose build

# Run in production mode
run:
	docker-compose up -d

# Run in development mode with hot reload
dev:
	docker-compose -f docker-compose.dev.yml up

# Stop all containers
stop:
	docker-compose down
	docker-compose -f docker-compose.dev.yml down

# Clean up containers and images
clean: stop
	docker-compose down --rmi all --volumes
	docker system prune -f

# Run tests
test:
	docker-compose exec bank-api pytest test_config.py -v

# Show logs
logs:
	docker-compose logs -f bank-api

# Open shell in container
shell:
	docker-compose exec bank-api /bin/bash

# Build and run in one command
up: build run

# Development setup
dev-setup:
	@echo "Setting up development environment..."
	docker-compose -f docker-compose.dev.yml build
	docker-compose -f docker-compose.dev.yml up -d

# Production deployment
deploy:
	@echo "Deploying to production..."
	docker-compose -f docker-compose.prod.yml build
	docker-compose -f docker-compose.prod.yml up -d