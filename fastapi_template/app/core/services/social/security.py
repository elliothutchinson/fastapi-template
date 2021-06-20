import secrets
import string

from fastapi import Body, Depends, HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token
from starlette.requests import Request

from app.core import logger as trace
from app.core.logger import get_logger
from app.core.security.security import validate_request

from .config import social_config
from .models import SocialToken

logger = get_logger(__name__)


@trace.debug(logger)
async def validate_google_client_token(auth_code):
    email = None
    name = None
    try:
        idinfo = id_token.verify_oauth2_token(
            auth_code, requests.Request(), social_config.google_client_id
        )
        logger.debug(idinfo)
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Wrong issuer.")

        if idinfo["email"] and idinfo["email_verified"]:
            email = idinfo.get("email")
            name = idinfo["name"]
        else:
            raise HTTPException(
                status_code=400, detail="Unable to validate social login"
            )
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=400,
            detail="Exception occurred. Unable to validate social login",
        )
    return email, name


@trace.debug(logger)
async def get_user_info_from_social_token(
    social_token: SocialToken = Body(...), request: Request = Depends(validate_request)
):
    oauth2_source = request.headers.get("X-Social-OAuth2-Type")
    auth_code = social_token.social_token
    logger.debug(f"authcode: {auth_code}")

    email = None
    name = None
    if oauth2_source == "google-client":
        email, name = await validate_google_client_token(auth_code)
    else:
        raise HTTPException(
            status_code=400, detail="Unsupported social authentication provider"
        )
    logger.debug(f"email: {email}, name: {name}")
    return email, name


@trace.debug(logger)
def generate_random_password():
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for i in range(25))
