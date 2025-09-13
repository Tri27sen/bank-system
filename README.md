# Bank Branches GraphQL API

A **FastAPI** + **Strawberry GraphQL** service to query **Indian Bank branches and IFSC codes**.  
The API provides structured GraphQL queries for fetching bank details, branch information, and IFSC-based lookups.

---

##  Features
- Built with **FastAPI** (async, lightweight, high-performance)
- **GraphQL API** powered by Strawberry
- Query banks, branches, and IFSC codes
- Supports filtering branches by:
  - Bank name
  - City
  - State
  - IFSC code
- Pagination support with `first` parameter
- Includes a `/health` endpoint for service checks
- GraphQL Playground available at `/gql`

---

##  Project Structure
  - **main.py** # Application entrypoint (FastAPI + GraphQL)
  - **requirements.txt** # Python dependencies
  - **docker-compose.yml** # Docker setup 
  - **test-api** # for testing 

## API Endpoints

- **GraphQL Playground: http://localhost:8000/gql**
- **Health Check: http://localhost:8000/health**
- **API Documentation: http://localhost:8000/docs (FastAPI auto-generated)**
# Bank Branches GraphQL API

A FastAPI-based GraphQL API for querying Indian bank branches and IFSC codes. This API provides comprehensive information about banks and their branches across India.

## Features

- **GraphQL API** with interactive playground
- **Bank Management** - Query all banks or specific banks by ID
- **Branch Search** - Advanced filtering by bank name, city, state, and IFSC code
- **IFSC Lookup** - Direct branch lookup by IFSC code
- **PostgreSQL Integration** - Robust database backend
- **Docker Ready** - Containerized deployment

## API Endpoints

- **GraphQL Playground**: `http://localhost:8000/gql`
- **Health Check**: `http://localhost:8000/health`
- **API Documentation**: `http://localhost:8000/docs` (FastAPI auto-generated)

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Strawberry GraphQL** - Python GraphQL library
- **PostgreSQL** - Database backend
- **Docker** - Containerization
- **Uvicorn** - ASGI server

### To  Run with Docker Compose

```bash
# Build and start the application
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

The API will be available at:
- GraphQL Playground: http://localhost:8000/gql
- Health Check: http://localhost:8000/health

## Docker Commands

### Development Mode (with hot reload)

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# Or use Makefile
make dev
```

### Production Deployment

```bash
# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Or use deployment script
chmod +x deploy.sh
./deploy.sh prod
```

### Useful Docker Commands

```bash
# View logs
docker-compose logs -f bank-api

# Access container shell
docker-compose exec bank-api /bin/bash

# Stop containers
docker-compose down

# Rebuild and restart
docker-compose up --build

# Run tests in container
docker-compose exec bank-api pytest test_config.py -v
```

### Makefile Commands

A Makefile is included for convenience:

```bash
make help      # Show available commands
make build     # Build Docker image
make run       # Run in production mode
make dev       # Run in development mode
make stop      # Stop all containers
make clean     # Clean up containers and images
make test      # Run tests
make logs      # Show application logs
make shell     # Open shell in container
```

## Manual Installation (without Docker)

### Prerequisites

- Python 3.9+
- PostgreSQL database

### Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://username:password@host:port/database"

# Run the application
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## GraphQL Schema

### Available Queries

#### Get All Banks
```graphql
query {
  banks {
    id
    name
  }
}
```

#### Get Bank by ID
```graphql
query {
  bank(id: 1) {
    id
    name
  }
}
```

#### Search Branches with Filters
```graphql
query {
  branches(
    first: 10
    bankName: "State Bank"
    city: "Mumbai"
    state: "Maharashtra"
  ) {
    edges {
      node {
        ifsc
        branch
        address
        city
        state
        bank {
          name
        }
      }
    }
    totalCount
  }
}
```

#### Get Branch by IFSC
```graphql
query {
  branchByIfsc(ifsc: "SBIN0001234") {
    ifsc
    branch
    address
    city
    district
    state
    bank {
      id
      name
    }
  }
}
```

## Database Schema

### Banks Table
- `id` (Primary Key) - Auto-incrementing bank ID
- `name` - Bank name (unique)

### Branches Table
- `ifsc` (Primary Key) - 11-character IFSC code
- `bank_id` - Foreign key to banks table
- `branch` - Branch name
- `address` - Branch address
- `city` - City name
- `district` - District name
- `state` - State name

## Testing

### Running Tests with Docker

```bash
# Run all tests
docker-compose exec bank-api pytest test_config.py -v

# Run specific test class
docker-compose exec bank-api pytest test_config.py::TestBanksQuery -v

# Run with coverage
docker-compose exec bank-api pytest test_config.py --cov=main
```

### Running Tests Locally

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest test_api.py -v
```

## Deployment : https://bank-system-qzx84wzyb-trisha-senguptas-projects.vercel.app/


## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GraphQL API   │────│   FastAPI App    │────│   PostgreSQL    │
│  (Strawberry)   │    │                  │    │    Database     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
    ┌─────────┐            ┌─────────────┐         ┌─────────────┐
    │ Client  │            │  Docker     │         │  Database   │
    │ Apps    │            │ Container   │         │  Connection │
    └─────────┘            └─────────────┘         └─────────────┘
```
