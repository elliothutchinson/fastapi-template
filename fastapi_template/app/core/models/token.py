from pydantic import BaseModel, SecretStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


class Credential(BaseModel):
    password: SecretStr


class ResetPasswordToken(BaseModel):
    token: str
    password: SecretStr
