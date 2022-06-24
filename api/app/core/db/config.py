from app.core import util

from .model import DbConfig


def get_db_config() -> DbConfig:
    defaults = {
        "db_host": "db",
        "db_port": 5432,
        "db_root_user": "root",
        "db_root_password": "password",
        "db_root_database": "template1",
        "db_app_user": "app",
        "db_app_password": "password",
        "db_app_database": "api",
        "db_table": "docs",
        "db_test_table": "test_docs",
    }
    db_config = DbConfig(**defaults)
    util.populate_from_env_var(db_config)
    return db_config
