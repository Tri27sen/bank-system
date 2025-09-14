from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import strawberry
from typing import List, Optional
import asyncio
import os
from databases import Database
from contextlib import asynccontextmanager

# Database configuration

# ...existing code...
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql:"
)
# ...existing code...
# Global database instance
database = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global database
    database = Database(DATABASE_URL)
    await database.connect()
    yield
    # Shutdown
    await database.disconnect()

# GraphQL Types
@strawberry.type
class Bank:
    id: int
    name: str

@strawberry.type
class Branch:
    ifsc: str
    bank_id: int
    branch: str
    address: str
    city: str
    district: str
    state: str
    bank: Optional[Bank] = None

@strawberry.type
class BranchEdge:
    node: Branch

@strawberry.type
class BranchConnection:
    edges: List[BranchEdge]
    total_count: int

# Resolvers
@strawberry.type
class Query:
    @strawberry.field
    async def banks(self) -> List[Bank]:
        """Get all banks"""
        query = "SELECT id, name FROM banks ORDER BY name"
        rows = await database.fetch_all(query)
        return [Bank(id=row["id"], name=row["name"]) for row in rows]
    
    @strawberry.field
    async def bank(self, id: int) -> Optional[Bank]:
        """Get a specific bank by ID"""
        query = "SELECT id, name FROM banks WHERE id = :id"
        row = await database.fetch_one(query, {"id": id})
        if row:
            return Bank(id=row["id"], name=row["name"])
        return None
    
    @strawberry.field
    async def branches(
        self, 
        first: Optional[int] = 100, 
        bank_name: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        ifsc: Optional[str] = None
    ) -> BranchConnection:
        """Get branches with optional filtering"""
        conditions = []
        params = {}
        
        base_query = """
        SELECT b.ifsc, b.bank_id, b.branch, b.address, b.city, 
               b.district, b.state, banks.name as bank_name, banks.id as bank_id_ref
        FROM branches b
        JOIN banks ON b.bank_id = banks.id
        """
        
        if bank_name:
            conditions.append("LOWER(banks.name) LIKE LOWER(:bank_name)")
            params["bank_name"] = f"%{bank_name}%"
        
        if city:
            conditions.append("LOWER(b.city) LIKE LOWER(:city)")
            params["city"] = f"%{city}%"
            
        if state:
            conditions.append("LOWER(b.state) LIKE LOWER(:state)")
            params["state"] = f"%{state}%"
            
        if ifsc:
            conditions.append("b.ifsc LIKE :ifsc")
            params["ifsc"] = f"%{ifsc}%"
        
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        
        # Count query
        count_query = f"""
        SELECT COUNT(*) as total
        FROM branches b
        JOIN banks ON b.bank_id = banks.id
        {where_clause}
        """
        
        # Data query with limit
        
        data_query = f"""
        {base_query}
        {where_clause}
        ORDER BY banks.name, b.branch
        LIMIT :limit
        """

        params["limit"] = first if first is not None else 100

        count_params = {k: v for k, v in params.items() if k != "limit"}
        total_result = await database.fetch_one(count_query, count_params)
        rows = await database.fetch_all(data_query, params)
        total_count = total_result["total"] if total_result else 0
        
        ###
        # Build response
        edges = []
        for row in rows:
            bank = Bank(id=row["bank_id_ref"], name=row["bank_name"])
            branch = Branch(
                ifsc=row["ifsc"],
                bank_id=row["bank_id"],
                branch=row["branch"],
                address=row["address"],
                city=row["city"],
                district=row["district"],
                state=row["state"],
                bank=bank
            )
            edges.append(BranchEdge(node=branch))
        
        return BranchConnection(edges=edges, total_count=total_count)
    
    @strawberry.field
    async def branch_by_ifsc(self, ifsc: str) -> Optional[Branch]:
        """Get a specific branch by IFSC code"""
        query = """
        SELECT b.ifsc, b.bank_id, b.branch, b.address, b.city, 
               b.district, b.state, banks.name as bank_name, banks.id as bank_id_ref
        FROM branches b
        JOIN banks ON b.bank_id = banks.id
        WHERE b.ifsc = :ifsc
        """
        
        row = await database.fetch_one(query, {"ifsc": ifsc})
        if row:
            bank = Bank(id=row["bank_id_ref"], name=row["bank_name"])
            return Branch(
                ifsc=row["ifsc"],
                bank_id=row["bank_id"],
                branch=row["branch"],
                address=row["address"],
                city=row["city"],
                district=row["district"],
                state=row["state"],
                bank=bank
            )
        return None

# Create GraphQL schema
schema = strawberry.Schema(query=Query)

# Create FastAPI app
app = FastAPI(
    title="Bank Branches API",
    description="GraphQL API for Indian Bank Branches and IFSC codes",
    version="1.0.0",
    lifespan=lifespan
)

# Add GraphQL router
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/gql")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Bank Branches API is running"}

@app.get("/")
async def root():
    return {
        "message": "Bank Branches GraphQL API",
        "graphql_endpoint": "/gql",
        "graphql_playground": "/gql (GET request for playground)"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
