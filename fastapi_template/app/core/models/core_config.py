from pydantic import BaseModel


class CoreConfig(BaseModel):
    project_name: str = "FastAPI Template"
    base_url: str = "http://localhost"
    current_api: str = "API_V1"
    api_v1: str = "/api/v1"
    templates_dir: str = "ui/templates"
    secret_key: str = "changethis"
    verify_token_expire_min: float = 20160.0
    access_token_expire_min: float = 1440.0
    username_min_length: int = 1
    password_min_length: int = 4
    token_type: str = "Bearer"
    login_path: str = "/login"
    token_path: str = "/token"
    users_path: str = "/users"
    forgot_path: str = "/forgot"
    reset_path: str = "/reset"
    reset_success_path: str = "/reset_success"
    verify_path: str = "/verify"
    debug: bool = False

    def get_current_api(self):
        return getattr(self, self.current_api.lower())
