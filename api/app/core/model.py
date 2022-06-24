from typing import TypeVar

from pydantic import BaseModel, SecretStr

PydanticModel = TypeVar("PydanticModel", bound=BaseModel)


class CoreConfig(BaseModel):
    username_min_length: int
    password_min_length: int
    project_name: str
    login_token_expire_min: float
    secret_key: SecretStr
    token_path: str
    login_path: str
    forgot_path: str
    reset_path: str
    user_path: str
    current_api: str
    api_v1: str

    def get_current_api(self):
        return getattr(self, self.current_api.lower())