from datetime import datetime
from typing import List, TYPE_CHECKING, Optional

from app.common.model import AliasMixin
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.api.admin.model.user import User


# Shared properties
class ReceiptBase(AliasMixin):
    category: str = Field(max_length=50)
    date: datetime = Field(default_factory=datetime.utcnow)
    description: str = Field(max_length=100)
    notes: Optional[str] = Field(default=None, max_length=100, nullable=True)
    amount: float = Field(default=0.0)


# Properties to receive on receipt creation
class ReceiptCreate(ReceiptBase):
    items: List["ReceiptItem"] = []


# Properties to receive on receipt update
class ReceiptUpdate(ReceiptBase):
    id: int
    items: List["ReceiptItem"] = []


class ReceiptDelete(SQLModel):
    ids: List[int]


# Database model, database table inferred from class name
class Receipt(ReceiptBase, table=True):
    __tablename__ = "receipt"

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="receipts")
    items: List["ReceiptItem"] = Relationship(back_populates="receipt")


# Properties to return via API, id is always required
class ReceiptPublic(ReceiptBase):
    id: int
    owner_id: int


class ReceiptDetail(ReceiptBase):
    items: List["ReceiptItem"] = []


class ReceiptItemBase(AliasMixin):
    item: str = Field(max_length=50, nullable=False)
    quantity: int = Field(default=0)
    unit: str = Field(max_length=20)
    unit_price: float = Field(default=0.0)
    discount_price: float = Field(default=0.0)
    notes: Optional[str] = Field(max_length=100, default=None, nullable=True)


class ReceiptItem(ReceiptItemBase, table=True):
    __tablename__ = "receipt_item"

    id: Optional[int] = Field(default=None, primary_key=True)
    receipt_id: int = Field(foreign_key="receipt.id")
    receipt: "Receipt" = Relationship(back_populates="items")
