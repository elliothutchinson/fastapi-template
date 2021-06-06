import logging

from passlib.context import CryptContext
from pydantic import SecretStr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(password: SecretStr, hashed_password: str):
    logger.debug("verify_password()")
    return pwd_context.verify(password.get_secret_value(), hashed_password)


def get_password_hash(password: SecretStr):
    logger.debug("get_password_hash()")
    return pwd_context.hash(password.get_secret_value())
