from app.core import util

from .model import EmailConfig

def get_email_config():
    defaults = {
        "email_enabled": False,
        "from_email": "support@example.com",
        "from_name": "API Template",
        "email_templates_dir": "/app/ui/email_templates/build",
        "smtp_host": "changethis",
        "smtp_port": 587,
        "smtp_tls": True,
        "smtp_user": "changethis",
        "smtp_password": "password",
        "email_reset_token_expire_min": 30.0,
    }
    email_config = EmailConfig(**defaults)
    util.populate_from_env_var(email_config)
    return email_config
