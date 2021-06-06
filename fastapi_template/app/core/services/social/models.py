from pydantic import BaseModel, constr

from app.core.config import core_config


class SocialToken(BaseModel):
    social_token: str


class UserCreateSocial(BaseModel):
    username: constr(min_length=core_config.username_min_length)


class SocialConfig(BaseModel):
    social_enabled: bool = False
    social_path: str = "/social"
    social_register_path: str = "/register"
    swap_token_path: str = "/swaptoken"
    google_client_id: str = "changethis"
    google_client_secret: str = "changethis"
    google_client_secret_json: str = "google_client_secret_json"
