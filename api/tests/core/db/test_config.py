import os

import pytest

from app.core.db import config as uut
from app.core.db.model import DbConfig


@pytest.fixture
def db_config_env(db_config_dict):
    env = {}
    env["db_port"] = str(db_config_dict["db_port"])
    db_config_dict.pop("db_port")
    for key in db_config_dict:
        env[key] = db_config_dict[key] + "_env"
    return env


@pytest.fixture
def env_setup(db_config_env):
    env_setup = {}
    for key in db_config_env:
        env_setup[key.upper()] = db_config_env[key]

    original_env = dict(os.environ)
    os.environ.update(env_setup)

    yield db_config_env

    os.environ.clear()
    os.environ.update(original_env)


def test_get_db_config_default(db_config):
    expected = db_config
    actual = uut.get_db_config()
    assert actual == expected


def test_get_db_config_env(env_setup):
    expected = DbConfig(**env_setup)
    actual = uut.get_db_config()
    assert actual == expected
