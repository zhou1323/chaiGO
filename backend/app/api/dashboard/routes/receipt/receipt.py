from typing import Any, Annotated
import uuid

from app.api.admin.model.token import Message
from app.api.dashboard.model.receipt import (
    ReceiptPublic,
    ReceiptCreate,
    ReceiptUpdate,
    ReceiptDelete,
)
from app.api.dashboard.service.receipt_service import receipt_service
from app.api.deps import CurrentUser, SessionDep
from app.common.response.response_schema import ResponseModel
from app.common.response.response_schema import response_base
from fastapi import APIRouter, Query
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from datetime import datetime

router = APIRouter()


@router.get("/list")
def get_receipts_list(
    session: SessionDep,
    current_user: CurrentUser,
    description: str | None = None,
    category: str | None = None,
    start_date: Annotated[datetime | None, Query(alias="startDate")] = None,
    end_date: Annotated[datetime | None, Query(alias="endDate")] = None,
    order_by: Annotated[str | None, Query(alias="orderBy")] = None,
    order_type: Annotated[str | None, Query(alias="orderType")] = None,
) -> Page[ReceiptPublic]:
    statement = receipt_service.get_receipts_list(
        session=session,
        current_user=current_user,
        description=description,
        category=category,
        start_date=start_date,
        end_date=end_date,
        order_by=order_by,
        order_type=order_type,
    )
    return paginate(session, statement)


@router.get("/{id}")
async def get_receipt(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> ResponseModel:
    receipt = receipt_service.get_receipt(session=session, id=id)
    return await response_base.success(data=receipt)


@router.post("/")
async def create_receipt(
    *, session: SessionDep, current_user: CurrentUser, receipt_in: ReceiptCreate
) -> ResponseModel:
    receipt = receipt_service.create_receipt(
        session=session, current_user=current_user, receipt_in=receipt_in
    )
    return await response_base.success(data=receipt)


@router.put("/{id}")
async def update_receipt(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    receipt_in: ReceiptUpdate
) -> ResponseModel:
    receipt = receipt_service.update_receipt(
        session=session, current_user=current_user, id=id, receipt_in=receipt_in
    )
    return await response_base.success(data=receipt)


@router.delete("/")
async def delete_receipts(
    session: SessionDep, current_user: CurrentUser, receipts_to_delete: ReceiptDelete
) -> Message:
    receipt_service.delete_receipts(
        session=session,
        current_user=current_user,
        receipts_to_delete=receipts_to_delete,
    )
    return await response_base.success()
