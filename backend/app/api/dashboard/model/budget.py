from datetime import datetime
from typing import List, TYPE_CHECKING, Optional

from app.common.model import AliasMixin
from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel
import uuid
import re

if TYPE_CHECKING:
    from app.api.admin.model.user import User


class BudgetBase(AliasMixin):
    budget: float = Field(default=0.0)
    other_expense: float = Field(default=0.0)
    surplus: float = Field(default=0.0)
    notes: Optional[str] = Field(default=None, max_length=100, nullable=True)


# Properties to receive on budget creation
class BudgetCreate(BudgetBase):
    date: str = Field()


# Properties to receive on budget update
class BudgetUpdate(BudgetBase):
    id: uuid.UUID


class BudgetDelete(SQLModel):
    ids: List[uuid.UUID]


# Database model, database table inferred from class name
class Budget(BudgetBase, table=True):
    __tablename__ = "budget"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date: str = Field()
    recorded_expense: float = Field(default=0.0)

    owner_id: uuid.UUID = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="budgets")

    @field_validator("date")
    def validate_date_format(cls, v):
        month_regex = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
        if not month_regex.match(v):
            raise ValueError(
                f"Invalid month format: {v}. Expected format is 'YYYY-MM'."
            )
        return v


class BudgetDetail(BudgetBase):
    id: uuid.UUID
    date: str
    recorded_expense: float
    surplus: float
