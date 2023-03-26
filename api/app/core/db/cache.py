from typing import Optional, Type

import orjson
from redis import asyncio as aioredis

from app.core.config import get_config
from app.core.logging import get_logger
from app.core.util import PydanticModel

logger = get_logger(__name__)

config = get_config()


def _connection():
    return aioredis.from_url(config.cache_url, decode_responses=True)


def _build_cache_key(prefix: str, key: str) -> str:
    return f"{prefix}-{key}"


async def fetch(
    prefix: str, key: str, doc_model: Type[PydanticModel]
) -> Optional[PydanticModel]:
    entity = None

    cache_key = _build_cache_key(prefix=prefix, key=key)
    redis = _connection()
    cached_json = await redis.get(cache_key)

    if cached_json:
        cached_dict = orjson.loads(cached_json)
        entity = doc_model(**cached_dict)

    return entity


async def put(prefix: str, key: str, doc: PydanticModel, ttl: int) -> Optional[bool]:
    cache_key = _build_cache_key(prefix=prefix, key=key)
    redis = _connection()

    return await redis.set(cache_key, doc.json(), ex=ttl)


async def delete(prefix: str, key: str) -> bool:
    cache_key = _build_cache_key(prefix=prefix, key=key)
    redis = _connection()

    result = await redis.delete(cache_key)

    return result == 1
