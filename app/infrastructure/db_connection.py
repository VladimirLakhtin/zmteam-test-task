"""Database connection module."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
)


class DbConnection:
    """Database connection manager.
    
    This class manages database connections using SQLAlchemy's async engine
    and session factory. It provides methods for session creation and
    connection disposal.
    
    Attributes:
        engine (AsyncEngine): SQLAlchemy async engine instance
        session_factory (async_sessionmaker): Async session factory
    """
    
    def __init__(
        self,
        url: str,
        echo: bool = False,
        echo_pool: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        """Initialize database connection manager.
        
        Args:
            url (str): Database connection URL
            echo (bool): Enable SQL query logging
            echo_pool (bool): Enable connection pool logging
            pool_size (int): Size of the connection pool
            max_overflow (int): Maximum number of connections that can be created
                              beyond the pool size
        """
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        """Dispose of the database engine and close all connections."""
        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session.
        
        Yields:
            AsyncSession: SQLAlchemy async session
        """
        async with self.session_factory() as session:
            yield session
