import logging
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from fastapi import FastAPI
from sqlalchemy.future import select
from vilcos.config import settings

class Base(DeclarativeBase):
    pass

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.database_url.replace('postgresql://', 'postgresql+asyncpg://'),
    echo=settings.debug,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@asynccontextmanager
async def manage_db(app: FastAPI):
    """Context manager for database lifecycle management."""
    try:
        yield
    finally:
        await engine.dispose()

async def init_db() -> None:
    """Create all database tables and initialize default roles."""
    from vilcos.models import Role  # Import here to avoid circular import
    
    async with engine.begin() as conn:
        try:
            logger.info("Starting table creation")
            await conn.run_sync(Base.metadata.create_all)
            
            # Create default roles
            async with AsyncSessionLocal() as session:
                # Check if roles already exist
                result = await session.execute(select(Role).where(Role.name == "admin"))
                if not result.scalar_one_or_none():
                    default_roles = [
                        Role(name="admin", description="Administrator with full access"),
                        Role(name="user", description="Regular user with standard access")
                    ]
                    session.add_all(default_roles)
                    await session.commit()
                    
            logger.info("Table creation and initialization completed successfully")
        except Exception as e:
            logger.error(f"Error during table creation: {e}")
            raise
