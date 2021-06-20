from passlib.context import CryptContext
from pydantic import SecretStr

from app.core import logger as trace
from app.core.logger import get_logger

logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@trace.debug(logger)
def verify_password(password: SecretStr, hashed_password: str):
    return pwd_context.verify(password.get_secret_value(), hashed_password)


@trace.debug(logger)
def get_password_hash(password: SecretStr):
    return pwd_context.hash(password.get_secret_value())
