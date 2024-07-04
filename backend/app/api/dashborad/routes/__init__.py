from fastapi import APIRouter

from app.api.dashborad.routes.receipt import router as receipt_router

router = APIRouter(tags=['Dashboard routes'])

router.include_router(receipt_router)
