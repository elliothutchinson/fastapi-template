from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, SecretStr, constr, validator

from app.core.config import get_core_config

USER_DOC_TYPE = "user"

core_config = get_core_config()


def min_length_password(cls, value):
    if len(value.get_secret_value()) < core_config.password_min_length:
        raise ValueError(
            f"password needs to be at least {core_config.password_min_length} characters"
        )
    return value


def matching_password(cls, value, values):
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
    verified: bool
    date_created: datetime
    date_modified: datetime = None
    last_login: datetime = None


class UserCreate(BaseModel):
    username: constr(min_length=core_config.username_min_length)
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


class UserUpdatePrivate(BaseModel):
    verified_email: Optional[EmailStr]
    roles: Optional[List[str]]
    disabled: Optional[bool]
    verified: Optional[bool]
    date_modified: Optional[datetime]
    last_login: Optional[datetime]


class UserDb(BaseModel):
    type: str = USER_DOC_TYPE
    username: constr(min_length=core_config.username_min_length)
    first_name: str
    last_name: str
    email: EmailStr
    verified_email: EmailStr = None
    roles: List[str] = []
    disabled: bool = False
    verified: bool = False
    date_created: datetime
    date_modified: datetime = None
    last_login: datetime = None
    password_hash: str


class UserUpdateDb(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    verified_email: Optional[EmailStr]
    roles: Optional[List[str]]
    disabled: Optional[bool]
    verified: Optional[bool]
    date_modified: Optional[datetime]
    last_login: Optional[datetime]
    password_hash: Optional[str]
