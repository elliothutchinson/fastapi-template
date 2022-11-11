from fastapi import APIRouter, Depends

from app.core.security.auth import get_user_from_token
from app.core.user import service as user_service
from app.core.user.model import USER_ROLE, User, UserCreate, UserUpdate

router = APIRouter()


@router.post("/", response_model=User)
async def register_new_user(user_create: UserCreate):
    user = await user_service.create_user(user_create=user_create, roles=[USER_ROLE])

    return user


@router.get("/", response_model=User)
async def read_current_user(
    current_user: User = Depends(get_user_from_token),
):
    user = await user_service.fetch_user(current_user.username)

    return user


@router.put("/", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_user_from_token),
):
    updated_user = await user_service.update_user(
        username=current_user.username, user_update=user_update
    )

    return updated_user
