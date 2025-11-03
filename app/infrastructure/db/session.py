"""Database session and engine configuration."""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.infrastructure.db.base import Base
from app.infrastructure.db import models  # noqa: F401


settings = get_settings()
engine = create_async_engine(settings.async_database_url, echo=settings.debug)
SessionFactory = async_sessionmaker(bind=engine, expire_on_commit=False)


async def init_db() -> None:
    """Create database tables if they do not exist."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a session per request."""
    async with SessionFactory() as session:
        yield session
