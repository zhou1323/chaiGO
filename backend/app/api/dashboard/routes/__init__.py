from app.api.dashboard.routes.receipt import router as receipt_router
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user

router = APIRouter(tags=["Dashboard routes"], dependencies=[Depends(get_current_user)])

router.include_router(receipt_router)
