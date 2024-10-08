from app.api.dashboard.routes.receipt import router as receipt_router
from app.api.dashboard.routes.budget import router as budget_router
from app.api.dashboard.routes.offer import router as offer_router
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user

router = APIRouter(tags=["Dashboard routes"], dependencies=[Depends(get_current_user)])

router.include_router(receipt_router)
router.include_router(budget_router)
router.include_router(offer_router)
