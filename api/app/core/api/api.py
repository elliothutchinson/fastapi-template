from fastapi import APIRouter

from app.core.api.v1 import login, user

v1_router = APIRouter()

v1_router.include_router(login.router, prefix="/login", tags=["login"])
v1_router.include_router(user.router, prefix="/user", tags=["users"])

api_router = APIRouter()

api_router.include_router(v1_router, prefix="/api/v1")
