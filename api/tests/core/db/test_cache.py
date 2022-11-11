from unittest.mock import AsyncMock, Mock, patch

from app.core.db import cache as uut
from app.core.user.model import UserDb


def test_connection():
    actual = uut.connection()

    assert actual is not None


def test_build_cache_key():
    actual = uut.build_cache_key(prefix="test_prefix", key="test_key")

    assert actual == "test_prefix-test_key"


async def test_fetch_entity_cache_miss(_setup_cache):
    actual = await uut.fetch_entity(prefix="TEST_USER", key="tester", doc_model=UserDb)

    assert actual is None


async def test_fetch_entity_cache_hit(_setup_db, _setup_cache_user_db, user_db):
    actual = await uut.fetch_entity(prefix="TEST_USER", key="tester", doc_model=UserDb)

    assert actual == user_db


async def test_cache_entity(_setup_cache, user_db):
    actual = await uut.cache_entity(
        prefix="TEST_USER", key="tester", doc=user_db, ttl=60
    )

    assert actual is True


@patch(
    "app.core.db.cache.aioredis.from_url",
    Mock(return_value=AsyncMock(delete=AsyncMock(return_value=0))),
)
async def test_delete_entity():
    actual = await uut.delete_entity(prefix="TEST_USER", key="tester")

    assert actual is False
