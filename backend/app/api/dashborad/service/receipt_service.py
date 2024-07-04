from typing import Any
from fastapi import HTTPException
from sqlmodel import func, select, delete

from app.api.admin.model.token import Message
from app.api.dashborad.model.receipt import ItemsPublic, Item, ItemPublic, ItemCreate, ItemUpdate
from app.api.deps import SessionDep, CurrentUser


class ItemService:
    @staticmethod
    def read_items(self, session: SessionDep, current_user: CurrentUser, skip: int, limit: int) -> ItemsPublic:
        if current_user.is_superuser:
            count_statement = select(func.count()).select_from(Item)
            count = session.exec(count_statement).one()
            statement = select(Item).offset(skip).limit(limit)
            items = session.exec(statement).all()
        else:
            count_statement = select(func.count()).select_from(Item).where(Item.owner_id == current_user.id)
            count = session.exec(count_statement).one()
            statement = select(Item).where(Item.owner_id == current_user.id).offset(skip).limit(limit)
            items = session.exec(statement).all()
        return ItemsPublic(data=items, count=count)

    @staticmethod
    def read_item(self, session: SessionDep, current_user: CurrentUser, id: int) -> ItemPublic:
        item = session.get(Item, id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if not current_user.is_superuser and (item.owner_id != current_user.id):
            raise HTTPException(status_code=400, detail="Not enough permissions")
        return item

    @staticmethod
    def create_item(self, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate) -> ItemPublic:
        item = Item.model_validate(item_in, update={"owner_id": current_user.id})
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    @staticmethod
    def update_item(self, session: SessionDep, current_user: CurrentUser, id: int, item_in: ItemUpdate) -> ItemPublic:
        item = session.get(Item, id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if not current_user.is_superuser and (item.owner_id != current_user.id):
            raise HTTPException(status_code=400, detail="Not enough permissions")
        update_dict = item_in.model_dump(exclude_unset=True)
        item.sqlmodel_update(update_dict)
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    @staticmethod
    def delete_item(self, session: SessionDep, current_user: CurrentUser, id: int) -> Message:
        item = session.get(Item, id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if not current_user.is_superuser and (item.owner_id != current_user.id):
            raise HTTPException(status_code=400, detail="Not enough permissions")
        session.delete(item)
        session.commit()
        return Message(message="Item deleted successfully")


item_service = ItemService()
