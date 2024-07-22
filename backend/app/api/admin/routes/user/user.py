from typing import Any
import uuid

from app.api.admin.model.token import Message
from app.api.admin.model.user import (
    UsersPublic,
    UserCreate,
    UserPublic,
    UpdatePassword,
    UserUpdateMe,
    UserUpdate,
)
from app.api.admin.service.user_service import user_service
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    return user_service.read_users(session, skip, limit)


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    return user_service.read_user_by_id(user_id, session, current_user)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    return user_service.create_user(session, user_in)


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    return user_service.update_user(session, user_id, user_in)


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    return user_service.delete_user(session, current_user, user_id)


# Current user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    return user_service.update_user_me(session, user_in, current_user)


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    return user_service.update_password_me(session, body, current_user)


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    return user_service.delete_user_me(session, current_user)
