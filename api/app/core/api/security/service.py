from typing import Union

from pydantic import SecretStr

from app.core.db import service as db_service
from app.core.user import crud as user_crud
from app.core.user.model import User

from .crypt import verify_password
from .model import InvalidCredentialException, UserDisabledException


async def get_authenticated_user(username: str, password: SecretStr) -> User:
    user = await authenticate_user(username=username, password=password)
    if not user:
        raise InvalidCredentialException("Invalid credentials provided")
    if user.disabled:
        raise UserDisabledException("User is disabled")
    return user


async def authenticate_user(username: str, password: SecretStr) -> Union[User, bool]:
    user = False
    db_context = db_service.get_db_context()
    user_db = await user_crud.get_user(db_context=db_context, username=username)
    if user_db and verify_password(
        password=password, password_hash=user_db.password_hash
    ):
        user = User(**user_db.dict())
    return user
