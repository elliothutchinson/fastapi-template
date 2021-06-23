import inspect
from functools import wraps


def get_logger(name):
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name)
    return logger


def logged(logger, level="debug"):
    def outter(func):
        log = f"{func.__name__} invoked"

        @wraps(func)
        def inner(*args, **kwargs):
            getattr(logger, level)(log)
            return func(*args, **kwargs)

        @wraps(func)
        async def inner_async(*args, **kwargs):
            getattr(logger, level)(log)
            return await func(*args, **kwargs)

        if inspect.iscoroutinefunction(func):
            return inner_async
        return inner

    return outter


def info(logger):
    return logged(logger, level="info")


def debug(logger):
    return logged(logger, level="debug")


def error(logger):
    return logged(logger, level="error")
