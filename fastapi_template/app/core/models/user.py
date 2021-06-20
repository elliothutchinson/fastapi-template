from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, SecretStr, constr, validator

from app.core.config import core_config
from app.core.logger import get_logger

USER_DOC_TYPE = "user"

logger = get_logger(__name__)


def min_length_password(cls, v):
    if len(v.get_secret_value()) < core_config.password_min_length:
        raise ValueError(
            f"ensure this value has at least {core_config.password_min_length} characters"
        )
    return v


class UserPublic(BaseModel):
    username: constr(min_length=core_config.username_min_length)
    full_name: str


class UserPrivate(UserPublic):
    email: EmailStr


class UserCreate(UserPrivate):
    password: SecretStr

    # validators
    _min_length_password = validator("password", allow_reuse=True)(min_length_password)


class User(UserPrivate):
    disabled: bool = False
    verified: bool = False
    date_created: datetime
    date_modified: datetime = None
    last_login: datetime = None


class UserUpdate(BaseModel):
    password: Optional[SecretStr]
    email: Optional[EmailStr]
    full_name: Optional[str]

    # validators
    _min_length_password = validator("password", allow_reuse=True)(min_length_password)


class UserUpdatePrivate(BaseModel):
    disabled: Optional[bool]
    verified: Optional[bool]
    last_login: Optional[datetime]


class UserUpdateDb(BaseModel):
    hashed_password: Optional[str]
    email: Optional[EmailStr]
    full_name: Optional[str]
    disabled: Optional[bool]
    verified: Optional[bool]
    date_modified: Optional[datetime]
    last_login: Optional[datetime]


class UserDb(User):
    type: str = USER_DOC_TYPE
    hashed_password: str
