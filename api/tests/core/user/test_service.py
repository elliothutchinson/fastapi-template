from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from app.core.exception import DataConflictException, ResourceNotFoundException
from app.core.user import service as uut
from app.core.user.model import UserUpdate
from tests.util import password_hash_str


async def test_fetch_user_from_cache(_setup_cache_user_db, user_db):
    actual = await uut.fetch_user("tester")

    assert actual == user_db


async def test_fetch_user_from_db(_setup_db_user_db, _setup_cache, user_db):
    actual = await uut.fetch_user("tester")

    assert actual == user_db


async def test_fetch_user_not_found(_setup_db, _setup_cache):

    with pytest.raises(
        ResourceNotFoundException, match=f"Resource not found for username 'tester'"
    ):
        await uut.fetch_user("tester")


@patch(
    "app.core.user.service.datetime",
    Mock(now=Mock(return_value=datetime(2020, 1, 1, 0, 0))),
)
@patch(
    "app.core.security.crypt.context", Mock(hash=Mock(return_value=password_hash_str()))
)
async def test_create_user(_setup_db, user_create, user_db):
    expected = user_db.dict()
    expected["verified_email"] = None
    expected["date_modified"] = None
    expected["last_login"] = None
    expected.pop("id")

    actual = await uut.create_user(user_create=user_create, roles=["USER"])
    actual_dict = actual.dict()
    actual_id = actual_dict.pop("id")

    assert actual_id is not None
    assert actual_dict == expected


async def test_create_user_username_already_exists(_setup_db_user_db, user_create):
    user_create.email = "tester_2@example.com"

    with pytest.raises(DataConflictException, match="Email or username already exists"):
        await uut.create_user(user_create=user_create, roles=["USER"])


async def test_create_user_email_already_exists(_setup_db_user_db, user_create):
    user_create.username = "tester_2"

    with pytest.raises(DataConflictException, match="Email or username already exists"):
        await uut.create_user(user_create=user_create, roles=["USER"])


@patch(
    "app.core.user.service.datetime",
    Mock(now=Mock(return_value=datetime(2020, 1, 5, 0, 0))),
)
async def test_update_user(
    mocker, _setup_db_user_db, _setup_cache, user_update, user_db
):
    password_changed_hash = (
        "$2b$12$pujnRjDeFKCnB5Xp5c4q.etDl8ACMs8O4vXVJ.9Xia0Ah6TdsAdze"
    )
    mocker.patch(
        "app.core.security.crypt.context",
        Mock(hash=Mock(return_value=password_changed_hash)),
    )

    expected = user_db.dict()
    expected.update(user_update.dict())
    expected["date_modified"] = datetime(2020, 1, 5, 0, 0)
    expected["password_hash"] = password_changed_hash
    expected.pop("password")
    expected.pop("password_match")

    actual = await uut.update_user(username="tester", user_update=user_update)

    assert actual.dict() == expected


@patch(
    "app.core.user.service.datetime",
    Mock(now=Mock(return_value=datetime(2020, 1, 5, 0, 0))),
)
async def test_update_user_optional_fields(_setup_db_user_db, _setup_cache, user_db):
    user_update = UserUpdate()

    expected = user_db.dict()
    expected["date_modified"] = datetime(2020, 1, 5, 0, 0)

    actual = await uut.update_user(username="tester", user_update=user_update)

    assert actual.dict() == expected
