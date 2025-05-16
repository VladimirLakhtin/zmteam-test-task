"""API v1 router initialization module."""

from fastapi import APIRouter, Depends

from app.api.api_v1.tasks import router as task_router
from app.auth import get_current_user
from app.infrastructure.config import settings

router = APIRouter(dependencies=[Depends(get_current_user)])
router.include_router(task_router, prefix=settings.api_prefix.tasks)
