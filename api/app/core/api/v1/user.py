from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.api.model import ServerResponse
from app.core.api.security.login import service as login_service
from app.core.config import get_core_config
from app.core.event.service import process_event
from app.core.user.event import user_registered_event, user_updated_email_event
from app.core.user.model import User, UserCreate, UserUpdate
from app.core.user.service import get_user_data, register_user, update_user_data, verify_email

core_config = get_core_config()

router = APIRouter()


@router.post("/", response_model=User)
async def register_new_user(user_create: UserCreate, background_tasks: BackgroundTasks):
    user = await register_user(user_create=user_create)
    event = user_registered_event(user=user)
    background_tasks.add_task(process_event, event=event)
    return user


@router.get("/", response_model=User)
async def read_current_user(login_user: User = Depends(login_service.get_login_user)):
    return await get_user_data(username=login_user.username)


@router.put("/", response_model=User)
async def update_user(
    user_update: UserUpdate,
    background_tasks: BackgroundTasks,
    login_user: User = Depends(login_service.get_login_user),
):
    user = await update_user_data(username=login_user.username, user_update=user_update)
    if user_update.email:
        event = user_updated_email_event(user=user, previous_email=user.verified_email)
    background_tasks.add_task(process_event, event=event)
    return user


@router.get(core_config.verify_path, response_model=ServerResponse)
async def verify_user_email(token: str):
    await verify_email(token=token)
    return ServerResponse(message="Email has been verified")
