from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID

import pytest

from app.core.exception import InvalidTokenException
from app.core.security import token as uut
from app.core.util import convert_datetime_to_str
from tests.util import access_token_id_str, refresh_token_id_str


@pytest.fixture
def revoked_refresh_token_db(refresh_token_id):
    revoked_token_db_dict = {
        "id": None,
        "token_id": refresh_token_id,
        "claim": "REFRESH_TOKEN",
        "exp": 1665339138,
        "sub": "tester",
        "data": None,
        "revoke_reason": "REVOKE_LOGOUT",
    }

    return uut.RevokedTokenDb(**revoked_token_db_dict)


@pytest.fixture
def _setup_cache_refresh_revoked_token_db(mocker, revoked_refresh_token_db):
    mocker.patch(
        "app.core.db.cache.aioredis.from_url",
        Mock(
            return_value=AsyncMock(
                get=AsyncMock(return_value=revoked_refresh_token_db.json()),
                set=AsyncMock(return_value=True),
                delete=AsyncMock(return_value=1),
            )
        ),
    )


def test_REVOKED_TOKEN_CACHE_PREFIX():
    actual = uut.REVOKED_TOKEN_CACHE_PREFIX

    assert actual == "REVOKED_TOKEN"


def test_RevokedTokenDb_optional_fields(refresh_token_id):
    revoked_token_db_dict = {
        "token_id": refresh_token_id,
        "claim": "REFRESH_TOKEN",
        "exp": 1665339138,
        "sub": "tester",
        "revoke_reason": "REVOKE_LOGOUT",
    }

    expected = revoked_token_db_dict.copy()
    expected["id"] = None
    expected["data"] = None

    actual = uut.RevokedTokenDb(**revoked_token_db_dict)

    assert actual.dict() == expected


def test_RevokedTokenDb(access_token_id, user):
    user_dict = user.dict()
    convert_datetime_to_str(user_dict)

    revoked_token_db_dict = {
        "id": None,
        "token_id": access_token_id,
        "claim": "ACCESS_TOKEN",
        "exp": 1577840400,
        "sub": "tester",
        "data": user_dict,
        "revoke_reason": "REVOKE_LOGOUT",
    }

    actual = uut.RevokedTokenDb(**revoked_token_db_dict)

    assert actual.dict() == revoked_token_db_dict


@patch(
    "app.core.security.token.uuid4",
    Mock(return_value=UUID(access_token_id_str())),
)
@patch(
    "app.core.security.token.utc_now",
    Mock(return_value=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)),
)
def test_generate_token_with_data(user, access_token):
    expected_token = access_token
    expected_expires = datetime(2020, 1, 1, 1, 0, tzinfo=timezone.utc)

    actual_token, actual_expires = uut.generate_token(
        claim="ACCESS_TOKEN", expire_min=60, sub="tester", data=user
    )

    assert actual_token == expected_token
    assert actual_expires == expected_expires


@patch(
    "app.core.security.token.uuid4",
    Mock(return_value=UUID(refresh_token_id_str())),
)
@patch(
    "app.core.security.token.utc_now",
    Mock(return_value=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)),
)
def test_generate_token_without_data(refresh_token):
    expected_token = refresh_token
    expected_expires = datetime(2020, 1, 1, 3, 0, tzinfo=timezone.utc)

    actual_token, actual_expires = uut.generate_token(
        claim="REFRESH_TOKEN", expire_min=180, sub="tester"
    )

    assert actual_token == expected_token
    assert actual_expires == expected_expires


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
async def test_validate_token_valid(_setup_cache, user, access_token, access_token_id):
    user_dict = user.dict()
    convert_datetime_to_str(user_dict)

    expected = {
        "token_id": access_token_id,
        "claim": "ACCESS_TOKEN",
        "exp": 1577840400,
        "sub": "tester",
        "data": user_dict,
    }

    actual = await uut.validate_token(claim="ACCESS_TOKEN", token=access_token)

    assert actual == expected


async def test_validate_token_invalid_expired(access_token):

    with pytest.raises(
        InvalidTokenException, match="Invalid token with expected claim 'ACCESS_TOKEN'"
    ):
        await uut.validate_token(claim="ACCESS_TOKEN", token=access_token)


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
async def test_validate_token_invalid_wrong_claim(access_token):

    with pytest.raises(
        InvalidTokenException,
        match="Token claim 'ACCESS_TOKEN' didn't match expected claim 'WRONG_CLAIM'",
    ):
        await uut.validate_token(claim="WRONG_CLAIM", token=access_token)


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
async def test_validate_token_invalid_revoked(
    _setup_cache_refresh_revoked_token_db, refresh_token, refresh_token_id
):

    with pytest.raises(
        InvalidTokenException,
        match=f"Token with token_id '{refresh_token_id}' has been revoked",
    ):
        await uut.validate_token(claim="REFRESH_TOKEN", token=refresh_token)


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
async def test_revoke_token_success(_setup_db, _setup_cache, refresh_token):
    actual = await uut.revoke_token(
        claim="REFRESH_TOKEN", token=refresh_token, revoke_reason="REVOKE_LOGOUT"
    )

    assert actual is True


async def test_revoke_token_fail_expired(_setup_db, _setup_cache, refresh_token):
    actual = await uut.revoke_token(
        claim="REFRESH_TOKEN", token=refresh_token, revoke_reason="REVOKE_LOGOUT"
    )

    assert actual is False


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
async def test_revoke_token_fail_already_revoked(
    _setup_db, _setup_cache, revoked_refresh_token_db, refresh_token
):
    await revoked_refresh_token_db.save()

    actual = await uut.revoke_token(
        claim="REFRESH_TOKEN", token=refresh_token, revoke_reason="REVOKE_LOGOUT"
    )

    assert actual is False


async def test_is_token_revoked_cache_hit(
    _setup_cache_refresh_revoked_token_db, refresh_token_id
):
    actual = await uut.is_token_revoked(refresh_token_id)

    assert actual is True


async def test_is_token_revoked_cache_miss(_setup_cache, refresh_token_id):
    actual = await uut.is_token_revoked(refresh_token_id)

    assert actual is False
