from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.config import settings
from app.infrastructure.db_connection import DbConnection
from app.crud import TaskCRUD

db_connection = DbConnection(
    url=settings.db.dsn,
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_connection.session_getter():
        yield session


async def get_task_crud() -> TaskCRUD:
    return TaskCRUD()
