from datetime import datetime
from typing import Any
from uuid import uuid4

from app.core.api.email import service as email_service
from app.core.event.model import EventDb
from app.core.user.model import UserUpdatePrivate
from app.core.user import service as user_service

LOGIN_SUCCESS_EVENT = "LOGIN_SUCCESS_EVENT"
LOGIN_FAIL_EVENT = "LOGIN_FAIL_EVENT"
REQUEST_PASSWORD_RESET_EVENT = "REQUEST_PASSWORD_RESET_EVENT"


def register_login_events(event_processor):
    event_processor.add_event_handler(LOGIN_SUCCESS_EVENT, update_last_login)
    event_processor.add_event_handler(LOGIN_FAIL_EVENT, handle_failed_login)
    event_processor.add_event_handler(REQUEST_PASSWORD_RESET_EVENT, send_reset_password_email)


async def update_last_login(payload: dict):
    user_update_private = UserUpdatePrivate(last_login=payload["last_login"])
    await user_service.update_user_private_data(username=payload["username"], user_update_private=user_update_private)
    return True


# no op for now, just for audit
async def handle_failed_login(payload: Any):
    pass


# todo: impl
async def send_reset_password_email():
    await email_service.process_email(
        username=None,
        to_email=None,
        html_template=None,
        template_data=None
    )
    return True


def request_password_reset_event(username: str):
    return EventDb(
        event_id=str(uuid4()),
        event_name=REQUEST_PASSWORD_RESET_EVENT,
        username=username,
        date_created=datetime.now(),
    )


def login_success_event(username: str) -> EventDb:
    date_created = datetime.now()
    return EventDb(
        event_id=str(uuid4()),
        event_name=LOGIN_SUCCESS_EVENT,
        username=username,
        payload={ "last_login": date_created, "username": username },
        date_created=date_created,
    )


def login_fail_event(username: str) -> EventDb:
    return EventDb(
        event_id=str(uuid4()),
        event_name=LOGIN_FAIL_EVENT,
        username=username,
        date_created=datetime.now(),
    )
