import jwt
import orjson

from tests.factories.server_response_factory import ServerResponseFactory
from tests.factories.token_factory import AuthTokenFactory
from tests.factories.user_factory import UserDbFactory


async def test_login_for_auth_token(client):
    user_db = await UserDbFactory.create()

    credential = {
        "username": user_db.username,
        "password": "password",
    }

    expected = list(AuthTokenFactory.build().dict())

    actual = client.post("/api/v1/auth/login", data=credential)

    assert actual.status_code == 200
    assert list(actual.json()) == expected


async def test_login_for_auth_token_user_not_exists(client):
    credential = {
        "username": "invalid_user",
        "password": "password",
    }

    expected = ServerResponseFactory.build(
        message="Invalid credentials provided for username 'invalid_user'"
    )

    actual = client.post("/api/v1/auth/login", data=credential)

    assert actual.status_code == 401
    assert actual.json() == expected


async def test_login_for_auth_token_invalid_password(client):
    user_db = await UserDbFactory.create()

    credential = {
        "username": user_db.username,
        "password": "invalid_password",
    }

    expected = ServerResponseFactory.build(
        message=f"Invalid credentials provided for username '{user_db.username}'"
    )

    actual = client.post("/api/v1/auth/login", data=credential)

    assert actual.status_code == 401
    assert actual.json() == expected


async def test_login_for_auth_token_user_disabled(client):
    user_db = await UserDbFactory.create(disabled=True)

    credential = {
        "username": user_db.username,
        "password": "password",
    }

    expected = ServerResponseFactory.build(
        message=f"User '{user_db.username}' has been disabled"
    )

    actual = client.post("/api/v1/auth/login", data=credential)

    assert actual.status_code == 403
    assert actual.json() == expected


async def test_logout_auth_token(client, login_auth_token):
    expected = ServerResponseFactory.build(
        message="access_token revoked: True, refresh_token revoked: True"
    )

    actual = client.post("/api/v1/auth/logout", data=orjson.dumps(login_auth_token))

    assert actual.status_code == 200
    assert actual.json() == expected


async def test_logout_auth_token_already_revoked(client, login_auth_token):
    expected = ServerResponseFactory.build(
        message="access_token revoked: False, refresh_token revoked: False"
    )

    response = client.post("/api/v1/auth/logout", data=orjson.dumps(login_auth_token))
    assert response.status_code == 200

    actual = client.post("/api/v1/auth/logout", data=orjson.dumps(login_auth_token))

    assert actual.status_code == 200
    assert actual.json() == expected


async def test_logout_auth_token_expired_token(client):
    auth_token = AuthTokenFactory.build(jan_01_2020=True)
    expected = ServerResponseFactory.build(
        message="access_token revoked: False, refresh_token revoked: False"
    )

    actual = client.post("/api/v1/auth/logout", data=auth_token.json())

    assert actual.status_code == 200
    assert actual.json() == expected


async def test_refresh_auth_token(client, login_auth_token):
    expected = list(AuthTokenFactory.build().dict())

    actual = client.post("/api/v1/auth/refresh", data=orjson.dumps(login_auth_token))

    assert actual.status_code == 200
    assert list(actual.json()) == expected


async def test_refresh_auth_token_revoked_token(client, login_auth_token):
    token_data = jwt.decode(
        login_auth_token["refresh_token"], options={"verify_signature": False}
    )

    expected = ServerResponseFactory.build(
        message=f"Token with token_id '{token_data['token_id']}' has been revoked"
    )

    response = client.post("/api/v1/auth/logout", data=orjson.dumps(login_auth_token))
    assert response.status_code == 200

    actual = client.post("/api/v1/auth/refresh", data=orjson.dumps(login_auth_token))

    assert actual.status_code == 401
    assert actual.json() == expected


async def test_refresh_auth_token_expired_token(client):
    auth_token = AuthTokenFactory.build(jan_01_2020=True)

    expected = ServerResponseFactory.build(
        message="Invalid token with claim 'REFRESH_TOKEN'"
    )

    actual = client.post("/api/v1/auth/refresh", data=auth_token.json())

    assert actual.status_code == 401
    assert actual.json() == expected


async def test_refresh_auth_token_invalid_token(client, login_auth_token):
    login_auth_token["refresh_token"] = login_auth_token["access_token"]

    expected = ServerResponseFactory.build(
        message="Token claim 'ACCESS_TOKEN' didn't match expected claim 'REFRESH_TOKEN'"
    )

    actual = client.post("/api/v1/auth/refresh", data=orjson.dumps(login_auth_token))

    assert actual.status_code == 401
    assert actual.json() == expected
