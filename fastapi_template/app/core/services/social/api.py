from datetime import datetime
from typing import Tuple

from fastapi import APIRouter, BackgroundTasks, Body, Depends
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from app.core import logger as trace
from app.core.config import core_config
from app.core.crud.user import create_user, update_user_private
from app.core.logger import get_logger
from app.core.models.token import Token
from app.core.models.user import User, UserCreate, UserUpdatePrivate
from app.core.security.security import generate_login_token, get_active_user_by_email
from app.core.services.email.service import send_welcome_email

from .config import social_config
from .models import UserCreateSocial
from .security import generate_random_password, get_user_info_from_social_token

templates = Jinja2Templates(directory="ui/templates")

logger = get_logger(__name__)

router = APIRouter()

base_url = (
    f"{core_config.base_url}{core_config.get_current_api()}{social_config.social_path}"
)


@router.get("/google_client_login")
@trace.debug(logger)
def login_for_google_client(request: Request):
    url = f"{base_url}{social_config.swap_token_path}"
    return templates.TemplateResponse(
        "google_client_login.html",
        {
            "request": request,
            "google_client_id": social_config.google_client_id,
            "redirect_url": url,
        },
    )


@router.get("/google_client_register")
@trace.debug(logger)
def register_for_google_client(request: Request):
    url = f"{base_url}{social_config.social_register_path}"
    return templates.TemplateResponse(
        "google_client_register.html",
        {
            "request": request,
            "google_client_id": social_config.google_client_id,
            "redirect_url": url,
        },
    )


@router.post(social_config.social_register_path, response_model=User)
@trace.debug(logger)
async def register_user_by_social(
    background_tasks: BackgroundTasks,
    user_create_social: UserCreateSocial = Body(...),
    email_name: Tuple[str, str] = Depends(get_user_info_from_social_token),
):
    logger.debug(email_name)
    user_create = UserCreate(
        username=user_create_social.username,
        password=generate_random_password(),
        email=email_name[0],
        full_name=email_name[1],
    )
    user = await create_user(user_in=user_create)
    background_tasks.add_task(send_welcome_email, user=user)
    return user


@router.post(social_config.swap_token_path, response_model=Token)
@trace.debug(logger)
async def swap_token(
    background_tasks: BackgroundTasks,
    email_name: Tuple[str, str] = Depends(get_user_info_from_social_token),
):
    logger.debug(f"email_name: {email_name}")
    user = await get_active_user_by_email(email=email_name[0])
    background_tasks.add_task(
        update_user_private,
        username=user.username,
        user_update=UserUpdatePrivate(last_login=datetime.now()),
    )
    return generate_login_token(user=user, exp_min=core_config.access_token_expire_min)
