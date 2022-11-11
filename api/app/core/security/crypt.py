from passlib.context import CryptContext
from pydantic import SecretStr

context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(password: SecretStr, password_hash: str) -> bool:

    return context.verify(password.get_secret_value(), password_hash)


def hash_password(password: SecretStr) -> str:

    return context.hash(password.get_secret_value())
