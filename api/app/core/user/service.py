from app.core.db import service as db_service

from .crud import create_user, get_user, update_user, update_user_private
from .model import User, UserCreate, UserUpdate, UserUpdatePrivate


async def register_user(user_create: UserCreate) -> User:
    db_context = db_service.get_db_context()
    user_db = await create_user(db_context=db_context, user_create=user_create)
    return User(**user_db.dict())


async def get_user_data(username: str) -> User:
    db_context = db_service.get_db_context()
    user_db = await get_user(db_context=db_context, username=username)
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
