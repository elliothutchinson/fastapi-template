from datetime import datetime, timedelta
from typing import Any, List, Type, Union
from uuid import uuid4

import jwt
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from app.core.config import get_core_config
from app.core.db import service as db_service
from app.core.model import PydanticModel
from app.core.util import convert_datetime_to_str, get_utc_now

from .crud import create_token, get_valid_tokens_for_user, update_token
from .model import AccessToken, InvalidTokenException, TokenData, TokenDb, TokenUpdateDb

ALGORITHM = "HS256"


core_config = get_core_config()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{core_config.get_current_api()}{core_config.login_path}{core_config.token_path}"
)


# todo: check token is not redacted
# at service startup/out of request cycle refresh from db, check unexpired but redacted tokens, put in cache
# when redacting token, add to cache
# expire from cache when token would otherwise expire
def get_verified_token_data(
    token: str, claim: str, data_model: Type[PydanticModel]
) -> TokenData:
    token_data = verify_token(token=token, claim=claim, data_model=data_model)
    if not token_data:
        raise InvalidTokenException("Invalid token")
    return token_data


def verify_token(
    token: str, claim: str, data_model: Type[PydanticModel]
) -> Union[TokenData, bool]:
    token_data = False
    try:
        core_config = get_core_config()
        decoded_jwt = jwt.decode(
            token, core_config.secret_key.get_secret_value(), algorithms=[ALGORITHM]
        )
        if decoded_jwt.get("claim", None) != claim:
            raise InvalidTokenError("Token claim didn't match expected claim")

        decoded_jwt["data"] = data_model(**decoded_jwt["data"])

        token_data = TokenData(**decoded_jwt)
    except InvalidTokenError as e:
        print(e)
    return token_data


async def generate_token(
    token_type: str, expire_min: float, username: str, data: Any
) -> AccessToken:
    date_created = get_utc_now()
    date_expires = date_created + timedelta(minutes=expire_min)
    token_db = await save_user_token(
        token_type=token_type,
        username=username,
        date_created=date_created,
        date_expires=date_expires,
    )

    token_data = TokenData(
        metadata=token_db, data=data, sub=username, claim=token_type, exp=date_expires
    )

    token_data_dict = token_data.dict()
    convert_datetime_to_str(data=token_data_dict, skip=["exp", "nbf", "iat"])

    core_config = get_core_config()
    encoded_jwt = jwt.encode(
        token_data_dict, core_config.secret_key.get_secret_value(), algorithm=ALGORITHM
    )
    return AccessToken(access_token=encoded_jwt)


async def save_user_token(
    token_type: str, username: str, date_created: datetime, date_expires: datetime
) -> TokenDb:
    token_db = TokenDb(
        token_id=str(uuid4()),
        token_type=token_type,
        username=username,
        date_created=date_created,
        date_expires=date_expires,
    )
    db_context = db_service.get_db_context()
    return await create_token(db_context=db_context, token_db=token_db)


async def redact_user_token(token_db: TokenDb) -> TokenDb:
    db_context = db_service.get_db_context()
    token_update_db = TokenUpdateDb(date_redacted=get_utc_now())
    return await update_token(
        db_context=db_context, token_db=token_db, token_update_db=token_update_db
    )


async def redact_user_tokens(username: str) -> List[TokenDb]:
    db_context = db_service.get_db_context()
    tokens = await get_valid_tokens_for_user(db_context=db_context, username=username)
    redacted = []
    for token in tokens:
        redacted_token = await redact_user_token(token_db=token)
        redacted.append(redacted_token)
    return redacted
