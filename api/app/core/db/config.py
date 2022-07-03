from app.core import util

from .model import DbConfig


def get_db_config() -> DbConfig:
    env = util.populate_from_env_var(doc_model=DbConfig)
    db_config = DbConfig(**env)
    return db_config
