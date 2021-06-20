def get_logger(name):
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(name)
    return logger


def wrap(pre, post, logger, level):
    def decorate(func, *args):
        def call(*args, **kwargs):
            if pre:
                pre(logger, level, func, *args, **kwargs)
            result = func(*args, **kwargs)
            if post:
                post(logger, level, func, *args, **kwargs)
            return result

        return call

    return decorate


def trace_in(logger, level, func, *args, **kwargs):
    getattr(logger, level)(f"Entering function: {func.__name__}")


def trace_out(logger, level, func, *args, **kwargs):
    getattr(logger, level)(f"Leaving function: {func.__name__}")


def trace(logger, level="error"):
    return wrap(trace_in, trace_out, logger, level)


def info(logger):
    return trace(logger, "info")


def debug(logger):
    return trace(logger, "debug")
