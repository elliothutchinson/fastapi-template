from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import EmailStr
from starlette.requests import Request

from app.core import logger as trace
from app.core.config import core_config
from app.core.crud.user import (
    create_user,
    get_user,
    get_user_by_email,
    update_user,
    update_user_private,
)
from app.core.exception import not_found_exception
from app.core.logger import get_logger
from app.core.models.user import (
    User,
    UserCreate,
    UserPublic,
    UserUpdate,
    UserUpdatePrivate,
)
from app.core.security.security import (
    get_current_active_user,
    get_user_from_verify_token,
)
from app.core.services.cache import fetch_data
from app.core.services.event.models import Event
from app.core.services.event.processor import USER_REGISTER_EVENT, process_event

logger = get_logger(__name__)


router = APIRouter()

# todo: move base urls to config


@router.get("/cache/{hello}")
@trace.debug(logger)
async def read_cache(hello: str):
    logger.info(fetch_data.cache_info())
    return fetch_data(hello)


@router.get("/", response_model=User)
@trace.debug(logger)
async def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/username/{username}", response_model=UserPublic)
@trace.debug(logger)
async def read_user_by_username(username: str):
    user = await get_user(username)
    if user is None:
        raise not_found_exception
    return user


@router.get("/email/{email}", response_model=UserPublic)
@trace.debug(logger)
async def read_user_by_email(email: EmailStr):
    user = await get_user_by_email(email)
    if user is None:
        raise not_found_exception
    return user


@router.put("/", response_model=User)
@trace.debug(logger)
async def update_user_data(
    user_update: UserUpdate, current_user: User = Depends(get_current_active_user)
):
    return await update_user(username=current_user.username, user_update=user_update)


@router.post("/", response_model=User)
@trace.debug(logger)
async def register_user(user_in: UserCreate, background_tasks: BackgroundTasks):
    user = await create_user(user_in=user_in)
    event = Event(name=USER_REGISTER_EVENT, payload=user)
    background_tasks.add_task(process_event, event=event)
    return user


@router.get(core_config.verify_path)
@trace.debug(logger)
async def verify_account(token: str, request: Request):
    user = await get_user_from_verify_token(token=token)
    user_update = UserUpdatePrivate(verified=True)
    await update_user_private(username=user.username, user_update=user_update)
    return {"detail": "Account has been verified"}
