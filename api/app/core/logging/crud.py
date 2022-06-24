from typing import List

from app.core.db import crud as db_crud
from app.core.db.model import DbContext

from .model import LOG_DOC_TYPE, LogDb


def get_log_doc_id(log_id: str) -> str:
    return f"{LOG_DOC_TYPE}::{log_id}"


async def create_log(db_context: DbContext, log_db: LogDb) -> LogDb:
    doc_id = get_log_doc_id(log_id=log_db.log_id)
    return await db_crud.create_doc(db_context=db_context, doc_id=doc_id, doc=log_db)


async def get_recent_logs(db_context: DbContext, limit: int) -> List[LogDb]:
    return await db_crud.query_doc(
        db_context=db_context,
        doc_type=LOG_DOC_TYPE,
        doc_model=LogDb,
        order_by="doc->>'date_created' desc",
        limit=limit,
    )
