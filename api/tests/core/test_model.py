from pydantic import BaseModel

from app.core import model as uut


def test_PydanticModel():
    actual = uut.PydanticModel
    assert actual.__bound__ == BaseModel


def test_CoreConfig():
    pass
