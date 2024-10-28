# vilcos/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from vilcos.config import settings
from vilcos.models import Table  # Import models at the top

# Use asyncpg for async database connection
SQLALCHEMY_DATABASE_URL = settings.database_url.replace('postgresql://', 'postgresql+asyncpg://')

# Create an async engine and session
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Base class for declarative models
Base = declarative_base()

# Dependency for getting a database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Function to create tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
