from unittest.mock import AsyncMock

from tests.factories.server_response_factory import ServerResponseFactory
from tests.factories.token_factory import AuthTokenFactory
from tests.util import json_dict


def test_login_for_auth_token(client, mocker):
    auth_token = AuthTokenFactory.build()

    credential = {
        "username": "tester",
        "password": "password",
    }

    expected = json_dict(auth_token.dict())

    mocker.patch("app.core.api.v1.auth.user_login", AsyncMock(return_value=auth_token))

    actual = client.post("/api/v1/auth/login", data=credential)

    assert actual.status_code == 200
    assert actual.json() == expected


def test_logout_auth_token(client, mocker):
    auth_token = AuthTokenFactory.build()

    expected = ServerResponseFactory.build(
        message="access_token revoked: True, refresh_token revoked: True"
    )

    mocker.patch(
        "app.core.api.v1.auth.user_logout", AsyncMock(return_value=(True, True))
    )

    actual = client.post("/api/v1/auth/logout", data=auth_token.json())

    assert actual.status_code == 200
    assert actual.json() == expected


def test_refresh_auth_token(client, mocker):
    auth_token = AuthTokenFactory.build()

    expected = json_dict(auth_token.dict())

    mocker.patch(
        "app.core.api.v1.auth.refresh_access_token", AsyncMock(return_value=auth_token)
    )

    actual = client.post("/api/v1/auth/refresh", data=auth_token.json())

    assert actual.status_code == 200
    assert actual.json() == expected
