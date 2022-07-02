from pydantic import BaseModel, EmailStr, SecretStr, validator

from app.core.user.model import matching_password, min_length_password


class ForgottenPassword(BaseModel):
    username: str


class ForgottenUsername(BaseModel):
    email: EmailStr


class ResetPasswordToken(BaseModel):
    token: str
    password_match: SecretStr
    password: SecretStr

    _min_length_password = validator("password", allow_reuse=True)(min_length_password)
    _matching_password = validator("password", allow_reuse=True)(matching_password)
