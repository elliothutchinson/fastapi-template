from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID

import pytest
from pydantic import SecretStr

from app.core.exception import InvalidCredentialException, UserDisabedException
from app.core.security import auth as uut
from tests.util import (
    access_token_id_str,
    access_token_refreshed_id_str,
    refresh_token_id_str,
)


def test_ACCESS_TOKEN():
    actual = uut.ACCESS_TOKEN

    assert actual == "ACCESS_TOKEN"


def test_REFRESH_TOKEN():
    actual = uut.REFRESH_TOKEN

    assert actual == "REFRESH_TOKEN"


def test_REVOKE_LOGOUT():
    actual = uut.REVOKE_LOGOUT

    assert actual == "REVOKE_LOGOUT"


def test_oauth2_scheme():
    actual = uut.oauth2_scheme

    assert actual.model.flows.password.tokenUrl == "/api/v1/auth/login"


def test_AuthToken_optional_fields(access_token, refresh_token):
    auth_token_dict = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    expected = auth_token_dict.copy()
    expected["token_type"] = "Bearer"
    expected["access_token_expires_at"] = None
    expected["refresh_token_expires_at"] = None

    actual = uut.AuthToken(**auth_token_dict)

    assert actual.dict() == expected


def test_AuthToken(auth_token_dict):
    expected = auth_token_dict

    actual = uut.AuthToken(**auth_token_dict)

    assert actual.dict() == expected


@patch(
    "app.core.security.token.uuid4",
    Mock(side_effect=[UUID(access_token_id_str()), UUID(refresh_token_id_str())]),
)
@patch(
    "app.core.security.token.utc_now",
    Mock(return_value=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)),
)
@patch(
    "app.core.security.auth.datetime",
    Mock(now=Mock(return_value=datetime(2020, 1, 3, 0, 0))),
)
async def test_user_login(_setup_db_user_db, _setup_cache, access_token, refresh_token):
    expected = uut.AuthToken(
        access_token=access_token,
        access_token_expires_at=datetime(2020, 1, 1, 1, 0, tzinfo=timezone.utc),
        refresh_token=refresh_token,
        refresh_token_expires_at=datetime(2020, 1, 1, 3, 0, tzinfo=timezone.utc),
    )

    actual = await uut.user_login(username="tester", password=SecretStr("password"))

    assert actual == expected


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
async def test_user_logout(_setup_db, _setup_cache, access_token, refresh_token):
    actual_access_token_logout, actual_refresh_token_logout = await uut.user_logout(
        access_token=access_token, refresh_token=refresh_token
    )

    assert actual_access_token_logout is True
    assert actual_refresh_token_logout is True


@patch(
    "app.core.security.token.uuid4",
    Mock(return_value=UUID(access_token_refreshed_id_str())),
)
@patch(
    "app.core.security.token.utc_now",
    Mock(return_value=datetime(2020, 1, 1, 0, 30, tzinfo=timezone.utc)),
)
@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
async def test_refresh_access_token(_setup_db_user_db, _setup_cache, refresh_token):
    # pylint: disable=line-too-long
    expected = uut.AuthToken(
        access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl9pZCI6ImZiMjhiNWM0LTUyYzAtNDlkOC05Y2ZhLWI4YjE1MDM5MTA1NyIsImNsYWltIjoiQUNDRVNTX1RPS0VOIiwiZXhwIjoxNTc3ODQyMjAwLCJzdWIiOiJ0ZXN0ZXIiLCJkYXRhIjp7InVzZXJuYW1lIjoidGVzdGVyIiwiZmlyc3RfbmFtZSI6IkpvZSIsImxhc3RfbmFtZSI6IlRlc3RlciIsImVtYWlsIjoidGVzdGVyQGV4YW1wbGUuY29tIiwidmVyaWZpZWRfZW1haWwiOiJ0ZXN0ZXJAZXhhbXBsZS5jb20iLCJyb2xlcyI6WyJVU0VSIl0sImRpc2FibGVkIjpmYWxzZSwiZGF0ZV9jcmVhdGVkIjoiMjAyMC0wMS0wMSAwMDowMDowMCIsImRhdGVfbW9kaWZpZWQiOiIyMDIwLTAxLTAyIDAwOjAwOjAwIiwibGFzdF9sb2dpbiI6IjIwMjAtMDEtMDMgMDA6MDA6MDAifX0.x5l2Qw4uTzaeCsNsPrPVyNeS54eBvNanbx7Xf6ih5rc",
        access_token_expires_at=datetime(2020, 1, 1, 1, 30, tzinfo=timezone.utc),
        refresh_token=refresh_token,
        refresh_token_expires_at=datetime(2020, 1, 1, 3, 0, tzinfo=timezone.utc),
    )

    actual = await uut.refresh_access_token(refresh_token)

    assert actual == expected


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
async def test_get_user_from_token(_setup_cache, access_token, user):
    actual = await uut.get_user_from_token(access_token)

    assert actual == user


async def test_get_api_user_success(_setup_db_user_db, _setup_cache, user):
    actual = await uut.get_api_user(username="tester", password=SecretStr("password"))

    assert actual == user


async def test_get_api_user_invalid(_setup_db, _setup_cache):

    with pytest.raises(
        InvalidCredentialException,
        match="Invalid credentials provided for username 'tester'",
    ):
        await uut.get_api_user(username="tester", password=SecretStr("password"))


async def test_get_api_user_disabled(mocker, user_db):
    user_db.disabled = True
    mocker.patch(
        "app.core.security.auth.user_service",
        Mock(fetch_user=AsyncMock(return_value=user_db)),
    )

    with pytest.raises(UserDisabedException, match="User 'tester' has been disabled"):
        await uut.get_api_user(username="tester", password=SecretStr("password"))


async def test_authenticate_user_valid(_setup_db_user_db, _setup_cache, user):
    actual = await uut.authenticate_user(
        username="tester", password=SecretStr("password")
    )

    assert actual == user


async def test_authenticate_user_invalid_password(
    _setup_db_user_db,
    _setup_cache,
):
    actual = await uut.authenticate_user(
        username="tester", password=SecretStr("invalid")
    )

    assert actual is None


async def test_authenticate_user_invalid_username(_setup_db, _setup_cache):
    actual = await uut.authenticate_user(
        username="tester", password=SecretStr("password")
    )

    assert actual is None
