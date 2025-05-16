"""Test configuration and fixtures module."""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.auth import get_current_user
from app.crud import TaskCRUD
from app.dependencies import get_db_session
from app.infrastructure.config import settings
from app.main import main_app
from app.models.base import Base
from app.schemas import TokenData, TaskCreate

TEST_DATABASE_URL = f'postgresql+asyncpg://{settings.db.user}:{settings.db.password}@localhost:5434/zmteam_test'

test_engine = create_async_engine(TEST_DATABASE_URL, echo=settings.db.echo)
test_async_session_maker = async_sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)


async def override_get_current_user() -> TokenData:
    """This mock allows tests to bypass actual JWT validation"""
    return TokenData(username="testuser")


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
async def setup_test_database():
    """Create database tables before tests and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await test_engine.dispose()


@pytest.fixture(scope="function")  # "function" scope for DB session to ensure isolation between tests
async def db_session(setup_test_database: None) -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for a test."""
    async with test_async_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncClient:
    """Get an TestClient instance that uses the test_db."""
    main_app.dependency_overrides[get_db_session] = lambda: db_session
    main_app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(
            transport=ASGITransport(app=main_app),
            base_url="http://testserver",
    ) as ac:
        yield ac

    main_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_tasks(db_session: AsyncSession) -> list[dict]:
    """Create test tasks and authentication token."""
    task_crud = TaskCRUD()
    tasks_data = [
        {
            "id": 1,
            "datetime_to_do": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "task_info": "Test task 1"
        },
        {
            "id": 2,
            "datetime_to_do": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "task_info": "Test task 2"
        }
    ]

    for task_data in tasks_data:
        await task_crud.create(db_session, TaskCreate(**task_data))

    return tasks_data
