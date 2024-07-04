from typing import Any

from fastapi import APIRouter, HTTPException, Depends

from app.api.dashborad.service.receipt_service import item_service
from app.api.deps import CurrentUser, SessionDep
from app.api.admin.model.token import Message
from app.api.dashborad.model.receipt import ItemsPublic, Item, ItemPublic, ItemCreate, ItemUpdate

router = APIRouter()


@router.get("/", response_model=ItemsPublic)
def read_items(session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100) -> Any:
    return item_service.read_items(session, current_user, skip, limit)


@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    return item_service.read_item(session, current_user, id)


@router.post("/", response_model=ItemPublic)
def create_item(*, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate) -> Any:
    return item_service.create_item(session, current_user, item_in)


@router.put("/{id}", response_model=ItemPublic)
def update_item(*, session: SessionDep, current_user: CurrentUser, id: int, item_in: ItemUpdate) -> Any:
    return item_service.update_item(session, current_user, id, item_in)


@router.delete("/{id}")
def delete_item(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    return item_service.delete_item(session, current_user, id)
