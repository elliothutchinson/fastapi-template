from passlib.context import CryptContext
from pydantic import SecretStr

context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(password: SecretStr, password_hash: str):
    return context.verify(password.get_secret_value(), password_hash)


def hash_password(password: SecretStr):
    return context.hash(password.get_secret_value())
