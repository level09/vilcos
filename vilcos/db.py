import logging
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from vilcos.config import settings
from typing import AsyncGenerator
from fastapi import FastAPI

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


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
    """Create all database tables."""
    async with engine.begin() as conn:
        try:
            logger.info("Starting table creation")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Table creation completed successfully")
        except Exception as e:
            logger.error(f"Error during table creation: {e}")
            raise
