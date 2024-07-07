from datetime import datetime
from typing import Optional

from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from sqlmodel import SQLModel, Field


class TimeStampMixin(SQLModel):
    created_at: Optional[datetime] = Field(default=datetime.utcnow(), nullable=False)
    updated_at: Optional[datetime] = Field(default=datetime.utcnow(), nullable=False)


class UserMixin(SQLModel):
    created_by: int = Field(nullable=False)
    modified_by: int | None = Field(nullable=False)


class AliasMixin(SQLModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
