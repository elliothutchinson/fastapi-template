import os

import pytest
from pydantic import BaseModel


@pytest.fixture
def some_class_dict():
    return {
        "bool_attr": "False",
        "bool_attr_1": "1",
        "bool_attr_on": "on",
        "bool_attr_t": "t",
        "bool_attr_true": "true",
        "bool_attr_y": "y",
        "bool_attr_yes": "yes",
        "int_attr": "456",
        "float_attr": "3.14",
        "str_attr": "test",
    }


@pytest.fixture
def env_setup(some_class_dict):
    env_setup = {}
    for key in some_class_dict:
        env_setup[key.upper()] = some_class_dict[key]

    original_env = dict(os.environ)
    os.environ.update(env_setup)

    yield

    os.environ.clear()
    os.environ.update(original_env)


class SomeClass(BaseModel):
    bool_attr: bool = True
    bool_attr_1: bool = False
    bool_attr_on: bool = False
    bool_attr_t: bool = False
    bool_attr_true: bool = False
    bool_attr_y: bool = False
    bool_attr_yes: bool = False
    int_attr: int = 123
    float_attr: float = 3.5
    str_attr: str = "asdf"


def test_get_utc_now():
    pass


# def test_populate_from_env_var_default():
#     expected = SomeClass()
#     actual = SomeClass()
#     uut.populate_from_env_var(actual)
#     assert actual == expected


# def test_populate_from_env_var_from_env(env_setup, some_class_dict):
#     expected = SomeClass(**some_class_dict)
#     actual = SomeClass()
#     uut.populate_from_env_var(actual)
#     actual_dict = actual.dict()
#     for key in actual_dict:
#         if key in [
#             "bool_attr_1",
#             "bool_attr_on",
#             "bool_attr_t",
#             "bool_attr_true",
#             "bool_attr_y",
#             "bool_attr_yes",
#         ]:
#             assert actual_dict[key] is True
#     assert actual == expected
