from fastapi import APIRouter

from app.core.api.v1 import login, users
from app.core.config import core_config
from app.core.logger import get_logger
from app.core.services.social import api as social
from app.core.services.social.config import social_config

logger = get_logger(__name__)

v1_router = APIRouter()

v1_router.include_router(login.router, prefix=core_config.login_path, tags=["login"])
v1_router.include_router(users.router, prefix=core_config.users_path, tags=["users"])

if social_config.social_enabled:
    v1_router.include_router(
        social.router, prefix=social_config.social_path, tags=["social"]
    )

api_router = APIRouter()
api_router.include_router(v1_router, prefix=core_config.api_v1)
