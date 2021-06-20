from app.core.logger import get_logger
from app.core.utils import populate_from_env_var
from app.ext.models.ext_config import ExtConfig

logger = get_logger(__name__)

ext_config = ExtConfig()
populate_from_env_var(ext_config)
