import os

from tests.util import convert_to_env_vars, create_config_dict

env = convert_to_env_vars(create_config_dict())
os.environ.update(env)
