from pydantic import BaseModel, EmailStr
from app.core.user.model import min_length_password, matching_password

from pydantic import BaseModel, EmailStr, SecretStr, constr, validator

class ForgottenPassword(BaseModel):
    username: str


class ForgottenUsername(BaseModel):
    email: EmailStr


class PasswordResetToken(BaseModel):
    token: str
    password_match: SecretStr
    password: SecretStr

    _min_length_password = validator("password", allow_reuse=True)(min_length_password)
    _matching_password = validator("password", allow_reuse=True)(matching_password)

