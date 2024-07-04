from fastapi import APIRouter

from app.api.admin.routes.auth import router as auth_router
from app.api.admin.routes.user import router as user_router

router = APIRouter(tags=["Admin"])

router.include_router(auth_router)
router.include_router(user_router)
