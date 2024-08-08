from typing import TYPE_CHECKING, List, Optional
import uuid
from app.api.admin.model.token import Token
from app.common.model import AliasMixin
from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.api.dashboard.model.receipt import Receipt
    from app.api.dashboard.model.budget import Budget


# Shared properties
class UserBase(AliasMixin):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    username: Optional[str] = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    username: Optional[str] = Field(default=None, max_length=255)


class UserUpdateMe(SQLModel):
    username: Optional[str] = Field(default=None, max_length=255)
    email: Optional[EmailStr] = Field(default=None, max_length=255)


class UpdatePassword(AliasMixin):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class ResetPassword(AliasMixin):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    __tablename__ = "user"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    receipts: List["Receipt"] = Relationship(back_populates="owner")
    budgets: List["Budget"] = Relationship(back_populates="owner")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: List[UserPublic]
    count: int


class UserWithToken(UserBase, Token):
    pass
