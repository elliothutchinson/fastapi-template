import os
from datetime import datetime
from typing import List

from pydantic import SecretStr

from .model import PydanticModel


def get_utc_now():
    return datetime.utcnow()


def convert_datetime_to_str(data: dict, skip: List[str]):
    for key in data:
        if key in skip:
            continue
        elif type(data[key]) is dict:
            convert_datetime_to_str(data=data[key], skip=skip)
        elif type(data[key]) is datetime:
            data[key] = str(data[key])


# todo: find way to populate type from default without passing default value
# to prevent accidentally forgetting env var and using sensitive value from hardcoded default
def populate_from_env_var(obj: PydanticModel):
    for key in vars(obj):
        value_default = getattr(obj, key)
        value_type = type(value_default)
        value = os.getenv(key.upper(), None)

        if value is None:
            value = value_default
        elif value_type in [int, float]:
            value = value_type(value)
        elif value_type is bool:
            value = value.lower() in ["1", "on", "t", "true", "y", "yes"]
        elif value_type is SecretStr:
            value = SecretStr(value)

        setattr(obj, key, value)
