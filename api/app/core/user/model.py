from datetime import datetime
from typing import List, Optional

from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, SecretStr, constr, validator

from app.core.config import get_config

config = get_config()

USER_ROLE = "USER"
USER_CACHE_PREFIX = "USER"


def min_length_password(cls, value) -> SecretStr:
    del cls
    if len(value.get_secret_value()) < config.password_min_length:
        raise ValueError(
            f"password needs to be at least {config.password_min_length} characters"
        )

    return value


def matching_password(cls, value, values) -> SecretStr:
    del cls
    if (
        not "password_match" in values
        or not values["password_match"]
        or value.get_secret_value() != values["password_match"].get_secret_value()
    ):
        raise ValueError(f"passwords don't match")

    return value


class User(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    verified_email: EmailStr = None
    roles: List[str]
    disabled: bool
    date_created: datetime
    date_modified: datetime = None
    last_login: datetime = None


class UserCreate(BaseModel):
    username: constr(min_length=config.username_min_length)
    first_name: str
    last_name: str
    email: EmailStr
    password_match: SecretStr
    password: SecretStr

    _min_length_password = validator("password", allow_reuse=True)(min_length_password)
    _matching_password = validator("password", allow_reuse=True)(matching_password)


class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    password_match: Optional[SecretStr]
    password: Optional[SecretStr]

    _min_length_password = validator("password", allow_reuse=True)(min_length_password)
    _matching_password = validator("password", allow_reuse=True)(matching_password)


class UserDb(Document):
    username: Indexed(str, unique=True)
    first_name: str
    last_name: str
    email: Indexed(EmailStr, unique=True)
    verified_email: EmailStr = None
    roles: List[str] = []
    disabled: bool = False
    date_created: datetime
    date_modified: datetime = None
    last_login: datetime = None
    password_hash: str
