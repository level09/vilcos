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


DATABASE_URL = settings.database_url.replace(
    'postgresql://', 'postgresql+asyncpg://'
) if 'postgresql://' in settings.database_url else settings.database_url

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={"statement_cache_size": 0}
)

AsyncSessionMaker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with AsyncSessionMaker() as session:
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


async def create_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
