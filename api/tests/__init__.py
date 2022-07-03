import os

from pydantic import SecretStr

from tests.mock import create_core_config, create_db_config_dict

core_config_dict = create_core_config().dict()


env = {}
for key in core_config_dict:
    value = core_config_dict[key]
    if type(value) is SecretStr:
        env[key.upper()] = value.get_secret_value()
    else:
        env[key.upper()] = str(value)

for key in create_db_config_dict():
    value = create_db_config_dict()[key]
    env[key.upper()] = str(value)

os.environ.update(env)
