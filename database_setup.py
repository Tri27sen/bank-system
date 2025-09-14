import asyncio
import asyncpg
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://AutoBox_owner:SUhkErJ4KH0u@ep-tight-art-a50hk2av-pooler.us-east-2.aws.neon.tech/bank?sslmode=require&channel_binding=require")

async def setup_database():
    """Create tables and insert sample data"""
    
    # Connect to database
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Create banks table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS banks (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE
            );
        ''')
        
        # Create branches table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS branches (
                ifsc VARCHAR(11) PRIMARY KEY,
                bank_id INTEGER REFERENCES banks(id),
                branch VARCHAR(200) NOT NULL,
                address TEXT,
                city VARCHAR(100),
                district VARCHAR(100),
                state VARCHAR(100)
            );
        ''')
        
        # Create bank_branches view
        await conn.execute('''
            CREATE OR REPLACE VIEW bank_branches AS
            SELECT 
                b.ifsc,
                b.branch,
                b.address,
                b.city,
                b.district,
                b.state,
                banks.name as bank_name,
                banks.id as bank_id
            FROM branches b
            JOIN banks ON b.bank_id = banks.id;
        ''')
        
        # Insert sample banks (if not exists)
        sample_banks = [
            "State Bank of India",
            "HDFC Bank",
            "ICICI Bank", 
            "Axis Bank",
            "Punjab National Bank",
            "Bank of Baroda",
            "Kotak Mahindra Bank"
        ]
        
        for bank_name in sample_banks:
            await conn.execute(
                "INSERT INTO banks (name) VALUES ($1) ON CONFLICT (name) DO NOTHING",
                bank_name
            )
        
        # Insert sample branches (if not exists)
        sample_branches = [
            ("SBIN0000001", 1, "Mumbai Main Branch", "123 Fort Area, Mumbai", "Mumbai", "Mumbai", "Maharashtra"),
            ("HDFC0000001", 2, "Delhi Branch", "456 CP, New Delhi", "Delhi", "Central Delhi", "Delhi"),
            ("ICIC0000001", 3, "Bangalore Branch", "789 MG Road, Bangalore", "Bangalore", "Bangalore Urban", "Karnataka"),
            ("UTIB0000001", 4, "Chennai Branch", "321 Anna Salai, Chennai", "Chennai", "Chennai", "Tamil Nadu"),
            ("PUNB0000001", 5, "Chandigarh Branch", "654 Sector 17, Chandigarh", "Chandigarh", "Chandigarh", "Chandigarh"),
            ("BARB0000001", 6, "Ahmedabad Branch", "987 CG Road, Ahmedabad", "Ahmedabad", "Ahmedabad", "Gujarat"),
            ("KKBK0000001", 7, "Pune Branch", "147 FC Road, Pune", "Pune", "Pune", "Maharashtra")
        ]
        
        for branch_data in sample_branches:
            await conn.execute(
                """INSERT INTO branches (ifsc, bank_id, branch, address, city, district, state) 
                   VALUES ($1, $2, $3, $4, $5, $6, $7) ON CONFLICT (ifsc) DO NOTHING""",
                *branch_data
            )
        
        print("Database setup completed successfully!")
        print(f"Created tables: banks, branches")
        print(f"Created view: bank_branches")
        print(f"Inserted {len(sample_banks)} banks and {len(sample_branches)} branches")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(setup_database())
