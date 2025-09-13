
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Mock database for testing
@pytest.fixture(autouse=True)
async def mock_database():
    """Mock database responses for testing"""
    
    mock_banks = [
        {"id": 1, "name": "State Bank of India"},
        {"id": 2, "name": "HDFC Bank"},
        {"id": 3, "name": "ICICI Bank"}
    ]
    
    mock_branches = [
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
    
    async def mock_fetch_all(query, params=None):
        if "banks" in query and "branches" not in query:
            return mock_banks
        elif "branches" in query:
            return mock_branches
        return []
    
    async def mock_fetch_one(query, params=None):
        if "COUNT" in query:
            return {"total": len(mock_branches)}
        elif "banks" in query:
            return mock_banks[0]
        elif "branches" in query:
            return mock_branches[0]
        return None
    
    async def mock_connect():
        pass
    
    async def mock_disconnect():
        pass
    
    with patch('main.database') as mock_db:
        mock_db.fetch_all = mock_fetch_all
        mock_db.fetch_one = mock_fetch_one
        mock_db.connect = mock_connect
        mock_db.disconnect = mock_disconnect
        yield mock_db
