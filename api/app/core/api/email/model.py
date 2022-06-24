from typing import Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, SecretStr


EMAIL_DOC_TYPE = "email"


class EmailConfig(BaseModel):
    email_enabled: bool
    from_email: EmailStr
    from_name: str
    email_templates_dir: str
    smtp_host: str
    smtp_port: int
    smtp_tls: bool
    smtp_user: str
    smtp_password: SecretStr
    email_reset_token_expire_min: float


class EmailDb(BaseModel):
    type: str = EMAIL_DOC_TYPE
    email_id: str
    username: str
    from_email: EmailStr
    to_email: EmailStr
    subject: str
    html_template: str
    template_data: Any
    date_created: datetime