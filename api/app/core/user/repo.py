from datetime import datetime, timezone
from typing import List

from beanie import Document, Indexed
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError

from app.core.config import get_config
from app.core.db import cache
from app.core.exception import DataConflictException, ResourceNotFoundException
from app.core.logging import get_logger
from app.core.security import crypt

from .model import (
    USER_CACHE_PREFIX,
    UserCreate,
    UserPrivate,
    UserUpdate,
    UserUpdatePrivate,
)

config = get_config()
logger = get_logger(__name__)


class UserDb(Document):
    username: Indexed(str, unique=True)
    first_name: str
    last_name: str
    email: Indexed(EmailStr, unique=True)
    verified_email: EmailStr | None = None
    roles: List[str] = []
    disabled: bool = False
    date_created: datetime
    date_modified: datetime | None = None
    last_login: datetime | None = None
    password_hash: str


async def create(user_create: UserCreate, roles: List[str]) -> UserPrivate:
    if roles is None:
        roles = []

    password_hash = crypt.hash_password(user_create.password)
    user_db = UserDb(
        **user_create.dict(),
        date_created=datetime.now(timezone.utc),
        password_hash=password_hash,
        roles=roles,
    )

    try:
        await user_db.insert()
    except DuplicateKeyError as dke:
        logger.error(dke)
        raise DataConflictException("Email or username already exists") from dke

    return UserPrivate(**user_db.dict())


# todo: add unit test
def _update_date_timezones(user_private: UserPrivate):
    user_private.date_created = user_private.date_created.replace(tzinfo=timezone.utc)
    if user_private.date_modified:
        user_private.date_modified = user_private.date_modified.replace(
            tzinfo=timezone.utc
        )
    if user_private.last_login:
        user_private.last_login = user_private.last_login.replace(tzinfo=timezone.utc)


async def fetch(username: str) -> UserPrivate:
    logger.info(f"fetching user: {username} from db")

    user_private = await cache.fetch(
        prefix=USER_CACHE_PREFIX, key=username, doc_model=UserPrivate
    )
    if not user_private:
        user_db = await UserDb.find_one(UserDb.username == username)

        if user_db:
            user_private = UserPrivate(**user_db.dict())
            _update_date_timezones(user_private)
            await cache.put(
                prefix=USER_CACHE_PREFIX,
                key=username,
                doc=user_private,
                ttl=config.cache_ttl_user,
            )

    if not user_private:
        raise ResourceNotFoundException(
            f"User resource not found for username '{username}'"
        )

    return user_private


async def update(username: str, user_update: UserUpdate) -> UserPrivate:
    user_db = await UserDb.find_one(UserDb.username == username)

    if not user_db:
        raise ResourceNotFoundException(
            f"User resource not found for username '{username}'"
        )

    if user_update.first_name:
        user_db.first_name = user_update.first_name

    if user_update.last_name:
        user_db.last_name = user_update.last_name

    if user_update.email:
        user_db.email = user_update.email

    if user_update.password:
        password_hash = crypt.hash_password(user_update.password)
        user_db.password_hash = password_hash

    user_db.date_modified = datetime.now(timezone.utc)

    await user_db.replace()

    await cache.delete(prefix=USER_CACHE_PREFIX, key=username)

    user_private = UserPrivate(**user_db.dict())
    _update_date_timezones(user_private)

    return user_private


async def update_private(
    username: str, user_update_private: UserUpdatePrivate
) -> UserPrivate:
    user_db = await UserDb.find_one(UserDb.username == username)

    if not user_db:
        raise ResourceNotFoundException(
            f"User resource not found for username '{username}'"
        )

    if user_update_private.verified_email:
        user_db.verified_email = user_update_private.verified_email
    if user_update_private.roles:
        user_db.roles = user_update_private.roles
    if user_update_private.disabled is not None:
        user_db.disabled = user_update_private.disabled
    if user_update_private.last_login:
        user_db.last_login = user_update_private.last_login

    user_db.date_modified = datetime.now(timezone.utc)

    await user_db.replace()

    await cache.delete(prefix=USER_CACHE_PREFIX, key=username)

    user_private = UserPrivate(**user_db.dict())
    _update_date_timezones(user_private)

    return user_private
