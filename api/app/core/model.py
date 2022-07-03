from typing import TypeVar

from pydantic import BaseModel, SecretStr

PydanticModel = TypeVar("PydanticModel", bound=BaseModel)


class CoreConfig(BaseModel):
    username_min_length: int
    password_min_length: int
    project_name: str
    templates_dir: str
    login_token_expire_min: float
    verify_token_expire_min: float
    refresh_token_expire_min: float
    secret_key: SecretStr
    token_path: str
    refresh_path: str
    login_path: str
    forgot_password_path: str
    forgot_username_path: str
    reset_path: str
    user_path: str
    verify_path: str
    base_url: str
    current_api: str
    api_v1: str

    def get_current_api(self) -> str:
        return getattr(self, self.current_api.lower())
