from fastapi import APIRouter

from app.api.api_v1.tasks import router as task_router
from app.infrastructure.config import settings

router = APIRouter()
router.include_router(task_router, prefix=settings.api_prefix.tasks)
