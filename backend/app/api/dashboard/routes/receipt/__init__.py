from app.api.dashboard.routes.receipt.receipt import router as receipt_router
from app.api.dashboard.routes.receipt.analysis import router as analysis_router
from fastapi import APIRouter

router = APIRouter(prefix="/receipts", tags=["receipt"])

router.include_router(analysis_router)
router.include_router(receipt_router)
