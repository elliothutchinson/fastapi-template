import os

from app.core import logger as trace
from app.core.logger import get_logger

logger = get_logger(__name__)


@trace.debug(logger)
def getenv_boolean(var_name, default_value=False):
    result = default_value
    env_value = os.getenv(var_name)
    if env_value is not None:
        result = env_value.upper() in ("TRUE", "1")
    return result


@trace.debug(logger)
def getenv_int(var_name, default_value):
    result = os.getenv(var_name, default_value)
    return int(result)


@trace.debug(logger)
def getenv_float(var_name, default_value):
    result = os.getenv(var_name, default_value)
    return float(result)


@trace.debug(logger)
def getenv_or_raise_exception(var_name):
    result = os.getenv(var_name)
    if result is None:
        raise Exception(
            f"Improper configuration. Environment variable {var_name} not set"
        )
    return result


@trace.debug(logger)
def populate_from_env_var(obj):
    for key in vars(obj):
        key_upper = key.upper()
        value_default = getattr(obj, key)
        value_type = type(value_default)
        value = os.getenv(key_upper, value_default)
        if value_type is str:
            value = os.getenv(key_upper, value_default)
        elif value_type is int:
            value = getenv_int(key_upper, value_default)
        elif value_type is float:
            value = getenv_float(key_upper, value_default)
        elif value_type is bool:
            value = getenv_boolean(key_upper, value_default)
        else:
            raise Exception(
                f"Unsupported type '{value_type}' for {key}={value_default}"
            )
        setattr(obj, key, value)
