from fastapi import Depends
from pydantic import SecretStr

from app.core.api.security.service import get_authenticated_user
from app.core.api.security.token import service as token_service
from app.core.api.security.token.model import AccessToken, TokenData
from app.core.config import get_core_config
from app.core.user.model import User, UserUpdate
from app.core.user import service as user_service

LOGIN_TOKEN = "login_token"
RESET_TOKEN = "reset_token"


async def get_login_user(token: str = Depends(token_service.oauth2_scheme)):
    token_data = get_verified_login_token_data(token=token)
    return token_data.data


async def reset_password(token: str, password: SecretStr):
    token_data = token_service.get_verified_token_data(
        token=token, claim=RESET_TOKEN, data_model=User 
    )
    user_update = UserUpdate(password=password, password_match=password)
    await user_service.update_user_data(token_data.data.username, user_update=user_update)
    await token_service.redact_user_token(token_db=token_data.metadata)
    return True


async def login_user(username: str, password: SecretStr) -> AccessToken:
    user = await get_authenticated_user(username=username, password=password)
    return await generate_login_token(user=user)


async def generate_login_token(user: User) -> AccessToken:
    core_config = get_core_config()
    return await token_service.generate_token(
        token_type=LOGIN_TOKEN,
        expire_min=core_config.login_token_expire_min,
        username=user.username,
        data=user,
    )


def get_verified_login_token_data(token: str) -> TokenData:
    return token_service.get_verified_token_data(
        token=token, claim=LOGIN_TOKEN, data_model=User
    )
