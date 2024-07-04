from fastapi import APIRouter
from app.api.admin.routes.user.user import router as user_router

router = APIRouter(prefix='/user', tags=['User management'])

router.include_router(user_router)
