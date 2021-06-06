import logging
import secrets
import string

from fastapi import Body, Depends, HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token
from starlette.requests import Request

from app.core.security.security import validate_request

from .config import social_config
from .models import SocialToken

logger = logging.getLogger(__name__)


async def validate_google_client_token(auth_code):
    logger.debug("validate_google_client_token()")
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


async def get_user_info_from_social_token(
    social_token: SocialToken = Body(...), request: Request = Depends(validate_request)
):
    logger.debug("get_user_info_from_social_token()")
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


def generate_random_password():
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for i in range(25))
