import os
from datetime import datetime, timezone

# look into using list[str] etc for lists instead of import
from typing import List, Type, TypeVar, get_type_hints

from pydantic import BaseModel, SecretStr

PydanticModel = TypeVar("PydanticModel", bound=BaseModel)


def convert_timestamp_to_ttl(timestamp: int) -> int:
    now = int(datetime.now(timezone.utc).timestamp())
    ttl = timestamp - now

    return max(1, ttl)


def convert_datetime_to_str(data: dict, skip: List[str] = None):
    """
    Mutates provided data dict, stringifying datetime objects not provided in skip list.
    """
    if skip is None:
        skip = []

    for key in data:
        if key in skip:
            continue

        if isinstance(data[key], dict):
            convert_datetime_to_str(data=data[key], skip=skip)
        elif isinstance(data[key], datetime):
            data[key] = data[key].isoformat(timespec="milliseconds")


def populate_from_env(doc_model: Type[PydanticModel]) -> dict:
    env = {}
    type_hints = get_type_hints(doc_model)

    for key in type_hints:
        value = os.getenv(key.upper(), None)
        value_type = type_hints[key]

        if value is None:
            continue

        if value_type is bool:
            env[key] = value.lower() == "true"
        elif value_type is SecretStr:
            env[key] = value
        else:
            env[key] = value_type(value)

    return env
