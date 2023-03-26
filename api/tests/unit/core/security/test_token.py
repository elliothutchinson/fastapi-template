from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest
from freezegun import freeze_time
from pydantic import BaseModel

from app.core.exception import InvalidTokenException
from app.core.security import token as uut
from tests.factories.token_factory import RevokedTokenFactory


class TokenData(BaseModel):
    data: str


@pytest.fixture
def token_id():
    return "ed2b5f55-79ec-4cb0-ae5b-fbb2a9add283"


@pytest.fixture
def token_with_data(mocker, token_id):
    mocker.patch("app.core.security.token.uuid4", Mock(return_value=UUID(token_id)))

    return (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJ0b2tlbl9pZCI6ImVkMmI1ZjU1LTc5ZWMtNGNiMC1hZTViLWZiYjJhOWFkZDI4MyIsImNsYWltIjoiVEVTVCIsImV4cCI6MTU3Nzg0MDQwMCwic3ViIjoidGVzdGVyIiwiZGF0YSI6eyJkYXRhIjoidGVzdGVyIn19."  # pylint: disable=line-too-long
        "Kzus93q-jwqIW7UXZ8s-u4FbyG53kl000-6crvSiAq0"
    )


@pytest.fixture
def token_no_data(mocker, token_id):
    mocker.patch("app.core.security.token.uuid4", Mock(return_value=UUID(token_id)))

    return (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJ0b2tlbl9pZCI6ImVkMmI1ZjU1LTc5ZWMtNGNiMC1hZTViLWZiYjJhOWFkZDI4MyIsImNsYWltIjoiVEVTVCIsImV4cCI6MTU3Nzg0MDQwMCwic3ViIjoidGVzdGVyIiwiZGF0YSI6bnVsbH0."  # pylint: disable=line-too-long
        "pRxf7fgDhGoHLV63ILfhHYbUon4QGr4jfA-XwRi6V8M"
    )


def test_REVOKED_TOKEN_CACHE_PREFIX():
    expected = "REVOKED_TOKEN"

    actual = uut.REVOKED_TOKEN_CACHE_PREFIX

    assert actual == expected


def test_RevokedToken():
    revoked_token = RevokedTokenFactory.build()

    expected = revoked_token

    actual = uut.RevokedToken(**revoked_token.dict())

    assert actual == expected


def test_RevokedToken_defaults():
    revoked_token = RevokedTokenFactory.build()

    expected = uut.RevokedToken(**revoked_token.dict())
    expected.data = None

    actual = uut.RevokedToken(**revoked_token.dict(exclude={"data"}))

    assert actual == expected


@freeze_time("2020-01-01 00:00:00")
def test_generate_token_with_data(token_with_data):
    token_data = TokenData(data="tester")

    expected_token = token_with_data
    expected_expires = datetime(2020, 1, 1, 1, 0, tzinfo=timezone.utc)

    actual_token, actual_expires = uut.generate_token(
        claim="TEST", expire_min=60.0, sub="tester", data=token_data
    )

    assert actual_token == expected_token
    assert actual_expires == expected_expires


@freeze_time("2020-01-01 00:00:00")
def test_generate_token_no_data(token_no_data):
    expected_token = token_no_data
    expected_expires = datetime(2020, 1, 1, 1, 0, tzinfo=timezone.utc)

    actual_token, actual_expires = uut.generate_token(
        claim="TEST", expire_min=60.0, sub="tester"
    )

    assert actual_token == expected_token
    assert actual_expires == expected_expires


@freeze_time("2020-01-01 00:00:00")
async def test_validate_token(_setup_cache, token_no_data, token_id):
    expected = {
        "claim": "TEST",
        "data": None,
        "exp": 1577840400,
        "sub": "tester",
        "token_id": token_id,
    }

    actual = await uut.validate_token(claim="TEST", token=token_no_data)

    assert actual == expected


@freeze_time("2020-01-01 00:00:00")
async def test_validate_token_revoked(mocker, token_no_data, token_id):
    revoked_token = RevokedTokenFactory.build()

    mocker.patch(
        "app.core.security.token.cache.fetch", AsyncMock(return_value=revoked_token)
    )

    with pytest.raises(
        InvalidTokenException,
        match=f"Token with token_id '{token_id}' has been revoked",
    ):
        await uut.validate_token(claim="TEST", token=token_no_data)


@freeze_time("2020-01-01 00:00:00")
async def test_validate_token_invalid_claim(token_no_data):
    with pytest.raises(
        InvalidTokenException,
        match="Token claim 'TEST' didn't match expected claim 'INVALID'",
    ):
        await uut.validate_token(claim="INVALID", token=token_no_data)


async def test_validate_token_expired(token_no_data):
    with pytest.raises(InvalidTokenException, match="Invalid token with claim 'TEST'"):
        await uut.validate_token(claim="TEST", token=token_no_data)


@freeze_time("2020-01-01 00:00:00")
async def test_revoke_token(_setup_cache, token_no_data):
    actual = await uut.revoke_token(
        claim="TEST", token=token_no_data, revoke_reason="testing"
    )

    assert actual is True


@freeze_time("2020-01-01 00:00:00")
async def test_revoke_token_already_revoked(mocker, token_no_data):
    revoked_token = RevokedTokenFactory.build()

    mocker.patch(
        "app.core.security.token.cache.fetch", AsyncMock(return_value=revoked_token)
    )

    actual = await uut.revoke_token(
        claim="TEST", token=token_no_data, revoke_reason="testing"
    )

    assert actual is False


async def test_revoke_token_expired(_setup_cache, token_no_data):
    actual = await uut.revoke_token(
        claim="TEST", token=token_no_data, revoke_reason="testing"
    )

    assert actual is False


async def test__is_token_revoked_true(mocker, token_id):
    revoked_token = RevokedTokenFactory.build()

    mocker.patch(
        "app.core.security.token.cache.fetch", AsyncMock(return_value=revoked_token)
    )

    actual = await uut._is_token_revoked(token_id)  # pylint: disable=protected-access

    assert actual is True


async def test__is_token_revoked_false(_setup_cache, token_id):
    actual = await uut._is_token_revoked(token_id)  # pylint: disable=protected-access

    assert actual is False
