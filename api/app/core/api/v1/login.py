from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import SecretStr

from app.core.api.model import ServerResponse
from app.core.api.security.login.event import (
    login_success_event,
    login_refresh_event,
    request_reset_password_event,
    request_username_reminder_event,
)
from app.core.api.security.login.model import ForgottenPassword, ResetPasswordToken, ForgottenUsername
from app.core.api.security.login.service import login_user, reset_password, refresh_token
from app.core.api.security.token.model import AccessToken
from app.core.config import get_core_config
from app.core.event.service import process_event

templates = Jinja2Templates(directory=get_core_config().templates_dir)

core_config = get_core_config()

router = APIRouter()


@router.post(core_config.token_path, response_model=AccessToken)
async def login_for_access_token(
    background_tasks: BackgroundTasks, form_data: OAuth2PasswordRequestForm = Depends()
):
    access_token = await login_user(
        username=form_data.username, password=SecretStr(form_data.password)
    )
    event = login_success_event(username=form_data.username)
    background_tasks.add_task(process_event, event=event)
    return access_token


@router.post(core_config.refresh_path, response_model=AccessToken)
async def refresh_access_token(background_tasks: BackgroundTasks, token: str):
    access_token, username = await refresh_token(token=token)
    event = login_refresh_event(username=username)
    background_tasks.add_task(process_event, event=event)
    return access_token


@router.post(core_config.forgot_password_path, response_model=ServerResponse)
async def email_reset_password_token(
    background_tasks: BackgroundTasks, forgotten_password: ForgottenPassword
):
    event = request_reset_password_event(username=forgotten_password.username)
    background_tasks.add_task(process_event, event=event)
    return ServerResponse(message="Reset password email requested")


@router.get(core_config.reset_path)
async def reset_token_form(token: str, request: Request):
    base_url = (
        f"{core_config.base_url}{core_config.get_current_api()}{core_config.login_path}"
    )
    url = f"{base_url}{core_config.reset_path}"
    return templates.TemplateResponse(
        "reset_password.html",
        {
            "request": request,
            "url": url,
            "token": token,
        },
    )


@router.post(core_config.reset_path, response_model=ServerResponse)
async def user_reset_password(reset_password_token: ResetPasswordToken):
    await reset_password(
        token=reset_password_token.token, password=reset_password_token.password
    )
    return ServerResponse(message="Password has been reset")


@router.post(core_config.forgot_username_path, response_model=ServerResponse)
async def email_forgotten_username(
    background_tasks: BackgroundTasks, forgotten_username: ForgottenUsername
):
    event = request_username_reminder_event(email=forgotten_username.email)
    background_tasks.add_task(process_event, event=event)
    return ServerResponse(message="Username reminder email requested")