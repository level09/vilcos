import logging
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from vilcos.config import settings

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
    connect_args={"statement_cache_size": 0}  # Ensure this is set to disable prepared statements cache
)

AsyncSessionMaker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    async with AsyncSessionMaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def manage_db(app):
    async with engine.begin() as conn:
        try:
            if settings.debug:
                # Drop all tables if they exist
                await conn.run_sync(Base.metadata.drop_all)
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            logger.error(f"Error managing database schema: {e}")
            raise
    yield
    await engine.dispose()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
