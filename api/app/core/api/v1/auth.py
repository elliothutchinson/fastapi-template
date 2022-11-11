from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr

from app.core.api.model import ServerResponse
from app.core.security.auth import (
    AuthToken,
    refresh_access_token,
    user_login,
    user_logout,
)

router = APIRouter()


@router.post("/login", response_model=AuthToken)
async def login_for_auth_token(form_data: OAuth2PasswordRequestForm = Depends()):
    auth_token = await user_login(
        username=form_data.username, password=SecretStr(form_data.password)
    )

    return auth_token


@router.post("/logout", response_model=ServerResponse)
async def logout_auth_token(auth_token: AuthToken):
    access_revoked, refresh_revoked = await user_logout(
        access_token=auth_token.access_token, refresh_token=auth_token.refresh_token
    )

    return ServerResponse(
        message=f"access_token revoked: {access_revoked}, refresh_token revoked: {refresh_revoked}"
    )


@router.post("/refresh", response_model=AuthToken)
async def refresh_auth_token(auth_token: AuthToken):
    auth_token = await refresh_access_token(auth_token.refresh_token)

    return auth_token
