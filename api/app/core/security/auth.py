from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, SecretStr

from app.core.config import get_config
from app.core.exception import (
    InvalidCredentialException,
    ResourceNotFoundException,
    UserDisabedException,
)
from app.core.security.token import generate_token, revoke_token, validate_token
from app.core.user import service as user_service
from app.core.user.model import User

from .crypt import verify_password

ACCESS_TOKEN = "ACCESS_TOKEN"
REFRESH_TOKEN = "REFRESH_TOKEN"
REVOKE_LOGOUT = "REVOKE_LOGOUT"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")

config = get_config()


class AuthToken(BaseModel):
    token_type: Optional[str] = "Bearer"
    access_token: str
    access_token_expires_at: Optional[datetime]
    refresh_token: str
    refresh_token_expires_at: Optional[datetime]


# todo: update last login on success
async def user_login(username: str, password: SecretStr) -> AuthToken:
    user = await get_api_user(username=username, password=password)

    access_token, access_token_expires_at = generate_token(
        claim=ACCESS_TOKEN,
        expire_min=config.access_token_expire_min,
        sub=user.username,
        data=user,
    )
    refresh_token, refresh_token_expires_at = generate_token(
        claim=REFRESH_TOKEN,
        expire_min=config.refresh_token_expire_min,
        sub=user.username,
        data=None,
    )

    return AuthToken(
        access_token=access_token,
        access_token_expires_at=access_token_expires_at,
        refresh_token=refresh_token,
        refresh_token_expires_at=refresh_token_expires_at,
    )


async def user_logout(access_token: str, refresh_token: str) -> tuple[bool, bool]:
    access_revoked = await revoke_token(
        claim=ACCESS_TOKEN, token=access_token, revoke_reason=REVOKE_LOGOUT
    )
    refresh_revoked = await revoke_token(
        claim=REFRESH_TOKEN, token=refresh_token, revoke_reason=REVOKE_LOGOUT
    )

    return access_revoked, refresh_revoked


async def refresh_access_token(refresh_token: str) -> AuthToken:
    token_data = await validate_token(claim=REFRESH_TOKEN, token=refresh_token)
    refresh_token_expires_at = datetime.fromtimestamp(
        token_data["exp"], tz=timezone.utc
    )
    user_db = await user_service.fetch_user(token_data["sub"])
    user = User(**user_db.dict())

    access_token, access_token_expires_at = generate_token(
        claim=ACCESS_TOKEN,
        expire_min=config.access_token_expire_min,
        sub=user.username,
        data=user,
    )

    return AuthToken(
        access_token=access_token,
        access_token_expires_at=access_token_expires_at,
        refresh_token=refresh_token,
        refresh_token_expires_at=refresh_token_expires_at,
    )


async def get_user_from_token(token: str = Depends(oauth2_scheme)) -> User:
    token_data = await validate_token(claim=ACCESS_TOKEN, token=token)
    user = User(**token_data["data"])

    return user


async def get_api_user(username: str, password: SecretStr) -> User:
    user = await authenticate_user(username=username, password=password)

    if not user:
        raise InvalidCredentialException(
            f"Invalid credentials provided for username '{username}'"
        )

    if user.disabled:
        raise UserDisabedException(f"User '{username}' has been disabled")

    return user


async def authenticate_user(username: str, password: SecretStr) -> Optional[User]:
    user = None

    try:
        user_db = await user_service.fetch_user(username)
        if verify_password(password=password, password_hash=user_db.password_hash):
            user = User(**user_db.dict())
    except ResourceNotFoundException:
        pass

    return user
