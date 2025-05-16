"""Dependencies module."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.config import settings
from app.infrastructure.db_connection import DbConnection
from app.crud import TaskCRUD

# Initialize database connection with settings from config
db_connection = DbConnection(
    url=settings.db.dsn,
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency.
    
    This function provides an async generator that yields database sessions.
    It's used as a FastAPI dependency for database access.
    
    Yields:
        AsyncSession: SQLAlchemy async session
        
    Note:
        The session is automatically closed after use
    """
    async for session in db_connection.session_getter():
        yield session


async def get_task_crud() -> TaskCRUD:
    """Get TaskCRUD instance dependency.
    
    This function provides a TaskCRUD instance for task operations.
    It's used as a FastAPI dependency for task-related endpoints.
    
    Returns:
        TaskCRUD: Task CRUD operations handler
    """
    return TaskCRUD()
