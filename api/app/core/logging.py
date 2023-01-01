import logging
from contextvars import copy_context
from datetime import datetime

import orjson

logging.basicConfig(level=logging.INFO)


LOG_VERSION = "1.0.0"


class ContextFilter(logging.Filter):
    def from_context(self, ctx_key, default):
        value = default
        ctx = copy_context()

        for key in ctx.keys():
            if key.name == ctx_key:
                value = ctx[key]
                break

        return value

    def filter(self, record):
        try:
            msg = str(record.msg)
        except Exception:
            msg = "Incompatible log message"

        json = {
            "date": datetime.utcnow().isoformat(),
            "levelname": record.levelname,
            "pathname": record.pathname,
            "funcName": record.funcName,
            "lineno": record.lineno,
            "msg": msg,
            "request_ip": self.from_context("request_ip", "n/a"),
            "request_id": self.from_context("request_id", "n/a"),
            "thread_name": f"{record.threadName} - {record.thread}",
            "process": record.process,
            "log_version": LOG_VERSION,
        }
        record.json = orjson.dumps(json).decode()

        return True


def log_format() -> str:

    return "%(json)s"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.filters:
        filter_obj = ContextFilter()
        logger.addFilter(filter_obj)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(log_format())
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    return logger
