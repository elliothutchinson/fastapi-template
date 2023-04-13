import os

from tests.factories.config_factory import ConfigFactory
from tests.unit.util import convert_to_env_vars

config = ConfigFactory.build()
env = convert_to_env_vars(config.dict())
os.environ.update(env)
