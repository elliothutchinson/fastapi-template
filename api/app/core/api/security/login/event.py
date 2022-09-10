from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import EmailStr

from app.core.api.email import service as email_service
from app.core.api.email.config import get_email_config
from app.core.config import get_core_config
from app.core.event.model import EventDb
from app.core.user import service as user_service
from app.core.user.model import UserUpdatePrivate

from .service import generate_reset_token

LOGIN_SUCCESS_EVENT = "LOGIN_SUCCESS_EVENT"
LOGIN_REFRESH_EVENT = "LOGIN_REFRESH_EVENT"
LOGIN_FAIL_EVENT = "LOGIN_FAIL_EVENT"
REQUEST_RESET_PASSWORD_EVENT = "REQUEST_RESET_PASSWORD_EVENT"
REQUEST_USERNAME_REMINDER_EVENT = "REQUEST_USERNAME_REMINDER_EVENT"

core_config = get_core_config()


def register_login_events(event_processor):
    event_processor.add_event_handler(LOGIN_SUCCESS_EVENT, update_last_login)
    event_processor.add_event_handler(LOGIN_REFRESH_EVENT, handle_refreshed_login)
    event_processor.add_event_handler(LOGIN_FAIL_EVENT, handle_failed_login)
    event_processor.add_event_handler(
        REQUEST_RESET_PASSWORD_EVENT, send_reset_password_email
    )
    event_processor.add_event_handler(
        REQUEST_USERNAME_REMINDER_EVENT, send_username_reminder_email
    )


async def update_last_login(payload: dict) -> bool:
    user_update_private = UserUpdatePrivate(last_login=payload["last_login"])
    await user_service.update_user_private_data(
        username=payload["username"], user_update_private=user_update_private
    )
    return True


# no op for now, just for audit
async def handle_refreshed_login(payload: Any) -> bool:
    return True


# no op for now, just for audit
async def handle_failed_login(payload: Any) -> bool:
    return True


async def send_reset_password_email(payload: dict) -> bool:
    user = None
    try:
        user = await user_service.get_user_data(username=payload["username"])
    except:
        return

    email_config = get_email_config()

    token = await generate_reset_token(
        user=user, expire_min=email_config.email_reset_token_expire_min
    )
    base_url = (
        f"{core_config.base_url}{core_config.get_current_api()}{core_config.login_path}"
    )
    link = f"{base_url}{core_config.reset_path}?token={token.access_token}"

    await email_service.process_email(
        username=user.username,
        to_email=user.email,
        html_template="reset_password.html",
        template_data={
            "project_name": core_config.project_name,
            "username": user.username,
            "email": user.email,
            "link": link,
            "valid_min": email_config.email_reset_token_expire_min,
        },
    )
    return True


async def send_username_reminder_email(payload: dict) -> bool:
    user = None
    try:
        user = await user_service.get_user_data_by_email(email=payload["email"])
    except:
        return

    await email_service.process_email(
        username=user.username,
        to_email=user.email,
        html_template="forgot_username.html",
        template_data={
            "project_name": core_config.project_name,
            "username": user.username,
        },
    )
    return True


def request_reset_password_event(username: str) -> EventDb:
    return EventDb(
        event_id=str(uuid4()),
        event_name=REQUEST_RESET_PASSWORD_EVENT,
        username=username,
        payload={"username": username},
        date_created=datetime.now(),
    )


def request_username_reminder_event(email: EmailStr) -> EventDb:
    return EventDb(
        event_id=str(uuid4()),
        event_name=REQUEST_USERNAME_REMINDER_EVENT,
        username=email,
        payload={"email": email},
        date_created=datetime.now(),
    )


def login_success_event(username: str) -> EventDb:
    date_created = datetime.now()
    return EventDb(
        event_id=str(uuid4()),
        event_name=LOGIN_SUCCESS_EVENT,
        username=username,
        payload={"last_login": date_created, "username": username},
        date_created=date_created,
    )


def login_refresh_event(username: str) -> EventDb:
    return EventDb(
        event_id=str(uuid4()),
        event_name=LOGIN_REFRESH_EVENT,
        username=username,
        payload={"username": username},
        date_created=datetime.now(),
    )


def login_fail_event(username: str) -> EventDb:
    return EventDb(
        event_id=str(uuid4()),
        event_name=LOGIN_FAIL_EVENT,
        username={"username": username},
        date_created=datetime.now(),
    )
