from typing import Optional, Type

import orjson
from redis import asyncio as aioredis

from app.core.config import get_config
from app.core.logging import get_logger
from app.core.util import PydanticModel

logger = get_logger(__name__)

config = get_config()


def connection():

    return aioredis.from_url(config.cache_url, decode_responses=True)


def build_cache_key(prefix: str, key: str) -> str:

    return f"{prefix}-{key}"


async def fetch_entity(
    prefix: str, key: str, doc_model: Type[PydanticModel]
) -> Optional[PydanticModel]:
    entity = None

    cache_key = build_cache_key(prefix=prefix, key=key)
    redis = connection()
    cached_json = await redis.get(cache_key)

    if cached_json:
        cached_dict = orjson.loads(cached_json)
        entity = doc_model(**cached_dict)

    return entity


async def cache_entity(
    prefix: str, key: str, doc: PydanticModel, ttl: int
) -> Optional[bool]:
    cache_key = build_cache_key(prefix=prefix, key=key)
    redis = connection()

    return await redis.set(cache_key, doc.json(), ex=ttl)


async def delete_entity(prefix: str, key: str) -> bool:
    cache_key = build_cache_key(prefix=prefix, key=key)
    redis = connection()

    result = await redis.delete(cache_key)

    return result == 1
