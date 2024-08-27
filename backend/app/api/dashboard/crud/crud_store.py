from typing import List
import uuid

from app.api.dashboard.model.store import Store
from sqlmodel import Session, select
from sqlmodel.sql.expression import Select


class StoreDAO:
    def get_store_by_id(
        self,
        session: Session,
        id: uuid.UUID | None = None,
    ) -> List[Store]:
        store = session.get(Store, id)
        return store

    def get_store_by_name(
        self,
        session: Session,
        name: str | None = None,
    ) -> List[Store]:
        store = session.exec(select(Store).where(Store.name == name)).first()
        return store

    def get_store_by_ids(
        self,
        session: Session,
        ids: List[uuid.UUID] | None = None,
    ) -> List[Store]:
        store = session.exec(select(Store).where(Store.id in ids)).all()
        return store


store_dao = StoreDAO()
