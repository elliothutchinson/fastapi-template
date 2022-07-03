from fastapi import Depends
from pydantic import SecretStr

from app.core.api.security import service as security_service
from app.core.api.security.token import service as token_service
from app.core.api.security.token.model import AccessToken, TokenData
from app.core.config import get_core_config
from app.core.user import service as user_service
from app.core.user.model import User, UserUpdate

LOGIN_TOKEN = "LOGIN_TOKEN"
RESET_TOKEN = "RESET_TOKEN"
REFRESH_TOKEN = "REFRESH_TOKEN"

core_config = get_core_config()


async def login_user(username: str, password: SecretStr) -> AccessToken:
    user = await security_service.get_authenticated_user(
        username=username, password=password
    )
    return await generate_login_token(user=user, with_refresh_token=True)


async def get_login_user(token: str = Depends(token_service.oauth2_scheme)):
    token_data = get_verified_login_token_data(token=token)
    return token_data.data


async def generate_login_token(
    user: User, with_refresh_token: bool = False
) -> AccessToken:
    login_token = await token_service.generate_token(
        token_type=LOGIN_TOKEN,
        expire_min=core_config.login_token_expire_min,
        username=user.username,
        data=user,
    )
    if with_refresh_token:
        refresh_token = await generate_refresh_token(username=user.username)
        login_token.refresh_token = refresh_token.access_token
    return login_token


def get_verified_login_token_data(token: str) -> TokenData:
    return token_service.get_verified_token_data(
        token=token, claim=LOGIN_TOKEN, data_model=User
    )


async def generate_refresh_token(username: str) -> AccessToken:
    return await token_service.generate_token(
        token_type=REFRESH_TOKEN,
        expire_min=core_config.refresh_token_expire_min,
        username=username,
        data={"username": username},
    )


async def refresh_token(token: str) -> AccessToken:
    token_data = token_service.get_verified_token_data(
        token=token,
        claim=REFRESH_TOKEN,
    )
    username = token_data.data["username"]

    refreshed_user = await security_service.get_active_user(username=username)

    access_token = await generate_login_token(user=refreshed_user)
    access_token.refresh_token = token

    return access_token, username


async def generate_reset_token(user: User, expire_min: float) -> AccessToken:
    return await token_service.generate_token(
        token_type=RESET_TOKEN,
        expire_min=expire_min,
        username=user.username,
        data=user,
    )


async def reset_password(token: str, password: SecretStr):
    token_data = token_service.get_verified_token_data(
        token=token, claim=RESET_TOKEN, data_model=User
    )
    user_update = UserUpdate(password=password, password_match=password)
    await user_service.update_user_data(
        token_data.data.username, user_update=user_update
    )
    await token_service.redact_user_token(token_db=token_data.metadata)
    return True
