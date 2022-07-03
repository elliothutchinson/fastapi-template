import os
from datetime import datetime
from typing import List, get_type_hints

from pydantic import SecretStr

from .model import PydanticModel


def get_utc_now() -> datetime:
    return datetime.utcnow()


def convert_datetime_to_str(data: dict, skip: List[str]):
    for key in data:
        if key in skip:
            continue
        elif type(data[key]) is dict:
            convert_datetime_to_str(data=data[key], skip=skip)
        elif type(data[key]) is datetime:
            data[key] = str(data[key])


def populate_from_env_var(doc_model: PydanticModel) -> dict:
    env = {}
    type_hints = get_type_hints(doc_model)
    for key in type_hints:
        value = os.getenv(key.upper(), None)
        value_type = type_hints[key]

        if value is None:
            continue
        elif value_type is bool:
            env[key] = value.lower() in ["1", "on", "t", "true", "y", "yes"]
        elif value_type is not SecretStr:
            env[key] = value_type(value)
        else:
            env[key] = value

    return env
