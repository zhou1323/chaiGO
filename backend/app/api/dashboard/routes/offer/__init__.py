from app.api.dashboard.routes.offer.offer import router as offer_router
from fastapi import APIRouter

router = APIRouter(prefix="/offers", tags=["offer"])

router.include_router(offer_router)
