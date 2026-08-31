"""
Database Connection & Session Management
Supports async PostgreSQL (production) and SQLite (testing/local dev).
"""
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from config.settings import settings
from app.database.models import Base

logger = logging.getLogger(__name__)

# Normalize database URL for async drivers and strip any whitespace/newlines
db_url = settings.DATABASE_URL.strip()
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif db_url.startswith("sqlite://") and not db_url.startswith("sqlite+aiosqlite://"):
    db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

# Connection engine
connect_args = {}
if "sqlite" in db_url:
    connect_args = {"check_same_thread": False}

engine: AsyncEngine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    connect_args=connect_args,
    pool_pre_ping=True
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


async def init_db() -> None:
    """Initialize database tables idempotently."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for providing an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
