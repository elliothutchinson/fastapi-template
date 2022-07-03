import inspect
from datetime import datetime
from typing import Any

from pydantic import BaseModel

EVENT_DOC_TYPE = "EVENT"


class EventDb(BaseModel):
    type: str = EVENT_DOC_TYPE
    event_id: str
    event_name: str
    username: str = None
    payload: Any
    date_created: datetime


class EventProcessor:
    def __init__(self):
        self.events = {}

    def add_event_handler(self, event_name, handler):
        handlers = self.events.get(event_name, set())
        handlers.add(handler)

        if event_name not in self.events:
            self.events[event_name] = handlers

    def default_event_not_supported(self, payload):
        pass

    async def process_event(self, event_name, payload):
        handlers = self.events.get(event_name, {self.default_event_not_supported})

        for handler in handlers:
            if inspect.iscoroutinefunction(handler):
                await handler(payload)
            else:
                handler(payload)
