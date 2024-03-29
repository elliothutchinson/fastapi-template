from datetime import datetime, timedelta, timezone

import orjson

from app.core.user.model import UserPublic
from tests import util
from tests.factories.server_response_factory import ServerResponseFactory
from tests.factories.token_factory import AuthTokenFactory
from tests.factories.user_factory import (
    UserCreateFactory,
    UserDbFactory,
    UserPublicFactory,
    UserUpdateFactory,
)


async def test_register_new_user(client):
    # pylint: disable=duplicate-code
    user_create = UserCreateFactory.build()

    expected = util.json_dict(
        UserPublicFactory.build(
            **user_create.dict(),
            date_modified=None,
            last_login=None,
        ).dict(exclude={"date_created"})
    )

    actual = client.post("/api/v1/user/", data=user_create.json())
    actual_json = actual.json()
    actual_date_created = datetime.fromisoformat(actual_json.pop("date_created"))

    assert actual.status_code == 200
    assert actual_date_created > datetime.now(timezone.utc) - timedelta(seconds=5)
    assert actual_json == expected


async def test_register_new_user_persists(client):
    """
    Verify newly registered user is persisted and returned once logged in and
    user info is fetched.
    """
    user_create = UserCreateFactory.build()
    user_create_dict = user_create.dict()
    user_create_dict["password"] = user_create.password.get_secret_value()
    user_create_dict["password_match"] = user_create.password.get_secret_value()

    expected = util.json_dict(
        UserPublicFactory.build(
            **user_create.dict(),
        ).dict(exclude={"date_created", "date_modified", "last_login"})
    )

    create_response = client.post("/api/v1/user/", data=orjson.dumps(user_create_dict))
    assert create_response.status_code == 200

    credential = {
        "username": user_create.username,
        "password": "password",
    }
    login_response = client.post("/api/v1/auth/login", data=credential)
    assert login_response.status_code == 200
    auth_token = login_response.json()

    headers_access_token = util.authorization_header(auth_token["access_token"])

    actual = client.get("/api/v1/user/", headers=headers_access_token)
    actual_json = actual.json()
    actual_date_created = datetime.fromisoformat(actual_json.pop("date_created"))
    actual_date_modified = datetime.fromisoformat(actual_json.pop("date_modified"))
    actual_last_login = datetime.fromisoformat(actual_json.pop("last_login"))

    assert actual.status_code == 200
    assert actual_date_created > datetime.now(timezone.utc) - timedelta(seconds=5)
    assert actual_date_modified > datetime.now(timezone.utc) - timedelta(seconds=5)
    assert actual_last_login > datetime.now(timezone.utc) - timedelta(seconds=5)
    assert actual_json == expected


async def test_register_new_user_username_exists(client):
    user_db = await UserDbFactory.create()
    user_create = UserCreateFactory.build(username=user_db.username)

    expected = ServerResponseFactory.build(message="Email or username already exists")

    actual = client.post("/api/v1/user/", data=user_create.json())

    assert actual.status_code == 409
    assert actual.json() == expected


async def test_register_new_user_email_exists(client):
    user_db = await UserDbFactory.create()
    user_create = UserCreateFactory.build(email=user_db.email)

    expected = ServerResponseFactory.build(
        message="Email or username already exists"
    ).dict()

    actual = client.post("/api/v1/user/", data=user_create.json())

    assert actual.status_code == 409
    assert actual.json() == expected


async def test_read_current_user(client, headers_access_token, user_access_token):
    expected = util.json_dict(user_access_token.dict())

    actual = client.get("/api/v1/user/", headers=headers_access_token)
    actual.json()

    assert actual.status_code == 200
    assert actual.json() == expected


async def test_update_current_user(client, headers_access_token, user_access_token):
    # pylint: disable=duplicate-code
    user_update = UserUpdateFactory.build()
    user_dict = user_access_token.dict() | user_update.dict()

    expected = util.json_dict(UserPublic(**user_dict).dict(exclude={"date_modified"}))

    actual = client.put(
        "/api/v1/user/", headers=headers_access_token, data=user_update.json()
    )
    actual_json = actual.json()
    actual_date_modified = datetime.fromisoformat(actual_json.pop("date_modified"))

    assert actual.status_code == 200
    assert actual_date_modified > datetime.now(timezone.utc) - timedelta(seconds=5)
    assert actual_json == expected


async def test_update_current_user_persists(
    client, headers_access_token, user_access_token
):
    # pylint: disable=duplicate-code
    user_update = UserUpdateFactory.build()
    user_dict = user_access_token.dict() | user_update.dict()

    expected = util.json_dict(UserPublic(**user_dict).dict(exclude={"date_modified"}))

    response = client.put(
        "/api/v1/user/",
        headers=headers_access_token,
        data=user_update.json(exclude={"password", "password_match"}),
    )
    assert response.status_code == 200

    actual = client.get("/api/v1/user/", headers=headers_access_token)
    actual_json = actual.json()
    actual_date_modified = datetime.fromisoformat(actual_json.pop("date_modified"))

    assert actual.status_code == 200
    assert actual_date_modified > datetime.now(timezone.utc) - timedelta(seconds=5)
    assert actual_json == expected


async def test_update_current_user_change_password(
    client, headers_access_token, user_access_token
):
    changed_password = "changed"
    user_update = UserUpdateFactory.build().dict()
    user_update["password"] = changed_password
    user_update["password_match"] = changed_password
    credential = {
        "username": user_access_token.username,
        "password": changed_password,
    }

    expected = list(AuthTokenFactory.build().dict())

    response = client.put(
        "/api/v1/user/", headers=headers_access_token, data=orjson.dumps(user_update)
    )
    assert response.status_code == 200

    actual = client.post("/api/v1/auth/login", data=credential)

    assert actual.status_code == 200
    assert list(actual.json()) == expected
