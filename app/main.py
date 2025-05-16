"""Main application module."""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api.api_v1 import router
from app.dependencies import db_connection
from app.infrastructure.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    yield
    await db_connection.dispose()


main_app = FastAPI(
    title="Task Notification Service",
    description="API for managing scheduled tasks for notifications.",
    version="0.1.0",
    lifespan=lifespan,
)

main_app.include_router(router, prefix=settings.api_prefix.api)

if __name__ == '__main__':
    uvicorn.run(
        main_app,
        host=settings.run.host,
        port=settings.run.port,
    )
