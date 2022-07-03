from datetime import datetime
from uuid import uuid4

from pydantic import EmailStr

from app.core.api.email import service as email_service
from app.core.config import get_core_config
from app.core.event.model import EventDb

from .model import User
from .service import generate_verify_email_token

USER_REGISTERED_EVENT = "USER_REGISTERED_EVENT"
USER_UPDATED_EMAIL_EVENT = "USER_UPDATED_EMAIL_EVENT"

core_config = get_core_config()


def register_user_events(event_processor):
    event_processor.add_event_handler(USER_REGISTERED_EVENT, send_welcome_email)
    event_processor.add_event_handler(USER_UPDATED_EMAIL_EVENT, send_verify_email)


async def send_welcome_email(payload: dict) -> bool:
    await send_verify_email(payload=payload, html_template="welcome_verify_email.html")
    return True


async def send_verify_email(
    payload: dict, html_template: str = "verify_email.html", template_data: dict = None
) -> bool:
    user = payload["user"]
    token = await generate_verify_email_token(
        user=user, expire_min=core_config.verify_token_expire_min
    )
    base_url = (
        f"{core_config.base_url}{core_config.get_current_api()}{core_config.user_path}"
    )
    link = f"{base_url}{core_config.verify_path}?token={token.access_token}"

    if not template_data:
        template_data = {
            "project_name": core_config.project_name,
            "username": user.username,
        }

    template_data["link"] = link

    await email_service.process_email(
        username=user.username,
        to_email=user.email,
        html_template=html_template,
        template_data=template_data,
    )

    return True


def user_registered_event(user: User) -> EventDb:
    return EventDb(
        event_id=str(uuid4()),
        event_name=USER_REGISTERED_EVENT,
        username=user.username,
        payload={"user": user},
        date_created=datetime.now(),
    )


def user_updated_email_event(user: User, previous_email: EmailStr) -> EventDb:
    return EventDb(
        event_id=str(uuid4()),
        event_name=USER_UPDATED_EMAIL_EVENT,
        username=user.username,
        payload={"previous_email": previous_email, "user": user},
        date_created=datetime.now(),
    )
