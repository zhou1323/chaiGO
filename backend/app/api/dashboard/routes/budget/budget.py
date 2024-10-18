from typing import Any, Annotated
import uuid

from app.api.admin.model.token import Message
from app.api.dashboard.model.budget import (
    Budget,
    BudgetCreate,
    BudgetUpdate,
    BudgetDelete,
)
from app.api.dashboard.service.budget_service import budget_service
from app.api.deps import CurrentUser, SessionDep
from app.common.response.response_schema import ResponseModel
from app.common.response.response_schema import response_base
from fastapi import APIRouter, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from datetime import datetime

router = APIRouter()


@router.get("/list")
async def get_budgets_list(
    session: SessionDep,
    current_user: CurrentUser,
    start_date: Annotated[str | None, Query(alias="startDate")] = None,
    end_date: Annotated[str | None, Query(alias="endDate")] = None,
    order_by: Annotated[str | None, Query(alias="orderBy")] = None,
    order_type: Annotated[str | None, Query(alias="orderType")] = None,
) -> Page[Budget]:
    statement = budget_service.get_budget_list_statement(
        session=session,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        order_by=order_by,
        order_type=order_type,
    )
    return paginate(session, statement)


@router.get("/current")
async def get_budget(session: SessionDep, current_user: CurrentUser) -> ResponseModel:
    budget = budget_service.get_current_budget(
        session=session, current_user=current_user
    )
    return await response_base.success(data=budget)


@router.post("/budget")
async def create_budget(
    *, session: SessionDep, current_user: CurrentUser, budget_in: BudgetCreate
) -> ResponseModel:
    budget = budget_service.create_budget(
        session=session, current_user=current_user, budget_in=budget_in
    )
    return await response_base.success(data=budget)


@router.put("/budget/{id}")
async def update_budget(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    budget_in: BudgetUpdate
) -> ResponseModel:
    budget = budget_service.update_budget(
        session=session, current_user=current_user, id=id, budget_in=budget_in
    )
    return await response_base.success(data=budget)


@router.delete("/budget")
async def delete_budgets(
    session: SessionDep, current_user: CurrentUser, budgets_to_delete: BudgetDelete
) -> Message:
    budget_service.delete_budgets(
        session=session,
        current_user=current_user,
        budgets_to_delete=budgets_to_delete,
    )
    return await response_base.success()


@router.get("/overview")
async def get_budgets_overview(
    session: SessionDep, current_user: CurrentUser
) -> ResponseModel:
    overview = budget_service.get_budgets_overview(
        session=session, current_user=current_user
    )
    return await response_base.success(data=overview)
