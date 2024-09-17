from app.api.admin.routes import router as admin_router
from app.api.dashboard.routes import router as dashboard_router
from app.api.task.routes import router as task_router
from app.api.utils.routes import router as utils_router
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(admin_router)
api_router.include_router(dashboard_router)
api_router.include_router(utils_router)
api_router.include_router(task_router)
