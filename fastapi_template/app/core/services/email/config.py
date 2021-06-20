from app.core.logger import get_logger
from app.core.utils import populate_from_env_var

from .models import EmailConfig

logger = get_logger(__name__)

email_config = EmailConfig()
populate_from_env_var(email_config)
