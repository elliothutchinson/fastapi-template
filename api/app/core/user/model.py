from datetime import datetime
from typing import Optional

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
        "password_match" not in values
        or not values["password_match"]
        or value.get_secret_value() != values["password_match"].get_secret_value()
    ):
        raise ValueError("passwords don't match")

    return value


class UserPublic(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    verified_email: EmailStr | None = None
    roles: list[str]
    disabled: bool
    date_created: datetime
    date_modified: datetime | None = None
    last_login: datetime | None = None


class UserPrivate(UserPublic):
    password_hash: str


class UserCreate(BaseModel):
    username: constr(min_length=config.username_min_length)
    first_name: str
    last_name: str
    email: EmailStr
    password_match: SecretStr
    password: SecretStr

    _min_length_password = validator("password", allow_reuse=True)(min_length_password)
    _matching_password = validator("password", allow_reuse=True)(matching_password)

    class Config:
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value(),
        }


class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    password_match: Optional[SecretStr]
    password: Optional[SecretStr]

    _min_length_password = validator("password", allow_reuse=True)(min_length_password)
    _matching_password = validator("password", allow_reuse=True)(matching_password)

    class Config:
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value(),
        }


class UserUpdatePrivate(BaseModel):
    verified_email: Optional[EmailStr]
    roles: Optional[list[str]]
    disabled: Optional[bool]
    last_login: Optional[datetime]
