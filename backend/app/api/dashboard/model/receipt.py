from datetime import datetime
from typing import List, TYPE_CHECKING, Optional

from app.common.model import AliasMixin
from sqlmodel import Field, Relationship, SQLModel
import uuid

if TYPE_CHECKING:
    from app.api.admin.model.user import User


# Shared properties
class ReceiptFile(AliasMixin):
    file_name: Optional[str] = Field(max_length=100, default=None, nullable=True)
    file_url: Optional[str] = Field(max_length=100, default=None, nullable=True)


class ReceiptBase(ReceiptFile):
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
    id: uuid.UUID
    items: List["ReceiptItem"] = []


class ReceiptDelete(SQLModel):
    ids: List[uuid.UUID]


class ReceiptFileCreate(AliasMixin):
    files: List[ReceiptFile]


# Database model, database table inferred from class name
class Receipt(ReceiptBase, table=True):
    __tablename__ = "receipt"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="receipts")
    items: List["ReceiptItem"] = Relationship(
        back_populates="receipt", cascade_delete=True
    )


# Properties to return via API, id is always required
class ReceiptPublic(ReceiptBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ReceiptDetail(ReceiptBase):
    items: List["ReceiptItem"] = []


class ReceiptItemBase(AliasMixin):
    item: str = Field(max_length=50, nullable=False)
    quantity: float = Field(default=0.0)
    unit: str = Field(max_length=20)
    unit_price: float = Field(default=0.0)
    discount_price: float = Field(default=0.0)
    notes: Optional[str] = Field(max_length=100, default=None, nullable=True)


class ReceiptItem(ReceiptItemBase, table=True):
    __tablename__ = "receipt_item"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    receipt_id: uuid.UUID = Field(foreign_key="receipt.id", ondelete="CASCADE")
    receipt: "Receipt" = Relationship(back_populates="items")
