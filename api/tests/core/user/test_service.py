from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.core.user import service as uut
from app.core.user.model import User, UserCreate, UserUpdate, UserUpdatePrivate
from tests.mock import doc_row_full_user, doc_row_user


@patch("app.core.db.service.asyncpg", AsyncMock())
@patch(
    "app.core.user.crud.datetime",
    Mock(now=Mock(return_value=datetime(2020, 1, 1, 0, 0))),
)
async def test_register_user(user_create, user_dict):
    user_dict.pop("verified_email")
    user_dict.pop("date_modified")
    user_dict.pop("last_login")
    user_dict["roles"] = []
    user_dict["verified"] = False
    expected = User(**user_dict)
    user_create_obj = UserCreate(**user_create)
    actual = await uut.register_user(user_create=user_create_obj)
    assert actual == expected


@pytest.mark.expected_data(doc_row_full_user())
async def test_get_user_data(db_context, user_dict, mocker):
    mocker.patch("app.core.db.service.get_db_context", Mock(return_value=db_context))
    expected = User(**user_dict)
    actual = await uut.get_user_data(username="tester")
    assert actual == expected


@pytest.mark.expected_data(multi_expected=[doc_row_user(), None])
@patch(
    "app.core.user.crud.datetime",
    Mock(now=Mock(return_value=datetime(2022, 2, 2, 0, 0))),
)
async def test_update_user_data(
    db_context, updated_user_dict, user_update_dict, mocker
):
    mocker.patch("app.core.db.service.get_db_context", Mock(return_value=db_context))

    expected = User(**updated_user_dict)
    user_update = UserUpdate(**user_update_dict)
    actual = await uut.update_user_data(username="tester", user_update=user_update)
    assert actual == expected


@pytest.mark.expected_data(doc_row_user())
async def test_update_user_private_data(
    db_context, updated_user_private_dict, user_update_private_dict, mocker
):
    mocker.patch("app.core.db.service.get_db_context", Mock(return_value=db_context))

    user_update_private = UserUpdatePrivate(**user_update_private_dict)
    expected = User(**updated_user_private_dict)

    actual = await uut.update_user_private_data(
        username="tester", user_update_private=user_update_private
    )
    assert actual == expected
