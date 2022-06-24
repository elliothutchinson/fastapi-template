from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import EmailStr

from app.core.event.model import EventDb

from .model import User

USER_REGISTERED_EVENT = "USER_REGISTERED_EVENT"
USER_VERIFIED_EMAIL_EVENT = "USER_VERIFIED_EMAIL_EVENT"
USER_UPDATED_EMAIL_EVENT = "USER_UPDATED_EMAIL_EVENT"


def register_user_events(event_processor):
    event_processor.add_event_handler(USER_REGISTERED_EVENT, send_welcome_email)
    event_processor.add_event_handler(USER_VERIFIED_EMAIL_EVENT, mark_email_verified)
    event_processor.add_event_handler(USER_UPDATED_EMAIL_EVENT, notify_previous_email)
    event_processor.add_event_handler(USER_UPDATED_EMAIL_EVENT, send_verify_email)


# todo: implement
async def send_welcome_email(payload: str):
    pass


# todo: implement
async def mark_email_verified(payload: Any):
    pass


# todo: implement
async def notify_previous_email(payload: dict):
    pass


# todo: implement
async def send_verify_email(payload: dict):
    pass


def user_registered_event(user: User) -> EventDb:
    return EventDb(
        event_id=str(uuid4()),
        event_name=USER_REGISTERED_EVENT,
        username=user.username,
        payload=user.email,
        date_created=datetime.now(),
    )


def user_updated_email_event(user: User, previous_email: EmailStr) -> EventDb:
    return EventDb(
        event_id=str(uuid4()),
        event_name=USER_UPDATED_EMAIL_EVENT,
        username=user.username,
        payload={"previous_email": previous_email, "changed_email" : user.email},
        date_created=datetime.now(),
    )
