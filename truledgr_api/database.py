"""Database configuration and session management (async-first)."""

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .config import settings


# Create async engine (primary)
async_engine = create_async_engine(
    settings.database_url,  # Already async by default
    echo=settings.debug,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

# Create sync engine (fallback/compatibility)
engine = create_engine(
    settings.sync_database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

# Create sessionmaker for async sessions
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def create_db_and_tables():
    """Create database tables (async)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


def create_db_and_tables_sync():
    """Create database tables (sync fallback)."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get a database session (sync)."""
    with Session(engine) as session:
        yield session


async def get_async_session():
    """Get an async database session."""
    async with AsyncSessionLocal() as session:
        yield session


# Database dependency for FastAPI
def get_db():
    """FastAPI dependency for database session."""
    with Session(engine) as session:
        yield session


async def get_async_db():
    """FastAPI dependency for async database session."""
    async with AsyncSessionLocal() as session:
        yield session
