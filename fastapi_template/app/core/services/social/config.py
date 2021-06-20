from app.core.logger import get_logger
from app.core.utils import populate_from_env_var

from .models import SocialConfig

logger = get_logger(__name__)

social_config = SocialConfig()
populate_from_env_var(social_config)
