from __future__ import annotations

import os
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# Configure the database URL before importing the application
TEST_DB_PATH = Path("test.db")
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"
os.environ.setdefault("API_MAPBOX_DATABASE_URL", TEST_DB_URL)

from app.infrastructure.db import session as db_session
from app.infrastructure.db.base import Base
from app.infrastructure.db.session import get_session
from app.main import app


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL)
    db_session.engine = engine
    db_session.SessionFactory = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest_asyncio.fixture(autouse=True)
async def clean_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture()
async def client(test_engine):
    async def override_get_session():
        async with db_session.SessionFactory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
