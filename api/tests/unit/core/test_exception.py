from unittest.mock import Mock

import pytest
from fastapi.exceptions import HTTPException
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


def test__exception_mapping():
    expected = {
        uut.DataConflictException: 409,
        uut.ResourceNotFoundException: 404,
        uut.UserDisabedException: 403,
        uut.InvalidCredentialException: 401,
        uut.InvalidTokenException: 401,
    }

    actual = uut._exception_mapping()  # pylint: disable=protected-access

    assert actual == expected


async def test__handler_factory():
    actual_handler = uut._handler_factory(404)  # pylint: disable=protected-access

    actual_response = await actual_handler(
        Mock(), uut.ResourceNotFoundException("test exception")
    )

    assert isinstance(actual_response, JSONResponse)


def test__http_exception_handler():
    actual = uut._http_exception_handler(  # pylint: disable=protected-access
        Mock(), HTTPException(status_code=500, detail="test exception")
    )

    assert isinstance(actual, JSONResponse)


def test_register_exceptions():
    expected = 6

    mock_app = Mock(exception_handler=Mock())

    uut.register_exceptions(mock_app)
    actual = mock_app.exception_handler.call_count

    assert actual == expected
