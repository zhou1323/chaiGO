from datetime import datetime
from typing import List
import uuid

from app.api.dashboard.crud.crud_store import store_dao
from app.api.dashboard.model.store import (
    Store,
)
from app.api.deps import SessionDep
from sqlmodel.sql.expression import Select


class StoreService:
    def get_store_by_id(self, session: SessionDep, id: uuid.UUID) -> Store:
        return store_dao.get_store_by_id(session, id)

    def get_store_by_name(self, session: SessionDep, name: str) -> Store:
        return store_dao.get_store_by_name(session, name)

    def get_store_by_ids(
        self, session: SessionDep, ids: List[uuid.UUID]
    ) -> List[Store]:
        return store_dao.get_store_by_ids(session, ids)


store_service = StoreService()
