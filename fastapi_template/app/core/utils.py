import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def getenv_boolean(var_name, default_value=False):
    logger.debug("getenv_boolean()")
    result = default_value
    env_value = os.getenv(var_name)
    if env_value is not None:
        result = env_value.upper() in ("TRUE", "1")
    return result


def getenv_int(var_name, default_value):
    logger.debug("getenv_int()")
    result = os.getenv(var_name, default_value)
    return int(result)


def getenv_float(var_name, default_value):
    logger.debug("getenv_float()")
    result = os.getenv(var_name, default_value)
    return float(result)


def getenv_or_raise_exception(var_name):
    logger.debug("getenv_or_raise_exception()")
    result = os.getenv(var_name)
    if result is None:
        raise Exception(
            f"Improper configuration. Environment variable {var_name} not set"
        )
    return result


def populate_from_env_var(obj):
    logger.debug("populate_from_env_var")
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
