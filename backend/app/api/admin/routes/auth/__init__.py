from fastapi import APIRouter
from app.api.admin.routes.auth.auth import router as auth_router
from app.api.admin.routes.auth.captcha import router as captcha_router
from app.api.admin.routes.auth.aws import router as aws_router

router = APIRouter(prefix="/auth", tags=["Auth management"])

router.include_router(auth_router)
router.include_router(captcha_router, prefix="/captcha")
router.include_router(aws_router, prefix="/aws")
