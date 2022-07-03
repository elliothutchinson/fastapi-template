from unittest.mock import Mock, patch
from uuid import UUID

import pytest

from app.core.api.security.login.service import generate_login_token
from app.core.api.security.token import service as uut
from app.core.api.security.token.model import AccessToken, InvalidTokenException
from app.core.user.model import User
from tests.core.api.conftest import date_created, date_expires, token_db_data, token_id
from tests.mock import MIN_IN_YEAR, create_core_config, doc_row


def test_get_verified_token_data_valid(login_token, token_data):
    actual = uut.get_verified_token_data(
        token=login_token, claim="LOGIN_TOKEN", data_model=User
    )
    assert actual == token_data


def test_get_verified_token_data_invalid(login_token):
    with pytest.raises(InvalidTokenException, match="Invalid token"):
        uut.get_verified_token_data(token=login_token, claim="invalid", data_model=User)


def test_verify_token_valid(login_token, token_data):
    actual = uut.verify_token(token=login_token, claim="LOGIN_TOKEN", data_model=User)
    assert actual == token_data


@patch(
    "app.core.api.security.token.service.util.get_utc_now",
    Mock(return_value=date_created()),
)
async def test_verify_token_invalid_token(db_context, user, mocker):
    mocker.patch("app.core.db.service.get_db_context", Mock(return_value=db_context))
    access_token = await generate_login_token(user=user)
    actual = uut.verify_token(
        token=access_token.access_token, claim="LOGIN_TOKEN", data_model=User
    )
    assert actual is False


def test_verify_token_invalid_claim(login_token):
    actual = uut.verify_token(token=login_token, claim="invalid", data_model=User)
    assert actual is False


@patch(
    "app.core.api.security.token.service.util.get_utc_now",
    Mock(return_value=date_created()),
)
@patch("app.core.api.security.token.service.uuid4", Mock(return_value=UUID(token_id())))
@patch(
    "app.core.api.security.token.service.get_core_config",
    Mock(
        return_value=create_core_config(
            override={"login_token_expire_min": MIN_IN_YEAR * 100}
        )
    ),
)
async def test_generate_token(db_context, user, login_token, mocker):
    mocker.patch("app.core.db.service.get_db_context", Mock(return_value=db_context))
    expected = AccessToken(access_token=login_token, date_expires=date_expires())
    actual = await uut.generate_token(
        token_type="LOGIN_TOKEN",
        expire_min=MIN_IN_YEAR * 100,
        username=user.username,
        data=user,
    )
    assert actual == expected


@patch("app.core.api.security.token.service.uuid4", Mock(return_value=UUID(token_id())))
async def test_save_user_token(db_context, user, token_db, mocker):
    mocker.patch("app.core.db.service.get_db_context", Mock(return_value=db_context))
    actual = await uut.save_user_token(
        token_type="LOGIN_TOKEN",
        username=user.username,
        date_created=date_created(),
        date_expires=date_expires(),
    )
    assert actual == token_db


@patch(
    "app.core.api.security.token.service.util.get_utc_now",
    Mock(return_value=date_created()),
)
async def test_redact_user_token(db_context, token_db, mocker):
    mocker.patch("app.core.db.service.get_db_context", Mock(return_value=db_context))
    expected = token_db.copy(update={"date_redacted": date_created()})
    actual = await uut.redact_user_token(token_db=token_db)
    assert actual == expected


@patch(
    "app.core.api.security.token.service.util.get_utc_now",
    Mock(return_value=date_created()),
)
@pytest.mark.expected_data([doc_row(token_db_data())])
async def test_redact_user_tokens(db_context, token_db, mocker):
    mocker.patch("app.core.db.service.get_db_context", Mock(return_value=db_context))
    expected = [token_db.copy(update={"date_redacted": date_created()})]
    actual = await uut.redact_user_token(token_db=token_db)
    actual = await uut.redact_user_tokens(username="tester")
    assert actual == expected
