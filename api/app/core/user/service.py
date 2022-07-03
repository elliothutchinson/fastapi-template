from pydantic import EmailStr

from app.core.api.security.token import service as token_service
from app.core.api.security.token.model import AccessToken
from app.core.db import service as db_service

from .crud import (
    create_user,
    get_user,
    get_user_by_email,
    update_user,
    update_user_private,
)
from .model import User, UserCreate, UserUpdate, UserUpdatePrivate

VERIFY_TOKEN = "VERIFY_TOKEN"


async def register_user(user_create: UserCreate) -> User:
    db_context = db_service.get_db_context()
    user_db = await create_user(db_context=db_context, user_create=user_create)
    return User(**user_db.dict())


async def get_user_data(username: str) -> User:
    db_context = db_service.get_db_context()
    user_db = await get_user(db_context=db_context, username=username)
    return User(**user_db.dict())


async def get_user_data_by_email(email: EmailStr) -> User:
    db_context = db_service.get_db_context()
    user_db = await get_user_by_email(db_context=db_context, email=email)
    return User(**user_db.dict())


async def update_user_data(username: str, user_update: UserUpdate) -> User:
    db_context = db_service.get_db_context()
    user_db = await update_user(
        db_context=db_context, username=username, user_update=user_update
    )
    return User(**user_db.dict())


async def update_user_private_data(
    username: str, user_update_private: UserUpdatePrivate
) -> User:
    db_context = db_service.get_db_context()
    user_db = await update_user_private(
        db_context=db_context,
        username=username,
        user_update_private=user_update_private,
    )
    return User(**user_db.dict())


async def generate_verify_email_token(user: User, expire_min: float) -> AccessToken:
    return await token_service.generate_token(
        token_type=VERIFY_TOKEN,
        expire_min=expire_min,
        username=user.username,
        data=user,
    )


async def verify_email(token: str):
    token_data = token_service.get_verified_token_data(
        token=token, claim=VERIFY_TOKEN, data_model=User
    )
    user_update_private = UserUpdatePrivate(verified_email=token_data.data.email)
    await update_user_private_data(
        token_data.data.username, user_update_private=user_update_private
    )
    await token_service.redact_user_token(token_db=token_data.metadata)
    return True
