import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from main import app
import json

# Mock database responses
MOCK_BANKS = [
    {"id": 1, "name": "State Bank of India"},
    {"id": 2, "name": "HDFC Bank"},
    {"id": 3, "name": "ICICI Bank"}
]

MOCK_BRANCHES = [
    {
        "ifsc": "SBIN0000001",
        "bank_id": 1,
        "branch": "Mumbai Main Branch",
        "address": "123 Fort Area, Mumbai",
        "city": "Mumbai",
        "district": "Mumbai",
        "state": "Maharashtra",
        "bank_name": "State Bank of India",
        "bank_id_ref": 1
    },
    {
        "ifsc": "HDFC0000001",
        "bank_id": 2,
        "branch": "Delhi Branch",
        "address": "456 CP, New Delhi",
        "city": "Delhi",
        "district": "Central Delhi",
        "state": "Delhi",
        "bank_name": "HDFC Bank",
        "bank_id_ref": 2
    }
]

@pytest_asyncio.fixture(scope="function")
async def mock_database():
    """Mock database fixture"""
    mock_db = AsyncMock()
    
    # Mock fetch_all for banks
    async def mock_fetch_all(query, params=None):
        if "FROM banks" in query:
            return MOCK_BANKS
        elif "FROM branches" in query:
            return MOCK_BRANCHES
        return []
    
    # Mock fetch_one for specific queries
    async def mock_fetch_one(query, params=None):
        if "FROM banks WHERE id" in query:
            bank_id = params.get("id", 1)
            return next((bank for bank in MOCK_BANKS if bank["id"] == bank_id), None)
        elif "FROM branches b" in query and "WHERE b.ifsc" in query:
            ifsc = params.get("ifsc", "")
            return next((branch for branch in MOCK_BRANCHES if branch["ifsc"] == ifsc), None)
        elif "COUNT(*)" in query:
            return {"total": len(MOCK_BRANCHES)}
        return None
    
    mock_db.fetch_all = mock_fetch_all
    mock_db.fetch_one = mock_fetch_one
    mock_db.connect = AsyncMock()
    mock_db.disconnect = AsyncMock()
    
    # Patch the global database variable
    with patch('main.database', mock_db):
        yield mock_db

@pytest_asyncio.fixture
async def client(mock_database):
    """Create an async test client with mocked database"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "message": "Bank Branches API is running"}

@pytest.mark.asyncio 
async def test_root_endpoint(client):
    """Test root endpoint"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "graphql_endpoint" in data

@pytest.mark.asyncio
async def test_graphql_banks_query(client):
    """Test GraphQL banks query"""
    query = """
    query {
        banks {
            id
            name
        }
    }
    """
    
    response = await client.post("/gql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "banks" in data["data"]
    assert isinstance(data["data"]["banks"], list)
    assert len(data["data"]["banks"]) > 0
    # Verify structure
    first_bank = data["data"]["banks"][0]
    assert "id" in first_bank
    assert "name" in first_bank

@pytest.mark.asyncio
async def test_graphql_branches_query(client):
    """Test GraphQL branches query with the sample format"""
    query = """
    query {
        branches {
            edges {
                node {
                    branch
                    bank {
                        name
                    }
                    ifsc
                }
            }
        }
    }
    """
    
    response = await client.post("/gql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "branches" in data["data"]
    assert "edges" in data["data"]["branches"]
    assert isinstance(data["data"]["branches"]["edges"], list)

@pytest.mark.asyncio
async def test_graphql_branch_by_ifsc(client):
    """Test GraphQL branch by IFSC query"""
    query = """
    query {
        branchByIfsc(ifsc: "SBIN0000001") {
            ifsc
            branch
            city
            state
            bank {
                name
            }
        }
    }
    """
    
    response = await client.post("/gql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "branchByIfsc" in data["data"]

@pytest.mark.asyncio
async def test_graphql_branches_with_filters(client):
    """Test GraphQL branches query with filters"""
    query = """
    query {
        branches(bankName: "HDFC", first: 10) {
            totalCount
            edges {
                node {
                    ifsc
                    branch
                    city
                    bank {
                        name
                    }
                }
            }
        }
    }
    """
    
    response = await client.post("/gql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "branches" in data["data"]

@pytest.mark.asyncio
async def test_graphql_invalid_query(client):
    """Test GraphQL with invalid query"""
    query = """
    query {
        invalidField {
            id
        }
    }
    """
    
    response = await client.post("/gql", json={"query": query})
    # GraphQL typically returns 200 with errors in the response body
    assert response.status_code == 200
    data = response.json()
    assert "errors" in data
    assert len(data["errors"]) > 0
    assert "invalidField" in data["errors"][0]["message"]

@pytest.mark.asyncio
async def test_graphql_bank_by_id(client):
    """Test GraphQL bank by ID query"""
    query = """
    query {
        bank(id: 1) {
            id
            name
        }
    }
    """
    
    response = await client.post("/gql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "bank" in data["data"]

@pytest.mark.asyncio
async def test_graphql_nonexistent_bank(client):
    """Test GraphQL query for nonexistent bank"""
    query = """
    query {
        bank(id: 999) {
            id
            name
        }
    }
    """
    
    response = await client.post("/gql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["bank"] is None

@pytest.mark.asyncio
async def test_graphql_nonexistent_branch(client):
    """Test GraphQL query for nonexistent branch"""
    query = """
    query {
        branchByIfsc(ifsc: "INVALID000") {
            ifsc
            branch
        }
    }
    """
    
    response = await client.post("/gql", json={"query": query})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["branchByIfsc"] is None