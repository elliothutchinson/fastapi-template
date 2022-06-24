from datetime import datetime
from uuid import uuid4

from app.core.db import service as db_service

from .crud import create_log
from .model import LogDb


def log(message: str):
    pass


async def save_log(level: str, source: str, message: str) -> LogDb:
    log_db = LogDb(
        log_id=str(uuid4()),
        level=level,
        source=source,
        message=message,
        datetime=datetime.now(),
    )
    db_context = db_service.get_db_context()
    return await create_log(db_context=db_context, log_db=log_db)
