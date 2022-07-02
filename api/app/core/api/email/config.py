from app.core import util

from .model import EmailConfig


def get_email_config():
    env = util.populate_from_env_var(doc_model=EmailConfig)
    email_config = EmailConfig(**env)
    return email_config
