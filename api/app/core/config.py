from .model import CoreConfig
from .util import populate_from_env_var


def get_core_config() -> CoreConfig:
    env = populate_from_env_var(doc_model=CoreConfig)
    core_config = CoreConfig(**env)
    return core_config
