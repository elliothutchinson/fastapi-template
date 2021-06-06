import logging
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from app.core.config import core_config
from app.core.crud.user import update_user, update_user_private
from app.core.models.token import Credential, ResetPasswordToken, Token
from app.core.models.user import UserUpdate, UserUpdatePrivate
from app.core.security.security import (
    generate_login_token,
    get_active_user_by_email,
    get_authenticated_user,
    get_user_from_reset_token,
)
from app.core.services.email.service import send_reset_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory=core_config.templates_dir)

router = APIRouter()

base_url = f"{core_config.base_url}{core_config.api_v1}{core_config.login_path}"


@router.post(core_config.token_path, response_model=Token)
async def login_for_access_token(
    background_tasks: BackgroundTasks, form_data: OAuth2PasswordRequestForm = Depends()
):
    logger.debug("login_for_access_token()")
    cred = Credential(password=form_data.password)
    user = await get_authenticated_user(
        username=form_data.username, password=cred.password
    )
    background_tasks.add_task(
        update_user_private,
        username=user.username,
        user_update=UserUpdatePrivate(last_login=datetime.now()),
    )
    return generate_login_token(user=user, exp_min=core_config.access_token_expire_min)


@router.post("/forgot")
async def email_password_reset_token(
    background_tasks: BackgroundTasks, email: EmailStr = Body(...)
):
    logger.debug("email_password_reset_token()")
    user = await get_active_user_by_email(email=email)
    background_tasks.add_task(send_reset_email, user=user)
    return {"detail": "email reset sent"}


@router.get(core_config.reset_path)
async def reset_token_form(token: str, request: Request):
    logger.debug("reset_token_form()")
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
async def reset_password_with_token(
    reset_password_token: ResetPasswordToken = Body(...),
):
    logger.debug("reset_password_with_token()")
    user = await get_user_from_reset_token(token=reset_password_token.token)
    user_update = UserUpdate(password=reset_password_token.password.get_secret_value())
    await update_user(username=user.username, user_update=user_update)
    return RedirectResponse(url=f"{base_url}/reset_success")


@router.get("/reset_success")
@router.post("/reset_success")
def reset_success():
    return {"detail": "password has been updated"}
