from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from models import Base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost/stopodds")

# Production-optimized engine configuration
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "False").lower() == "true",  # Only echo in debug mode
    pool_size=5,  # Maintain 5 connections in the pool
    max_overflow=10,  # Allow up to 10 additional connections under load
    pool_pre_ping=True,  # Verify connections before using them (handles DB sleep)
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={
        "server_settings": {
            "application_name": "stopodds_api"
        },
        "timeout": 30,
        "command_timeout": 30,
    }
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()