from fastapi import APIRouter
from app.api.dashborad.routes.receipt.receipt import router as receipt_router

router = APIRouter(prefix='/items', tags=["receipt"])

router.include_router(receipt_router)
