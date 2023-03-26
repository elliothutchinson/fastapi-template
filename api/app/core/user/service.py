from typing import List

from app.core.config import get_config
from app.core.logging import get_logger
from app.core.user import repo as user_repo

from .model import UserCreate, UserPrivate, UserUpdate, UserUpdatePrivate

logger = get_logger(__name__)

config = get_config()


async def create(user_create: UserCreate, roles: List[str]) -> UserPrivate:
    return await user_repo.create(user_create=user_create, roles=roles)


async def fetch(username: str) -> UserPrivate:
    return await user_repo.fetch(username)


async def update(username: str, user_update: UserUpdate) -> UserPrivate:
    return await user_repo.update(username=username, user_update=user_update)


async def update_private(
    username: str, user_update_private: UserUpdatePrivate
) -> UserPrivate:
    return await user_repo.update_private(
        username=username, user_update_private=user_update_private
    )
