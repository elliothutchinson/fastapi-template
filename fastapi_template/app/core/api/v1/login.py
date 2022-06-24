from fastapi import APIRouter, BackgroundTasks, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from app.core import logger as trace
from app.core.config import core_config
from app.core.crud.user import update_user
from app.core.logger import get_logger
from app.core.models.token import Credential, ResetPasswordToken, Token
from app.core.models.user import UserUpdate
from app.core.security.security import (
    generate_login_token,
    get_active_user_by_email,
    get_authenticated_user,
    get_user_from_reset_token,
)
from app.core.services.event.models import Event
from app.core.services.event.processor import (
    FORGOT_PASSWORD_EVENT,
    LOGIN_EVENT,
    process_event,
)

logger = get_logger(__name__)

templates = Jinja2Templates(directory=core_config.templates_dir)

router = APIRouter()

base_url = f"{core_config.base_url}{core_config.api_v1}{core_config.login_path}"


@router.post(core_config.token_path, response_model=Token)
@trace.debug(logger)
async def login_for_access_token(
    background_tasks: BackgroundTasks, form_data: OAuth2PasswordRequestForm = Depends()
):
    cred = Credential(password=form_data.password)
    user = await get_authenticated_user(
        username=form_data.username, password=cred.password
    )
    event = Event(name=LOGIN_EVENT, payload=user)
    background_tasks.add_task(process_event, event=event)
    return generate_login_token(user=user, exp_min=core_config.access_token_expire_min)


@router.post(core_config.forgot_path)
@trace.debug(logger)
async def email_password_reset_token(
    background_tasks: BackgroundTasks, email: EmailStr = Body(...)
):
    user = await get_active_user_by_email(email=email)
    event = Event(name=FORGOT_PASSWORD_EVENT, payload=user)
    background_tasks.add_task(process_event, event=event)
    return {"detail": "email reset sent"}


@router.get(core_config.reset_path)
@trace.debug(logger)
async def reset_token_form(token: str, request: Request):
    await get_user_from_reset_token(token=token)
    url = f"{base_url}{core_config.reset_path}"
    return templates.TemplateResponse(
        "reset_password.html",
        {
            "request": request,
            "url": url,
        },
    )


@router.post(core_config.reset_path)
@trace.debug(logger)
async def reset_password_with_token(
    reset_password_token: ResetPasswordToken = Body(...),
):
    user = await get_user_from_reset_token(token=reset_password_token.token)
    user_update = UserUpdate(password=reset_password_token.password.get_secret_value())
    await update_user(username=user.username, user_update=user_update)
    return RedirectResponse(url=f"{base_url}/reset_success")


@router.get(core_config.reset_success_path)
@router.post(core_config.reset_success_path)
@trace.debug(logger)
def reset_success():
    return {"detail": "password has been updated"}
