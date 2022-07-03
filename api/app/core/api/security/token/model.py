from datetime import datetime
from typing import Any

from pydantic import BaseModel

TOKEN_DOC_TYPE = "TOKEN"


class AccessToken(BaseModel):
    token_type: str = "Bearer"
    refresh_token: str = None
    access_token: str
    date_expires: datetime


class TokenDb(BaseModel):
    type: str = TOKEN_DOC_TYPE
    token_id: str
    token_type: str
    username: str
    date_created: datetime
    date_expires: datetime
    date_redacted: datetime = None


class TokenUpdateDb(BaseModel):
    date_redacted: datetime


class TokenData(BaseModel):
    metadata: TokenDb
    data: Any
    sub: str
    claim: str
    exp: datetime


class InvalidTokenException(Exception):
    pass
