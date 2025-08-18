"""
Fix database schema for model_type column
"""

import asyncio
from database import AsyncSessionLocal
from sqlalchemy import text

async def fix_schema():
    """Fix the model_type column to accept VARCHAR"""
    print("Fixing database schema...")
    
    async with AsyncSessionLocal() as db:
        try:
            # Drop the enum constraint if it exists
            await db.execute(text("ALTER TABLE model_runs ALTER COLUMN model_type TYPE VARCHAR;"))
            await db.commit()
            print("Successfully updated model_type column to VARCHAR")
        except Exception as e:
            print(f"Schema update failed (might already be correct): {e}")
            await db.rollback()
        
        # Verify the change
        try:
            result = await db.execute(text("SELECT data_type FROM information_schema.columns WHERE table_name = 'model_runs' AND column_name = 'model_type';"))
            data_type = result.scalar()
            print(f"Current model_type data type: {data_type}")
        except Exception as e:
            print(f"Could not verify schema: {e}")

if __name__ == "__main__":
    asyncio.run(fix_schema())