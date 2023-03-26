from unittest.mock import AsyncMock

from app.core.user import service as uut
from tests.factories.user_factory import (
    UserCreateFactory,
    UserPrivateFactory,
    UserUpdateFactory,
    UserUpdatePrivateFactory,
)


async def test_create(mocker):
    user_private = UserPrivateFactory.build()

    user_create = UserCreateFactory.build(**user_private.dict())

    expected = user_private

    mocker.patch(
        "app.core.user.service.user_repo.create", AsyncMock(return_value=user_private)
    )

    actual = await uut.create(user_create=user_create, roles=user_private.roles)

    assert actual == expected


async def test_fetch(mocker):
    user_private = UserPrivateFactory.build()

    expected = user_private

    mocker.patch(
        "app.core.user.service.user_repo.fetch", AsyncMock(return_value=user_private)
    )

    actual = await uut.fetch(user_private.username)

    assert actual == expected


async def test_update(mocker):
    user_update = UserUpdateFactory.build()
    user_private = UserPrivateFactory.build(**user_update.dict())

    expected = user_private

    mocker.patch(
        "app.core.user.service.user_repo.update", AsyncMock(return_value=user_private)
    )

    actual = await uut.update(username=user_private.username, user_update=user_update)

    assert actual == expected


async def test_update_private(mocker):
    user_update_private = UserUpdatePrivateFactory.build()
    user_private = UserPrivateFactory.build(**user_update_private.dict())

    expected = user_private

    mocker.patch(
        "app.core.user.service.user_repo.update_private",
        AsyncMock(return_value=user_private),
    )

    actual = await uut.update_private(
        username=user_private.username, user_update_private=user_update_private
    )

    assert actual == expected
