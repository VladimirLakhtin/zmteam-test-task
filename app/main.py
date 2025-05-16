import uvicorn
from fastapi import FastAPI

from app.api.api_v1 import router
from app.infrastructure.config import settings


main_app = FastAPI(
    title="Task Notification Service",
    description="API for managing scheduled tasks for notifications.",
    version="0.1.0",
)

main_app.include_router(router, prefix=settings.api_prefix.prefix)

if __name__ == '__main__':
    uvicorn.run(
        main_app,
        host=settings.run.host,
        port=settings.run.port,
    )
