from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest

from app.core.api import middleware as uut


@pytest.fixture
def request_id_str():
    return "d4a9727c-08f5-4fb5-8dfc-265f71c54007"


async def test_RequestIdMiddleware_dispatch_new_request_id(mocker, request_id_str):
    mock_request = Mock()
    mock_request.configure_mock(name="headers")
    mock_request.headers = {}

    mock_response = Mock()
    mock_response.configure_mock(name="headers")
    mock_response.headers = {}

    mock_call_next = AsyncMock(return_value=mock_response)

    mock_context_request_id = Mock()

    mocker.patch(
        "app.core.api.middleware.uuid4", Mock(return_value=UUID(request_id_str))
    )
    mocker.patch("app.core.api.middleware.ctx_request_id", mock_context_request_id)

    actual = await uut.RequestIdMiddleware(Mock()).dispatch(
        mock_request, mock_call_next
    )

    assert actual.headers["request_id"] == request_id_str
    mock_context_request_id.set.assert_called_once_with(request_id_str)


async def test_RequestIdMiddleware_dispatch_existing_request_id(mocker, request_id_str):
    mock_request = Mock()
    mock_request.configure_mock(name="headers")
    mock_request.headers = {"request_id": request_id_str}

    mock_response = Mock()
    mock_response.configure_mock(name="headers")
    mock_response.headers = {}

    mock_call_next = AsyncMock(return_value=mock_response)

    mock_context_request_id = Mock()

    mocker.patch("app.core.api.middleware.ctx_request_id", mock_context_request_id)

    actual = await uut.RequestIdMiddleware(Mock()).dispatch(
        mock_request, mock_call_next
    )

    assert actual.headers["request_id"] == request_id_str
    mock_context_request_id.set.assert_called_once_with(request_id_str)


async def test_RequestIdMiddleware_dispatch_request_ip(mocker):
    mock_client = Mock()
    mock_client.configure_mock(name="host")
    mock_client.host = "127.0.0.1"

    mock_request = Mock()
    mock_request.configure_mock(name="client")
    mock_request.client = mock_client

    mock_context_request_ip = Mock()

    mocker.patch("app.core.api.middleware.ctx_request_ip", mock_context_request_ip)

    await uut.RequestIdMiddleware(Mock()).dispatch(mock_request, AsyncMock())

    mock_context_request_ip.set.assert_called_once_with("127.0.0.1")
