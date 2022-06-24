from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr

from app.core.api.model import ServerResponse
from app.core.api.security.login.model import ForgottenPassword, PasswordResetToken
from app.core.api.security.login.event import login_success_event, request_password_reset_event
from app.core.api.security.login.service import login_user, reset_password
from app.core.api.security.token.model import AccessToken
from app.core.config import get_core_config
from app.core.event.service import process_event

core_config = get_core_config()

router = APIRouter()

#todo: look into rate limit
# todo: lock after n failed attemps

@router.post(core_config.token_path, response_model=AccessToken)
async def login_for_access_token(
    background_tasks: BackgroundTasks, form_data: OAuth2PasswordRequestForm = Depends()
):
    access_token = await login_user(
        username=form_data.username, password=SecretStr(form_data.password)
    )
    event = login_success_event(username=form_data.username)
    background_tasks.add_task(process_event, event=event)
    return access_token


# forgot username
# todo: implement


@router.post(core_config.forgot_path, response_model=ServerResponse)
async def email_reset_password_token(
    background_tasks: BackgroundTasks, forgotten_password: ForgottenPassword
):
    event = request_password_reset_event(username=forgotten_password.username)
    background_tasks.add_task(process_event, event=event)
    return ServerResponse(message="Reset password email requested")


# todo: implement
# email reset link GET


@router.post(core_config.reset_path, response_model=ServerResponse)
async def user_reset_password(password_reset_token: PasswordResetToken):
    await reset_password(token=password_reset_token.token, password=password_reset_token.password)
    return ServerResponse(message="Password has been reset")


# refresh token support
# todo: implement

# reset password
# todo: implement
