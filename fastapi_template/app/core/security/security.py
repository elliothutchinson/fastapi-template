import logging
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from jwt.exceptions import InvalidTokenError
from pydantic import SecretStr
from starlette.requests import Request

from app.core.config import core_config
from app.core.crud.user import get_user, get_user_by_email
from app.core.exception import credentials_exception, get_bad_request_exception
from app.core.models.token import Token, TokenData
from app.core.models.user import User
from app.core.security.crypt import verify_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALGORITHM = "HS256"

LOGIN_JWT = "login token"
VERIFY_JWT = "verify token"
RESET_JWT = "reset token"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{core_config.get_current_api()}{core_config.login_path}{core_config.token_path}"
)


async def get_active_user_by_email(email: str):
    logger.debug("get_active_user_by_email()")
    user = await authenticate_user_email(email=email)
    if not user:
        raise get_bad_request_exception(detail="User not registered")
    if user.disabled:
        raise get_bad_request_exception(detail="Inactive user")
    return user


async def authenticate_user_email(email: str):
    logger.debug("authenticate_user_email()")
    user = await get_user_by_email(email=email)
    if not user:
        return False
    return user


async def get_user_from_reset_token(token: str):
    logger.debug("get_user_from_reset_token()")
    user = await authenticate_user_password_reset(token=token)
    if not user:
        raise credentials_exception
    if user.disabled:
        raise get_bad_request_exception(detail="Inactive user")
    return user


async def authenticate_user_password_reset(token: str):
    logger.debug("authenticate_user_password_reset()")
    username = verify_password_reset_token(token=token)
    if not username:
        return False
    user = await get_user(username=username)
    if not user:
        return False
    return user


async def get_user_from_verify_token(token: str):
    logger.debug("get_user_from_verify_token()")
    user = await authenticate_user_verify(token=token)
    if not user:
        raise credentials_exception
    if user.disabled:
        raise get_bad_request_exception(detail="Inactive user")
    return user


async def authenticate_user_verify(token: str):
    logger.debug("authenticate_user_verify()")
    username = verify_verify_token(token=token)
    if not username:
        return False
    user = await get_user(username=username)
    if not user:
        return False
    return user


async def get_authenticated_user(username: str, password: SecretStr):
    logger.debug("get_authenticated_user()")
    user = await authenticate_user(username=username, password=password)
    if not user:
        raise credentials_exception
    if user.disabled:
        raise get_bad_request_exception(detail="Inactive user")
    return user


async def authenticate_user(username: str, password: SecretStr):
    logger.debug("authenticate_user()")
    user = await get_user(username=username)
    if not user:
        return False
    if not verify_password(password=password, hashed_password=user.hashed_password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    logger.debug("get_current_user()")
    try:
        decoded_token = jwt.decode(
            token, core_config.secret_key, algorithms=[ALGORITHM]
        )
        if decoded_token.get("claim") != LOGIN_JWT:
            raise credentials_exception
        username: str = decoded_token.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    logger.debug("get_current_active_user()")
    if current_user.disabled:
        raise get_bad_request_exception(detail="Inactive user")
    return current_user


async def get_auth_token_from_request(request):
    logger.debug("get_auth_token_from_request()")
    auth = request.headers.get("Authorization")
    assert auth is not None, "Authorization not found in header"
    type_token = auth.split(" ")
    assert len(type_token) == 2, "Unexpected token format"
    token = type_token[1]
    return token


async def get_authenticated_user_from_request(request):
    logger.debug("get_authenticated_user_from_request()")
    token = await get_auth_token_from_request(request)
    current_user = await get_current_user(token)
    current_active_user = await get_current_active_user(current_user)
    return current_active_user


async def get_user_or_error(request):
    user = None
    error = None
    try:
        user = await get_authenticated_user_from_request(request)
    except HTTPException as e:
        logger.error(e.detail)
        error = "Invalid credentials provided"
    except AssertionError as e:
        logger.error(e)
        error = "Invalid credentials provided"
    return user, error


def create_access_token(data: dict, expires_delta: timedelta = None):
    logger.debug("create_access_token()")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, core_config.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def generate_login_token(user: User, exp_min: float):
    logger.debug("generate_login_token()")
    return generate_token(user=user, exp_min=exp_min, claim=LOGIN_JWT)


def generate_password_reset_token(user: User, exp_min: float):
    logger.debug("generate_password_reset_token()")
    return generate_token(user=user, exp_min=exp_min, claim=RESET_JWT)


def generate_verify_token(user: User, exp_min: float):
    logger.debug("generate_verify_token()")
    return generate_token(user=user, exp_min=exp_min, claim=VERIFY_JWT)


def generate_token(user: User, exp_min: float, claim: str):
    logger.debug("generate_token()")
    access_token_expires = timedelta(minutes=exp_min)
    access_token = create_access_token(
        data={"sub": user.username, "claim": claim},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type=core_config.token_type)


def verify_password_reset_token(token) -> Optional[str]:
    logger.debug("verify_password_reset_token()")
    return verify_token(token=token, claim=RESET_JWT)


def verify_verify_token(token) -> Optional[str]:
    logger.debug("verify_verify_token()")
    return verify_token(token=token, claim=VERIFY_JWT)


def verify_token(token: str, claim: str) -> Optional[str]:
    logger.debug("verify_token()")
    try:
        decoded_token = jwt.decode(token, core_config.secret_key, algorithms=["HS256"])
        if decoded_token.get("claim") != claim:
            return None
        return decoded_token.get("sub")
    except InvalidTokenError:
        return None


def validate_request(request: Request):
    logger.debug("validate_request()")
    if not request.headers.get("X-Requested-With"):
        raise get_bad_request_exception(detail="Incorrect headers")
    return request
