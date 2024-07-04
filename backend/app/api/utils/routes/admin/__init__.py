from fastapi import APIRouter
from app.api.utils.routes.admin.email import router as email_router

router = APIRouter(tags=['Admin related'])
router.include_router(email_router)