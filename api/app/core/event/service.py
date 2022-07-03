from app.core.api.security.login.event import register_login_events
from app.core.db import service as db_service
from app.core.user.event import register_user_events

from .crud import create_event
from .model import EventDb, EventProcessor


def event_processor() -> EventProcessor:
    processor = EventProcessor()
    register_user_events(processor)
    register_login_events(processor)
    return processor


async def process_event(event: EventDb) -> EventDb:
    processor = event_processor()
    await processor.process_event(event_name=event.event_name, payload=event.payload)
    await save_event(event)


async def save_event(event: EventDb) -> EventDb:
    db_context = db_service.get_db_context()
    await create_event(db_context=db_context, event_db=event)
