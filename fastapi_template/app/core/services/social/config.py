import logging

from app.core.utils import populate_from_env_var

from .models import SocialConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

social_config = SocialConfig()
populate_from_env_var(social_config)
