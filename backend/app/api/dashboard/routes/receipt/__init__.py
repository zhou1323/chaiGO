from app.api.dashboard.routes.receipt.receipt import router as receipt_router
from fastapi import APIRouter

router = APIRouter(prefix="/receipts", tags=["receipt"])

router.include_router(receipt_router)
