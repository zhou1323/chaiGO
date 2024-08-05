from app.api.dashboard.routes.budget.budget import router as budget_router
from fastapi import APIRouter

router = APIRouter(prefix="/budgets", tags=["budget"])

router.include_router(budget_router)
