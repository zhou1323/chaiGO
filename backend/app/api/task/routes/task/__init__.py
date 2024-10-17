from fastapi import APIRouter
from app.api.task.routes.task.task import router as task_router

router = APIRouter(prefix="/task", tags=["Task management"])

router.include_router(task_router)
