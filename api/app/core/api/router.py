from fastapi import APIRouter

from app.core.api.v1.auth import router as auth_router
from app.core.api.v1.health import router as health_router
from app.core.api.v1.user import router as user_router

v1_router = APIRouter()
v1_router.include_router(health_router, prefix="/health", tags=["Service health"])
v1_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
v1_router.include_router(user_router, prefix="/user", tags=["User"])

router = APIRouter()
router.include_router(v1_router, prefix="/api/v1")
