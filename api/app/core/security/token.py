from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

from app.core.config import get_config
from app.core.db import cache
from app.core.exception import InvalidTokenException
from app.core.logging import get_logger
from app.core.util import (
    PydanticModel,
    convert_datetime_to_str,
    convert_timestamp_to_ttl,
)

config = get_config()

logger = get_logger(__name__)

REVOKED_TOKEN_CACHE_PREFIX = "REVOKED_TOKEN"


class RevokedToken(BaseModel):
    token_id: str
    claim: str
    exp: int
    sub: str
    data: dict | None = None
    revoke_reason: str


def generate_token(
    claim: str, expire_min: float, sub: str, data: PydanticModel = None
) -> tuple[str, datetime]:
    date_created = datetime.now(timezone.utc)
    date_expires = date_created + timedelta(minutes=expire_min)

    data_dict = None
    if data:
        data_dict = data.dict()
        convert_datetime_to_str(data_dict)

    jwt_data = {
        "token_id": str(uuid4()),
        "claim": claim,
        "exp": date_expires,
        "sub": sub,
        "data": data_dict,
    }

    encoded_jwt = jwt.encode(
        jwt_data, config.jwt_secret_key.get_secret_value(), config.jwt_algorithm
    )

    return encoded_jwt, date_expires


async def validate_token(claim: str, token: str) -> dict:
    jwt_data = None

    try:
        jwt_data = jwt.decode(
            token,
            config.jwt_secret_key.get_secret_value(),
            algorithms=[config.jwt_algorithm],
        )

        decoded_claim = jwt_data.get("claim", None)
        if decoded_claim != claim:
            raise InvalidTokenException(
                f"Token claim '{decoded_claim}' didn't match expected claim '{claim}'"
            )

    except InvalidTokenError as ite:
        logger.error(ite)
        raise InvalidTokenException(f"Invalid token with claim '{claim}'") from ite

    token_id = jwt_data["token_id"]

    if await _is_token_revoked(token_id):
        raise InvalidTokenException(
            f"Token with token_id '{token_id}' has been revoked"
        )

    return jwt_data


async def revoke_token(claim: str, token: str, revoke_reason: str) -> bool:
    revoked = True

    try:
        jwt_data = await validate_token(claim=claim, token=token)
        revoked_token = RevokedToken(
            **jwt_data,
            revoke_reason=revoke_reason,
        )
        await cache.put(
            prefix=REVOKED_TOKEN_CACHE_PREFIX,
            key=revoked_token.token_id,
            doc=revoked_token,
            ttl=convert_timestamp_to_ttl(revoked_token.exp),
        )
    except InvalidTokenException:
        revoked = False

    return revoked


async def _is_token_revoked(token_id: str) -> bool:
    revoked_token = await cache.fetch(
        prefix=REVOKED_TOKEN_CACHE_PREFIX, key=token_id, doc_model=RevokedToken
    )

    return revoked_token is not None
