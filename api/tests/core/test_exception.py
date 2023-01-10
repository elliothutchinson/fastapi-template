from unittest.mock import Mock

import pytest
from fastapi.responses import JSONResponse

from app.core import exception as uut


def test_ResourceNotFoundException():

    with pytest.raises(uut.ResourceNotFoundException, match="test exception"):
        raise uut.ResourceNotFoundException("test exception")


def test_DataConflictException():

    with pytest.raises(uut.DataConflictException, match="test exception"):
        raise uut.DataConflictException("test exception")


def test_InvalidTokenException():

    with pytest.raises(uut.InvalidTokenException, match="test exception"):
        raise uut.InvalidTokenException("test exception")


def test_InvalidCredentialException():

    with pytest.raises(uut.InvalidCredentialException, match="test exception"):
        raise uut.InvalidCredentialException("test exception")


def test_UserDisabedException():

    with pytest.raises(uut.UserDisabedException, match="test exception"):
        raise uut.UserDisabedException("test exception")


def test_exception_mappying():
    expected = {
        uut.DataConflictException: 409,
        uut.ResourceNotFoundException: 404,
        uut.UserDisabedException: 403,
        uut.InvalidCredentialException: 401,
        uut.InvalidTokenException: 401,
    }

    actual = uut.exception_mapping()

    assert actual == expected


async def test_handler_factory():
    actual_handler = uut.handler_factory(404)

    actual_response = await actual_handler(
        Mock(), uut.ResourceNotFoundException("test exception")
    )

    assert isinstance(actual_response, JSONResponse)


def test_register_exceptions():
    mock_app = Mock(exception_handler=Mock())

    uut.register_exceptions(mock_app)

    mock_app.exception_handler.assert_called()
