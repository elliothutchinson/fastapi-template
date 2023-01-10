from datetime import datetime, timezone
from unittest.mock import Mock, patch
from uuid import UUID

import orjson

from tests.util import (
    access_token_id_str,
    access_token_refreshed_id_str,
    refresh_token_id_str,
)


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
async def test_login_for_auth_token(
    client, _setup_db_user_db, _setup_cache, auth_token_dict
):
    credential = {
        "username": "tester",
        "password": "password",
    }

    expected = auth_token_dict
    expected_json = orjson.dumps(expected).decode()
    expected_json_dict = orjson.loads(expected_json)

    actual = client.post("/api/v1/auth/login", data=credential)
    actual_json = actual.json()

    assert actual.status_code == 200
    assert actual_json == expected_json_dict


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
async def test_logout_auth_token(
    client, _setup_db, _setup_cache, access_token, refresh_token
):
    auth_token = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    actual = client.post("/api/v1/auth/logout", json=auth_token)

    assert actual.status_code == 200
    assert actual.json() == {
        "message": "access_token revoked: True, refresh_token revoked: True"
    }


@patch(
    "app.core.security.token.uuid4",
    Mock(return_value=UUID(access_token_refreshed_id_str())),
)
@patch(
    "app.core.security.token.utc_now",
    Mock(return_value=datetime(2020, 1, 1, 0, 30, tzinfo=timezone.utc)),
)
@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
async def test_refresh_auth_token(
    client,
    _setup_db_user_db,
    _setup_cache,
    access_token,
    refresh_token,
    access_token_refreshed,
):
    auth_token = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
    auth_token_json = orjson.loads(orjson.dumps(auth_token).decode())

    expected = {
        "token_type": "Bearer",
        "access_token": access_token_refreshed,
        "access_token_expires_at": datetime(2020, 1, 1, 1, 30, tzinfo=timezone.utc),
        "refresh_token": refresh_token,
        "refresh_token_expires_at": datetime(2020, 1, 1, 3, 0, tzinfo=timezone.utc),
    }
    expected_json = orjson.dumps(expected).decode()
    expected_json_dict = orjson.loads(expected_json)

    actual = client.post("/api/v1/auth/refresh", json=auth_token_json)
    actual_json = actual.json()

    assert actual.status_code == 200
    assert actual_json == expected_json_dict
