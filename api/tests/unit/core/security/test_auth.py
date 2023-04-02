from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest
from freezegun import freeze_time
from pydantic import SecretStr

from app.core.exception import (
    InvalidCredentialException,
    ResourceNotFoundException,
    UserDisabedException,
)
from app.core.security import auth as uut
from app.core.user.model import UserPrivate, UserPublic
from tests.factories.token_factory import AuthTokenFactory
from tests.factories.user_factory import UserPrivateFactory, UserPublicFactory
from tests.unit import util


def test_ACCESS_TOKEN():
    expected = "ACCESS_TOKEN"

    actual = uut.ACCESS_TOKEN

    assert actual == expected


def test_REFRESH_TOKEN():
    expected = "REFRESH_TOKEN"

    actual = uut.REFRESH_TOKEN

    assert actual == expected


def test_REVOKE_LOGOUT():
    expected = "REVOKE_LOGOUT"

    actual = uut.REVOKE_LOGOUT

    assert actual == expected


def test_oauth2_scheme():
    actual = uut.oauth2_scheme

    assert actual.model.flows.password.tokenUrl == "/api/v1/auth/login"


def test_AuthToken():
    auth_token = AuthTokenFactory.build()

    expected = auth_token

    actual = uut.AuthToken(**auth_token.dict())

    assert actual == expected


def test_AuthToken_defaults():
    auth_token = AuthTokenFactory.build()

    expected = uut.AuthToken(**auth_token.dict())
    expected.token_type = "Bearer"
    expected.access_token_expires_at = None
    expected.refresh_token_expires_at = None

    actual = uut.AuthToken(
        **auth_token.dict(
            exclude={
                "token_type",
                "access_token_expires_at",
                "refresh_token_expires_at",
            }
        )
    )

    assert actual == expected


@freeze_time("2020-01-01 00:00:00")
async def test_user_login(mocker):
    user_private = UserPrivateFactory.build(joe=True)

    updated_user_private = UserPrivate(
        **user_private.dict(exclude={"last_login", "date_modified"}),
        last_login=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
        date_modified=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
    )

    expected = AuthTokenFactory.build(jan_01_2020=True)

    mocker.patch(
        "app.core.security.auth.user_service.fetch",
        AsyncMock(return_value=user_private),
    )
    mocker.patch(
        "app.core.security.auth.user_service.update_private",
        AsyncMock(return_value=updated_user_private),
    )
    mocker.patch(
        "app.core.security.token.uuid4",
        Mock(side_effect=[UUID(util.access_token_id()), UUID(util.refresh_token_id())]),
    )

    actual = await uut.user_login(
        username=user_private.username, password=SecretStr("password")
    )

    assert actual == expected


async def test_user_login_invalid_credentials(mocker):
    user_private = UserPrivateFactory.build(joe=True)

    mocker.patch(
        "app.core.security.auth.user_service.fetch",
        AsyncMock(return_value=user_private),
    )

    with pytest.raises(
        InvalidCredentialException,
        match=f"Invalid credentials provided for username '{user_private.username}'",
    ):
        await uut.user_login(
            username=user_private.username, password=SecretStr("invalid")
        )


async def test_user_login_disabled(mocker):
    user_private = UserPrivateFactory.build(joe=True, disabled=True)

    mocker.patch(
        "app.core.security.auth.user_service.fetch",
        AsyncMock(return_value=user_private),
    )

    with pytest.raises(
        UserDisabedException, match=f"User '{user_private.username}' has been disabled"
    ):
        await uut.user_login(
            username=user_private.username, password=SecretStr("password")
        )


@freeze_time("2020-01-01 00:00:00")
async def test_user_logout(mocker):
    auth_token = AuthTokenFactory.build()

    expected = (True, True)

    mocker.patch("app.core.security.auth.revoke_token", AsyncMock(return_value=True))

    actual = await uut.user_logout(
        access_token=auth_token.access_token, refresh_token=auth_token.refresh_token
    )

    assert actual == expected


@freeze_time("2020-01-01 00:00:00")
async def test_refresh_access_token(mocker):
    auth_token = AuthTokenFactory.build(jan_01_2020=True)
    user_private = UserPrivateFactory.build(joe=True)

    token_data = {
        "exp": 1577847600,
        "sub": "Joe",
    }

    expected = uut.AuthToken(**auth_token.dict())

    mocker.patch(
        "app.core.security.auth.validate_token", AsyncMock(return_value=token_data)
    )
    mocker.patch(
        "app.core.security.auth.user_service.fetch",
        AsyncMock(return_value=user_private),
    )
    mocker.patch(
        "app.core.security.auth.generate_token",
        Mock(
            return_value=(auth_token.access_token, auth_token.access_token_expires_at)
        ),
    )

    actual = await uut.refresh_access_token(auth_token.refresh_token)

    assert actual == expected


@freeze_time("2020-01-01 00:00:00")
async def test_refresh_access_token_disabled(mocker):
    auth_token = AuthTokenFactory.build(jan_01_2020=True)
    user_private = UserPrivateFactory.build(joe=True, disabled=True)

    token_data = {
        "exp": 1577847600,
        "sub": "Joe",
    }

    mocker.patch(
        "app.core.security.auth.validate_token", AsyncMock(return_value=token_data)
    )
    mocker.patch(
        "app.core.security.auth.user_service.fetch",
        AsyncMock(return_value=user_private),
    )

    with pytest.raises(
        UserDisabedException, match=f"User '{user_private.username}' has been disabled"
    ):
        await uut.refresh_access_token(auth_token.refresh_token)


async def test_get_user_from_token(mocker):
    auth_token = AuthTokenFactory.build(jan_01_2020=True)
    user_public = UserPublicFactory.build(joe=True)

    token_data = {"data": user_public.dict()}

    expected = user_public

    mocker.patch(
        "app.core.security.auth.validate_token", AsyncMock(return_value=token_data)
    )

    actual = await uut.get_user_from_token(auth_token.access_token)

    assert actual == expected


async def test__get_api_user_from_credentials(mocker):
    user_private = UserPrivateFactory.build(joe=True)

    expected = UserPublic(**user_private.dict())

    mocker.patch(
        "app.core.security.auth.user_service.fetch",
        AsyncMock(return_value=user_private),
    )

    actual = (
        await uut._get_api_user_from_credentials(  # pylint: disable=protected-access
            username=user_private.username, password=SecretStr("password")
        )
    )

    assert actual == expected


async def test__get_api_user_from_credentials_invalid_credentials(mocker):
    user_private = UserPrivateFactory.build(joe=True)

    mocker.patch(
        "app.core.security.auth.user_service.fetch",
        AsyncMock(return_value=user_private),
    )

    with pytest.raises(
        InvalidCredentialException,
        match=f"Invalid credentials provided for username '{user_private.username}'",
    ):
        await uut._get_api_user_from_credentials(  # pylint: disable=protected-access
            username=user_private.username, password=SecretStr("invalid")
        )


async def test__get_api_user_from_credentials_disabled(mocker):
    user_private = UserPrivateFactory.build(joe=True, disabled=True)

    mocker.patch(
        "app.core.security.auth.user_service.fetch",
        AsyncMock(return_value=user_private),
    )

    with pytest.raises(
        UserDisabedException, match=f"User '{user_private.username}' has been disabled"
    ):
        await uut._get_api_user_from_credentials(  # pylint: disable=protected-access
            username=user_private.username, password=SecretStr("password")
        )


async def test__get_api_user_by_username(mocker):
    user_private = UserPrivateFactory.build(joe=True)

    expected = UserPublic(**user_private.dict())

    mocker.patch(
        "app.core.security.auth.user_service.fetch",
        AsyncMock(return_value=user_private),
    )

    actual = await uut._get_api_user_by_username(  # pylint: disable=protected-access
        username=user_private.username
    )

    assert actual == expected


async def test__get_api_user_by_username_disabled(mocker):
    user_private = UserPrivateFactory.build(joe=True, disabled=True)

    mocker.patch(
        "app.core.security.auth.user_service.fetch",
        AsyncMock(return_value=user_private),
    )

    with pytest.raises(
        UserDisabedException, match=f"User '{user_private.username}' has been disabled"
    ):
        await uut._get_api_user_by_username(  # pylint: disable=protected-access
            username=user_private.username
        )


async def test__authenticate_user(mocker):
    user_private = UserPrivateFactory.build(joe=True)

    expected = UserPublic(**user_private.dict())

    mocker.patch(
        "app.core.security.auth.user_service.fetch",
        AsyncMock(return_value=user_private),
    )

    actual = await uut._authenticate_user(  # pylint: disable=protected-access
        username=user_private.username, password=SecretStr("password")
    )

    assert actual == expected


async def test__authenticate_user_not_exists(mocker):
    user_private = UserPrivateFactory.build(joe=True)

    expected = None

    mocker.patch(
        "app.core.security.auth.user_service.fetch",
        AsyncMock(side_effect=ResourceNotFoundException()),
    )

    actual = await uut._authenticate_user(  # pylint: disable=protected-access
        username=user_private.username, password=SecretStr("password")
    )

    assert actual == expected


async def test__authenticate_user_invalid_credentials(mocker):
    user_private = UserPrivateFactory.build(joe=True)

    expected = None

    mocker.patch(
        "app.core.security.auth.user_service.fetch",
        AsyncMock(return_value=user_private),
    )

    actual = await uut._authenticate_user(  # pylint: disable=protected-access
        username=user_private.username, password=SecretStr("invalid")
    )

    assert actual == expected


def test__check_authorized():
    user_public = UserPublicFactory.build(disabled=False)

    expected = True

    actual = uut._check_authorized(user_public)  # pylint: disable=protected-access

    assert actual == expected


def test__check_authorized_disabled():
    user_public = UserPublicFactory.build(disabled=True)

    with pytest.raises(
        UserDisabedException, match=f"User '{user_public.username}' has been disabled"
    ):
        uut._check_authorized(user_public)  # pylint: disable=protected-access
