from fastapi import APIRouter

from app.core.api.v1 import login, user
from app.core.config import get_core_config

core_config = get_core_config()

v1_router = APIRouter()

v1_router.include_router(login.router, prefix=core_config.login_path, tags=["login"])
v1_router.include_router(user.router, prefix=core_config.user_path, tags=["user"])

api_router = APIRouter()

api_router.include_router(v1_router, prefix=core_config.api_v1)
