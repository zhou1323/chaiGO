from fastapi import APIRouter

from app.api.task.routes.task import router as task_router

router = APIRouter(tags=["Task"])

router.include_router(task_router)
