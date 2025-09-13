

import asyncio
import asyncpg
import pandas as pd  # or use csv module
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://AutoBox_owner:SUhkErJ4KH0u@ep-tight-art-a50hk2av-pooler.us-east-2.aws.neon.tech/bank?sslmode=require&channel_binding=require"
)

async def reset_and_load_csv():
    """Clear existing data and load from CSV"""
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        print("Clearing existing data...")
        
        # Delete existing data (foreign key constraint aware)
        await conn.execute("DELETE FROM branches")
        await conn.execute("DELETE FROM banks")
        
        # Reset sequences to start from 1
        await conn.execute("ALTER SEQUENCE banks_id_seq RESTART WITH 1")
        
        print("Loading data from bank_branches.csv...")
        
        # Load CSV data
        df = pd.read_csv('bank_branches.csv')
        
        # Extract unique banks and insert them
        unique_banks = df['bank_name'].unique()
        bank_id_map = {}
        
        for bank_name in unique_banks:
            result = await conn.fetchrow(
                "INSERT INTO banks (name) VALUES ($1) RETURNING id",
                bank_name
            )
            bank_id_map[bank_name] = result['id']
        
        # Insert branches from CSV
        for _, row in df.iterrows():
            bank_id = bank_id_map[row['bank_name']]
            await conn.execute(
                """INSERT INTO branches (ifsc, bank_id, branch, address, city, district, state) 
                   VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                row['ifsc'], bank_id, row['branch'], 
                row.get('address', ''), row.get('city', ''), 
                row.get('district', ''), row.get('state', '')
            )
        
        print(f"Successfully loaded {len(unique_banks)} banks and {len(df)} branches from CSV")
        
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(reset_and_load_csv()) 