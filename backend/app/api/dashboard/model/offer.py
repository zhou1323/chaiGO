from datetime import datetime
from typing import List, TYPE_CHECKING, Optional

from app.common.model import AliasMixin, TimeStampMixin
from sqlmodel import Field, Relationship, SQLModel
import uuid

if TYPE_CHECKING:
    from app.api.dashboard.model.store import Store


class OfferBase(AliasMixin, TimeStampMixin):
    category: str = Field(max_length=50)
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: datetime = Field(default_factory=datetime.utcnow)
    item: str = Field(max_length=50)
    quantity: int = Field(default=0)
    unit: str = Field(max_length=50)
    unit_range_from: int = Field(default=0)
    unit_range_to: int = Field(default=0)
    ordinary_price: float = Field(default=0.0)
    price: float = Field(default=0.0)
    img: str = Field(max_length=512, nullable=True)
    item_sv: str = Field(max_length=50, nullable=True)
    item_en: str = Field(max_length=50, nullable=True)
    item_zh: str = Field(max_length=50, nullable=True)


# Database model, database table inferred from class name
class Offer(OfferBase, table=True):
    __tablename__ = "offer"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    store_id: uuid.UUID = Field(foreign_key="store.id", ondelete="CASCADE")
    store: "Store" = Relationship(back_populates="offers")


# Properties to return via API, id is always required
class OfferPublic(OfferBase):
    id: uuid.UUID
    store_id: uuid.UUID
    store_name: str | None = None
    img_url: str | None = None


class OfferInShoppingList(OfferPublic):
    price_string: str
    offer_info: str


class StoreInShoppingList(AliasMixin):
    store_name: str
    total: str
    offers: list[OfferInShoppingList]


class ShoppingListContent(AliasMixin):
    shopping_list: list[StoreInShoppingList]
    total: str
    weekly_budget: str
