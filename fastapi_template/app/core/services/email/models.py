from pydantic import BaseModel


class EmailConfig(BaseModel):
    email_enabled: bool = False
    from_email: str = "changethis"
    from_name: str = "FastAPI Template"
    email_templates_dir: str = "/app/ui/email_templates/build"
    smtp_host: str = "changethis"
    smpt_port: int = 587
    smpt_tls: bool = True
    smpt_user: str = "changethis"
    smpt_password: str = "changethis"
    email_reset_token_expire_min: float = 30.0
