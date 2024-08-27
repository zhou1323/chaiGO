from datetime import datetime
from typing import List, TYPE_CHECKING, Optional

from app.common.model import AliasMixin
from sqlmodel import Field, Relationship, SQLModel
import uuid

if TYPE_CHECKING:
    from app.api.dashboard.model.offer import Offer


class StoreBase(AliasMixin):
    name: str = Field(max_length=50)
    location: str = Field(max_length=50, nullable=True)


# Database model, database table inferred from class name
class Store(StoreBase, table=True):
    __tablename__ = "store"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    offers: List["Offer"] = Relationship(back_populates="store", cascade_delete=True)
