from datetime import datetime, timedelta
from typing import Any

import jwt
from app.core.config import settings
from app.core.db_redis import redis_client
from passlib.context import CryptContext
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


async def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    # Use redis to save the access token
    key = f"{settings.PROJECT_NAME}:{str(subject)}:{encoded_jwt}"
    await redis_client.setex(key, int(expires_delta.total_seconds()), encoded_jwt)
    return encoded_jwt


async def redis_token_authenticate(id: str, token: str) -> bool:
    key = f"{settings.PROJECT_NAME}:{id}:{token}"
    token_verify = await redis_client.get(key)
    if not token_verify:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is expired",
        )
    return True


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
