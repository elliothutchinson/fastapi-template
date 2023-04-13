from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock

import pytest
from freezegun import freeze_time

from app.core.exception import DataConflictException, ResourceNotFoundException
from app.core.user import repo as uut
from app.core.user.model import UserCreate, UserPrivate, UserUpdate, UserUpdatePrivate
from tests.factories.user_factory import (
    UserDbFactory,
    UserPrivateFactory,
    UserUpdateFactory,
    UserUpdatePrivateFactory,
)

UUT_PATH = "app.core.user.repo"


def test_UserDb(_setup_db):
    user_db = UserDbFactory.build()

    expected = user_db

    actual = uut.UserDb(**user_db.dict())

    assert actual == expected


def test_UserDb_defaults(_setup_db):
    user_db = UserDbFactory.build(verified=True)

    expected = uut.UserDb(**user_db.dict())
    expected.verified_email = None
    expected.date_modified = None
    expected.last_login = None

    actual = uut.UserDb(
        **user_db.dict(exclude={"verified_email", "date_modified", "last_login"})
    )

    assert actual == expected


@freeze_time("2020-01-01 00:00:00")
async def test_create(_setup_db, mocker):
    user_private = UserPrivateFactory.build(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )
    user_create = UserCreate(
        **user_private.dict(), password="password", password_match="password"
    )

    expected = user_private

    mocker.patch(
        f"{UUT_PATH}.crypt.hash_password", Mock(return_value=user_private.password_hash)
    )

    actual = await uut.create(user_create=user_create, roles=user_private.roles)

    assert actual == expected


@freeze_time("2020-01-01 00:00:00")
async def test_create_default_roles(_setup_db, mocker):
    user_private = UserPrivateFactory.build(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )
    user_create = UserCreate(
        **user_private.dict(), password="password", password_match="password"
    )

    expected = user_private
    expected.roles = []

    mocker.patch(
        f"{UUT_PATH}.crypt.hash_password", Mock(return_value=user_private.password_hash)
    )

    actual = await uut.create(user_create=user_create, roles=None)

    assert actual == expected


@freeze_time("2020-01-01 00:00:00")
async def test_create_already_exists(_setup_db, mocker):
    user_db = await UserDbFactory.create(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )
    user_create = UserCreate(
        **user_db.dict(), password="password", password_match="password"
    )

    mocker.patch(
        f"{UUT_PATH}.crypt.hash_password", Mock(return_value=user_db.password_hash)
    )

    with pytest.raises(DataConflictException, match="Email or username already exists"):
        await uut.create(user_create=user_create, roles=user_db.roles)


async def test_fetch_cache_hit(_setup_db, mocker):
    user_private = UserPrivateFactory.build()

    expected = user_private

    mocker.patch(f"{UUT_PATH}.cache.fetch", AsyncMock(return_value=user_private))

    actual = await uut.fetch(user_private.username)

    assert actual == expected


async def test_fetch_cache_miss(_setup_db, _setup_cache):
    user_db = await UserDbFactory.create()

    expected = UserPrivate(**user_db.dict())

    actual = await uut.fetch(user_db.username)

    assert actual == expected


async def test_fetch_not_exists(_setup_db, _setup_cache):
    user_db = UserDbFactory.build()

    with pytest.raises(
        ResourceNotFoundException,
        match=f"User resource not found for username '{user_db.username}'",
    ):
        await uut.fetch(user_db.username)


@freeze_time("2020-01-01 00:00:00")
async def test_update_all(_setup_db, _setup_cache, mocker):
    user_db = await UserDbFactory.create(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )
    user_update = UserUpdateFactory.build()

    expected = UserPrivate(
        **user_db.dict(exclude={"first_name", "last_name", "email"}),
        **user_update.dict(),
    )
    expected.date_modified = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    expected.password_hash = "password_hash"

    mocker.patch(f"{UUT_PATH}.crypt.hash_password", Mock(return_value="password_hash"))

    actual = await uut.update(username=user_db.username, user_update=user_update)

    assert actual == expected


@freeze_time("2020-01-01 00:00:00")
async def test_update_none(_setup_db, _setup_cache):
    user_db = await UserDbFactory.create(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )
    user_update = UserUpdate()

    expected = UserPrivate(**user_db.dict())
    expected.date_modified = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)

    actual = await uut.update(username=user_db.username, user_update=user_update)

    assert actual == expected


async def test_update_not_exists(_setup_db):
    user_db = UserDbFactory.build(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )
    user_update = UserUpdate()

    with pytest.raises(
        ResourceNotFoundException,
        match=f"User resource not found for username '{user_db.username}'",
    ):
        await uut.update(username=user_db.username, user_update=user_update)


@freeze_time("2020-01-01 00:00:00")
async def test_update_private_all(_setup_db, _setup_cache):
    user_db = await UserDbFactory.create(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )
    user_update_private = UserUpdatePrivateFactory.build()

    expected = UserPrivate(
        **user_db.dict(exclude={"verified_email", "roles", "disabled", "last_login"}),
        **user_update_private.dict(),
    )
    expected.date_modified = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)

    actual = await uut.update_private(
        username=user_db.username, user_update_private=user_update_private
    )

    assert actual == expected


@freeze_time("2020-01-01 00:00:00")
async def test_update_private_none(_setup_db, _setup_cache):
    user_db = await UserDbFactory.create(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )
    user_update_private = UserUpdatePrivate()

    expected = UserPrivate(**user_db.dict())
    expected.date_modified = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)

    actual = await uut.update_private(
        username=user_db.username, user_update_private=user_update_private
    )

    assert actual == expected


async def test_update_private_not_exists(_setup_db):
    user_db = UserDbFactory.build(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )
    user_update_private = UserUpdatePrivate()

    with pytest.raises(
        ResourceNotFoundException,
        match=f"User resource not found for username '{user_db.username}'",
    ):
        await uut.update_private(
            username=user_db.username, user_update_private=user_update_private
        )
