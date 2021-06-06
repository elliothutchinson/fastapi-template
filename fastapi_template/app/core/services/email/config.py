import logging

from app.core.utils import populate_from_env_var

from .models import EmailConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

email_config = EmailConfig()
populate_from_env_var(email_config)
