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
from app.core.user.model import UserPublic, UserUpdatePrivate

from .crypt import verify_password

ACCESS_TOKEN = "ACCESS_TOKEN"
REFRESH_TOKEN = "REFRESH_TOKEN"
REVOKE_LOGOUT = "REVOKE_LOGOUT"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

config = get_config()


class AuthToken(BaseModel):
    token_type: Optional[str] = "Bearer"
    access_token: str
    access_token_expires_at: Optional[datetime]
    refresh_token: str
    refresh_token_expires_at: Optional[datetime]


async def user_login(username: str, password: SecretStr) -> AuthToken:
    api_user = await _get_api_user_from_credentials(
        username=username, password=password
    )
    updated_user = await user_service.update_private(
        username=api_user.username,
        user_update_private=UserUpdatePrivate(last_login=datetime.now(timezone.utc)),
    )
    user_public = UserPublic(**updated_user.dict())

    access_token, access_token_expires_at = generate_token(
        claim=ACCESS_TOKEN,
        expire_min=config.access_token_expire_min,
        sub=user_public.username,
        data=user_public,
    )
    refresh_token, refresh_token_expires_at = generate_token(
        claim=REFRESH_TOKEN,
        expire_min=config.refresh_token_expire_min,
        sub=user_public.username,
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
    user = await _get_api_user_by_username(token_data["sub"])

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


async def get_user_from_token(token: str = Depends(oauth2_scheme)) -> UserPublic:
    token_data = await validate_token(claim=ACCESS_TOKEN, token=token)
    user = UserPublic(**token_data["data"])

    return user


async def _get_api_user_from_credentials(
    username: str, password: SecretStr
) -> UserPublic:
    user = await _authenticate_user(username=username, password=password)

    if not user:
        raise InvalidCredentialException(
            f"Invalid credentials provided for username '{username}'"
        )

    _check_authorized(user)

    return user


async def _get_api_user_by_username(username: str) -> UserPublic:
    user_private = await user_service.fetch(username)
    user_public = UserPublic(**user_private.dict())

    _check_authorized(user_public)

    return user_public


async def _authenticate_user(
    username: str, password: SecretStr
) -> Optional[UserPublic]:
    user_public = None

    try:
        user_private = await user_service.fetch(username)
        if verify_password(password=password, password_hash=user_private.password_hash):
            user_public = UserPublic(**user_private.dict())
    except ResourceNotFoundException:
        pass

    return user_public


def _check_authorized(user: UserPublic) -> bool:
    if user.disabled:
        raise UserDisabedException(f"User '{user.username}' has been disabled")

    return True
