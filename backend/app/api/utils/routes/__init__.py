from fastapi import APIRouter
from app.api.utils.routes.admin import router as admin_router

router = APIRouter(prefix='/utils', tags=['utils'])

router.include_router(admin_router)
