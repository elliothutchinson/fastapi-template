from datetime import datetime
from typing import List

from pymongo.errors import DuplicateKeyError

from app.core.config import get_config
from app.core.db import cache
from app.core.exception import DataConflictException, ResourceNotFoundException
from app.core.logging import get_logger
from app.core.security import crypt

from .model import USER_CACHE_PREFIX, UserCreate, UserDb, UserUpdate, UserUpdatePrivate

logger = get_logger(__name__)

config = get_config()


async def fetch_user(username: str) -> UserDb:
    logger.info(f"fetching user: {username}")

    user_db = await cache.fetch_entity(
        prefix=USER_CACHE_PREFIX, key=username, doc_model=UserDb
    )
    if not user_db:
        user_db = await UserDb.find_one(UserDb.username == username)

        if user_db:
            await cache.cache_entity(
                prefix=USER_CACHE_PREFIX,
                key=username,
                doc=user_db,
                ttl=config.cache_ttl_user,
            )

    if not user_db:
        raise ResourceNotFoundException(
            f"User resource not found for username '{username}'"
        )

    return user_db


async def create_user(user_create: UserCreate, roles: List[str] = None) -> UserDb:
    if roles is None:
        roles = []

    password_hash = crypt.hash_password(user_create.password)
    user_db = UserDb(
        **user_create.dict(),
        date_created=datetime.now(),
        password_hash=password_hash,
        roles=roles,
    )

    try:
        await user_db.insert()
    except DuplicateKeyError as dke:
        logger.error(dke)
        raise DataConflictException("Email or username already exists") from dke

    return user_db


async def update_user(username: str, user_update: UserUpdate) -> UserDb:
    user_db = await UserDb.find_one(UserDb.username == username)

    if user_update.first_name:
        user_db.first_name = user_update.first_name

    if user_update.last_name:
        user_db.last_name = user_update.last_name

    if user_update.email:
        user_db.email = user_update.email

    if user_update.password:
        password_hash = crypt.hash_password(user_update.password)
        user_db.password_hash = password_hash

    user_db.date_modified = datetime.now()

    await user_db.replace()

    await cache.delete_entity(prefix=USER_CACHE_PREFIX, key=username)

    return user_db


async def update_user_private(
    username: str, user_update_private: UserUpdatePrivate
) -> UserDb:
    user_db = await UserDb.find_one(UserDb.username == username)

    if user_update_private.verified_email:
        user_db.verified_email = user_update_private.verified_email
    if user_update_private.roles:
        user_db.roles = user_update_private.roles
    if user_update_private.disabled is not None:
        user_db.disabled = user_update_private.disabled
    if user_update_private.last_login:
        user_db.last_login = user_update_private.last_login

    await user_db.replace()

    await cache.delete_entity(prefix=USER_CACHE_PREFIX, key=username)

    return user_db
