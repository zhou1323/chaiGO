from datetime import timedelta
import random
import string
from typing import Any
import uuid

from app.api.admin.crud.crud_user import user_dao
from app.api.admin.model.token import Message
from app.api.admin.model.user import (
    UserRegister,
    UsersPublic,
    User,
    UserCreate,
    UserPublic,
    UpdatePassword,
    UserUpdateMe,
    UserUpdate,
    UserWithToken,
)
from app.api.dashboard.model.receipt import Receipt
from app.api.deps import SessionDep, CurrentUser
from app.core import security
from app.core.config import settings
from app.core.db_redis import redis_client
from app.core.security import get_password_hash, verify_password
from app.utils.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    generate_verification_code_email,
    send_email,
    verify_password_reset_token,
    generate_new_account_email,
)
from fastapi import HTTPException
from sqlmodel import col, delete, func, select
from starlette.responses import HTMLResponse


class UserService:
    @staticmethod
    async def login(*, session: SessionDep, email: str, password: str) -> UserWithToken:
        """
        OAuth2 compatible token login, get an access token for future requests
        """
        user = user_dao.authenticate(session=session, email=email, password=password)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        elif not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
        access_token = await security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
        user_with_token = UserWithToken(
            access_token=access_token, email=user.email, username=user.username
        )
        return user_with_token

    async def logout(self, id: uuid.UUID) -> None:
        prefix = f"{settings.PROJECT_NAME}:{id}:"
        await redis_client.delete_prefix(prefix)

    # Return confirmation email with account info
    async def create_user(*, session: SessionDep, user_in: UserCreate) -> UserPublic:
        user = user_dao.get_user_by_email(session=session, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )
        user = user_dao.create_user(session=session, user_create=user_in)
        if settings.emails_enabled and user_in.email:
            email_data = generate_new_account_email(
                email_to=user_in.email,
                username=user_in.username,
                password=user_in.password,
            )
            await send_email(
                email_to=user_in.email,
                subject=email_data.subject,
                html_content=email_data.html_content,
            )
        return user

    async def generate_verification_code(self, email: str) -> str:
        verification_code = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )
        await redis_client.set(
            f"{settings.PROJECT_NAME}:{email}:verification_code",
            verification_code,
            ex=60,
        )
        return verification_code

    async def verify_code(self, email: str, code: str) -> bool:
        verification_code = await redis_client.get(
            f"{settings.PROJECT_NAME}:{email}:verification_code"
        )
        if verification_code is None:
            return False
        return verification_code.lower() == code.lower()

    async def send_verification_email(
        self, session: SessionDep, email: str, verification_code: str
    ):
        # Check if email already exists
        user = user_dao.get_user_by_email(session=session, email=email)
        if user:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )

        email_data = generate_verification_code_email(
            email_to=email,
            verification_code=verification_code,
        )
        await send_email(
            email_to=email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

    async def register_user_with_verification(
        self, session: SessionDep, user_in: UserRegister
    ):
        if not await self.verify_code(user_in.email, user_in.verification_code):
            raise HTTPException(status_code=400, detail="Invalid verification code")

        user = self.register_user(session=session, user_in=user_in)
        return user

    def register_user(self, session: SessionDep, user_in: UserRegister) -> None:
        if not settings.USERS_OPEN_REGISTRATION:
            raise HTTPException(
                status_code=403,
                detail="Open user registration is forbidden on this server",
            )
        user = user_dao.get_user_by_email(session=session, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system",
            )
        user_create = UserCreate.model_validate(user_in)
        user_dao.create_user(session=session, user_create=user_create)

    async def recover_password(self, session: SessionDep, email: str) -> None:
        """
        Password Recovery
        """
        user = user_dao.get_user_by_email(session=session, email=email)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="The user with this email does not exist in the system.",
            )

        password_reset_token = generate_password_reset_token(email=email)
        email_data = generate_reset_password_email(
            email_to=user.email, email=email, token=password_reset_token
        )
        await send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

    def reset_password(
        self, session: SessionDep, token: str, new_password: str
    ) -> Message:
        """
        Reset password
        """
        email = verify_password_reset_token(token=token)
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")
        user = user_dao.get_user_by_email(session=session, email=email)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="The user with this email does not exist in the system.",
            )
        elif not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        hashed_password = get_password_hash(password=new_password)
        user.hashed_password = hashed_password
        session.add(user)
        session.commit()
        return Message(message="Password updated successfully")

    def reset_password_html_content(*, session: SessionDep, email: str) -> Any:
        """
        HTML Content for Password Recovery
        """
        user = user_dao.get_user_by_email(session=session, email=email)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="The user with this username does not exist in the system.",
            )
        password_reset_token = generate_password_reset_token(email=email)
        email_data = generate_reset_password_email(
            email_to=user.email, email=email, token=password_reset_token
        )

        return HTMLResponse(
            content=email_data.html_content, headers={"subject:": email_data.subject}
        )

    def read_users(*, session: SessionDep, skip: int, limit: int) -> UsersPublic:
        count_statement = select(func.count()).select_from(User)
        count = session.exec(count_statement).one()
        statement = select(User).offset(skip).limit(limit)
        users = session.exec(statement).all()
        return UsersPublic(data=users, count=count)

    def read_user_by_id(
        *, user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
    ) -> UserPublic:
        user = session.get(User, user_id)
        if user == current_user:
            return user
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403,
                detail="The user doesn't have enough privileges",
            )
        return user

    def update_user(
        *, session: SessionDep, user_id: uuid.UUID, user_in: UserUpdate
    ) -> UserPublic:
        db_user = session.get(User, user_id)
        if not db_user:
            raise HTTPException(
                status_code=404,
                detail="The user with this id does not exist in the system",
            )
        if user_in.email:
            existing_user = user_dao.get_user_by_email(
                session=session, email=user_in.email
            )
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=409, detail="User with this email already exists"
                )
        db_user = user_dao.update_user(
            session=session, db_user=db_user, user_in=user_in
        )
        return db_user

    def delete_user(
        *, session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
    ) -> Message:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user == current_user:
            raise HTTPException(
                status_code=403,
                detail="Super users are not allowed to delete themselves",
            )
        statement = delete(Receipt).where(col(Receipt.owner_id) == user_id)
        session.exec(statement)
        session.delete(user)
        session.commit()
        return Message(message="User deleted successfully")

    # service about current user
    def update_user_me(
        self, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
    ) -> UserPublic:
        if user_in.email:
            existing_user = user_dao.get_user_by_email(
                session=session, email=user_in.email
            )
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=409, detail="User with this email already exists"
                )
        updated_user = user_dao.update_user_me(
            session=session, current_user=current_user, user_in=user_in
        )
        user_info = UserPublic.model_validate(updated_user)
        return user_info

    async def update_password_me(
        self, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
    ) -> Message:
        if not verify_password(body.current_password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect password")
        if body.current_password == body.new_password:
            raise HTTPException(
                status_code=400,
                detail="New password cannot be the same as the current one",
            )
        user_dao.update_password_me(
            session=session, current_user=current_user, new_password=body.new_password
        )
        await self.logout(id=current_user.id)

    def delete_user_me(*, session: SessionDep, current_user: CurrentUser) -> Message:
        if current_user.is_superuser:
            raise HTTPException(
                status_code=403,
                detail="Super users are not allowed to delete themselves",
            )
        statement = delete(Receipt).where(col(Receipt.owner_id) == current_user.id)
        session.exec(statement)
        session.delete(current_user)
        session.commit()
        return Message(message="User deleted successfully")


user_service = UserService()
