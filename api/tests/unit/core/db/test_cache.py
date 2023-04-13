from unittest.mock import AsyncMock, Mock

from pydantic import BaseModel
from redis.asyncio.client import Redis

from app.core.db import cache as uut


class CacheData(BaseModel):
    data: str


def test__connection():
    actual = uut._connection()  # pylint: disable=protected-access

    assert isinstance(actual, Redis)


def test__build_cache_key():
    expected = "test_prefix-test_key"

    actual = uut._build_cache_key(  # pylint: disable=protected-access
        prefix="test_prefix", key="test_key"
    )

    assert actual == expected


async def test_fetch(mocker):
    cache_data = CacheData(data="tester")

    expected = cache_data

    mocker.patch(
        "app.core.db.cache.aioredis.from_url",
        Mock(
            return_value=AsyncMock(
                get=AsyncMock(return_value=cache_data.json()),
                set=AsyncMock(return_value=True),
                delete=AsyncMock(return_value=1),
            )
        ),
    )

    actual = await uut.fetch(prefix="test_data", key="tester", doc_model=CacheData)

    assert actual == expected


async def test_fetch_not_exists(_setup_cache):
    actual = await uut.fetch(prefix="test_data", key="tester", doc_model=CacheData)

    assert actual is None


async def test_put(_setup_cache):
    cache_data = CacheData(data="tester")

    actual = await uut.put(prefix="test_data", key="tester", doc=cache_data, ttl=60)

    assert actual is True


async def test_delete(_setup_cache):
    actual = await uut.delete(prefix="test_data", key="tester")

    assert actual is True
