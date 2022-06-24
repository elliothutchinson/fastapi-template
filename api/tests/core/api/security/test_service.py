from unittest.mock import Mock

import pytest
from pydantic import SecretStr

from app.core.api.security import service as uut
from app.core.api.security.model import (
    InvalidCredentialException,
    UserDisabledException,
)
from app.core.user.model import User
from tests.mock import doc_row_full_user


@pytest.mark.expected_data(doc_row_full_user())
async def test_get_authenticated_user_valid(db_context, user_dict, mocker):
    mocker.patch("app.core.db.service.get_db_context", Mock(return_value=db_context))
    expected = User(**user_dict)
    actual = await uut.get_authenticated_user(
        username="tester", password=SecretStr("test")
    )
    assert actual == expected


@pytest.mark.expected_data(doc_row_full_user())
async def test_get_authenticated_user_invalid_credential(db_context, mocker):
    mocker.patch("app.core.db.service.get_db_context", Mock(return_value=db_context))
    with pytest.raises(
        InvalidCredentialException, match=f"Invalid credentials provided"
    ):
        await uut.get_authenticated_user(
            username="tester", password=SecretStr("invalid")
        )


@pytest.mark.expected_data(doc_row_full_user({"disabled": True}))
async def test_get_authenticated_user_disabled(db_context, mocker):
    mocker.patch("app.core.db.service.get_db_context", Mock(return_value=db_context))
    with pytest.raises(UserDisabledException, match=f"User is disabled"):
        await uut.get_authenticated_user(username="tester", password=SecretStr("test"))


@pytest.mark.expected_data(doc_row_full_user())
async def test_authenticate_user(db_context, user_dict, mocker):
    mocker.patch("app.core.db.service.get_db_context", Mock(return_value=db_context))
    expected = User(**user_dict)
    actual = await uut.authenticate_user(username="tester", password=SecretStr("test"))
    assert actual == expected


@pytest.mark.expected_data(None)
async def test_authenticate_user_no_user(db_context, mocker):
    mocker.patch("app.core.db.service.get_db_context", Mock(return_value=db_context))
    actual = await uut.authenticate_user(username="tester", password=SecretStr("test"))
    assert actual is False


@pytest.mark.expected_data(doc_row_full_user())
async def test_authenticate_user_invalid_password(db_context, mocker):
    mocker.patch("app.core.db.service.get_db_context", Mock(return_value=db_context))
    actual = await uut.authenticate_user(
        username="tester", password=SecretStr("invalid")
    )
    assert actual is False
