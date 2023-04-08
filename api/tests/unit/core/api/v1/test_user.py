from unittest.mock import AsyncMock

from app.core.user.model import UserPublic
from tests.factories.user_factory import (
    UserCreateFactory,
    UserPrivateFactory,
    UserUpdateFactory,
)
from tests.util import json_dict

UUT_PATH = "app.core.api.v1.user"


def test_register_new_user(client, mocker):
    user_private = UserPrivateFactory.build()
    user_create = UserCreateFactory.build(**user_private.dict())
    user_public = UserPublic(**user_private.dict())

    expected = json_dict(user_public.dict())

    mocker.patch(
        f"{UUT_PATH}.user_service.create", AsyncMock(return_value=user_private)
    )

    actual = client.post("/api/v1/user/", data=user_create.json())

    assert actual.status_code == 200
    assert actual.json() == expected


def test_read_current_user(client, mocker, auth_headers, override_get_user_from_token):
    user_private = UserPrivateFactory.build(**override_get_user_from_token.dict())

    expected = json_dict(override_get_user_from_token.dict())

    mocker.patch(f"{UUT_PATH}.user_service.fetch", AsyncMock(return_value=user_private))

    actual = client.get("/api/v1/user/", headers=auth_headers)

    assert actual.status_code == 200
    assert actual.json() == expected


def test_update_current_user(
    client, mocker, auth_headers, override_get_user_from_token
):
    user_update = UserUpdateFactory.build()
    user_private = UserPrivateFactory.build(
        **override_get_user_from_token.dict(
            exclude={"first_name", "last_name", "email"}
        ),
        **user_update.dict(),
    )
    user_public = UserPublic(**user_private.dict())

    expected = json_dict(user_public.dict())

    mocker.patch(
        f"{UUT_PATH}.user_service.update", AsyncMock(return_value=user_private)
    )

    actual = client.put("/api/v1/user/", headers=auth_headers, data=user_update.json())

    assert actual.status_code == 200
    assert actual.json() == expected
