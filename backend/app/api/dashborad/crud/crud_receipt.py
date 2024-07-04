from app.models import Item, ItemCreate, User, UserCreate, UserUpdate

from sqlmodel import Session, select
class ReceiptDAO:
    def create_item(self, session: Session, item_in: ItemCreate, owner_id: int) -> Item:
        db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item