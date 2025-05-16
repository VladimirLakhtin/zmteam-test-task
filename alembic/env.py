import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import pool, create_engine # create_engine for offline mode with sync URL if needed, or adjust offline mode

from alembic import context

# Import your app's settings and Base metadata
from app.infrastructure.config import settings # Adjust path if necessary
from app.models.base import Base # Adjust path if your Base is elsewhere

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target_metadata for 'autogenerate' support
target_metadata = Base.metadata

# Use your application's database URL from settings
DB_URL = settings.db.dsn

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # For offline mode, Alembic expects a synchronous URL if it's doing the connect itself.
    # If your DSN is async, you might need to adapt it or use a separate sync DSN for offline mode if strictly needed.
    # However, most of the time, you'll be running in online mode.
    context.configure(
        url=DB_URL, # Using the DSN directly
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(
        connection=connection, 
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = AsyncEngine(create_engine(DB_URL, poolclass=pool.NullPool, echo=settings.db.echo))

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
