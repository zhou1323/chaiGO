from app.api.dashboard.routes.receipt import router as receipt_router
from fastapi import APIRouter

router = APIRouter(tags=["Dashboard routes"])

router.include_router(receipt_router)
