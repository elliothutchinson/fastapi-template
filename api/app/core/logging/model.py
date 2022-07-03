from datetime import datetime
from typing import Any

from pydantic import BaseModel

LOG_DOC_TYPE = "LOG"


class Logger:
    def __init__(self, source):
        self.source = source

    def debug(self, message):
        pass

    def info(self, message):
        pass

    def error(self, message):
        pass


class LogDb(BaseModel):
    type: str = LOG_DOC_TYPE
    log_id: str
    correlation_id: str
    level: str
    source: str
    message: Any
    date_created: datetime
