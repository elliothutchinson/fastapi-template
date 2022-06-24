from app.core import logger as trace
from app.core.crud.user import update_user_private
from app.core.logger import get_logger
from app.core.models.user import UserUpdatePrivate
from app.core.services.email.service import send_reset_email, send_welcome_email
from app.core.services.event.models import Event

logger = get_logger(__name__)


USER_REGISTER_EVENT = "USER_REGISTER_EVENT"
EMAIL_CHANGE_EVENT = "EMAIL_CHANGE_EVENT"
FORGOT_PASSWORD_EVENT = "FORGOT_PASSWORD_EVENT"
LOGIN_EVENT = "LOGIN_EVENT"
FAILED_LOGIN_EVENT = "FAILED_LOGIN_EVENT"


@trace.info(logger)
async def process_event(event: Event):
    if event.name == USER_REGISTER_EVENT:
        await process_user_register_event(event=event)
    elif event.name == EMAIL_CHANGE_EVENT:
        await process_email_change_event(event=event)
    elif event.name == FORGOT_PASSWORD_EVENT:
        await process_forgot_password_event(event=event)
    elif event.name == LOGIN_EVENT:
        await process_login_event(event=event)
    elif event.name == FAILED_LOGIN_EVENT:
        await process_failed_login_event(event=event)
    else:
        logger.error(f"Unknown event `{event.name}`, skipping event")


@trace.info(logger)
async def process_user_register_event(event: Event):
    await send_welcome_email(user=event.payload)


@trace.info(logger)
async def process_email_change_event(event: Event):
    # TODO: implement, send verify email to new email
    pass


@trace.info(logger)
async def process_forgot_password_event(event: Event):
    await send_reset_email(user=event.payload)


@trace.info(logger)
async def process_login_event(event: Event):
    await update_user_private(
        username=event.payload.username,
        user_update=UserUpdatePrivate(last_login=event.date_created),
    )


@trace.info(logger)
async def process_failed_login_event(event: Event):
    # todo: implement
    pass