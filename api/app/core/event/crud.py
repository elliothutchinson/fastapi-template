from typing import List

from app.core.db import crud as db_crud
from app.core.db.model import DbContext

from .model import EVENT_DOC_TYPE, EventDb


def get_event_doc_id(event_id: str) -> str:
    return f"{EVENT_DOC_TYPE}::{event_id}"


async def create_event(db_context: DbContext, event_db: EventDb) -> EventDb:
    doc_id = get_event_doc_id(event_id=event_db.event_id)
    return await db_crud.create_doc(db_context=db_context, doc_id=doc_id, doc=event_db)


async def get_events_for_user(db_context: DbContext, username: str) -> List[EventDb]:
    return await db_crud.query_doc(
        db_context=db_context,
        doc_type=EVENT_DOC_TYPE,
        doc_model=EventDb,
        where_clause="doc->>'username'=$1",
        where_values=[username],
        order_by="doc->>'date_created'",
    )


# todo: get events by name for user


async def get_events_by_name(db_context: DbContext, event_name: str) -> List[EventDb]:
    return await db_crud.query_doc(
        db_context=db_context,
        doc_type=EVENT_DOC_TYPE,
        doc_model=EventDb,
        where_clause="doc->>'event_name'=$1",
        where_values=[event_name],
        order_by="doc->>'date_created'",
    )
