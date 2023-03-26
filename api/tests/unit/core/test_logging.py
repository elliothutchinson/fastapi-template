import logging
from contextvars import ContextVar
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import orjson
import pytest
from freezegun import freeze_time

from app.core import logging as uut


@pytest.fixture
def _context_vars():
    ctx_request_id = ContextVar("request_id", default="n/a")
    reset_request_id = ctx_request_id.set("3dab0896-6d4d-4358-a999-cf0c47776156")

    ctx_request_ip = ContextVar("request_ip", default="n/a")
    reset_request_ip = ctx_request_ip.set("127.0.0.1")

    yield

    ctx_request_id.reset(reset_request_id)
    ctx_request_ip.reset(reset_request_ip)


@pytest.fixture
def log_record():
    return {
        "date": datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc).isoformat(),
        "levelname": "INFO",
        "pathname": "app.py",
        "funcName": "calculate",
        "lineno": "42",
        "msg": "test message",
        "request_ip": "127.0.0.1",
        "request_id": "3dab0896-6d4d-4358-a999-cf0c47776156",
        "thread_name": "threadName - 12345",
        "process": "1234",
        "log_version": "1.0.0",
    }


def test_log_version():
    expected = "1.0.0"

    actual = uut.LOG_VERSION

    assert actual == expected


def test_ContextFilter():
    actual = uut.ContextFilter()

    assert isinstance(actual, logging.Filter)


def test_ContextFilter_from_context(_context_vars):
    context_filter = uut.ContextFilter()

    actual_request_id = context_filter.from_context("request_id", "n/a")
    actual_request_ip = context_filter.from_context("request_ip", "n/a")
    actual_not_set = context_filter.from_context("not_set", "n/a")

    assert actual_request_id == "3dab0896-6d4d-4358-a999-cf0c47776156"
    assert actual_request_ip == "127.0.0.1"
    assert actual_not_set == "n/a"


@freeze_time("2020-01-01 00:00:00")
def test_ContextFilter_filter_msg_string(_context_vars, log_record):
    mock_record = Mock(**log_record, threadName="threadName", thread="12345")
    context_filter = uut.ContextFilter()

    expected = orjson.dumps(log_record).decode()

    actual = context_filter.filter(mock_record)

    assert actual is True
    assert mock_record.json == expected


@freeze_time("2020-01-01 00:00:00")
def test_ContextFilter_filter_msg_string_not_supported(_context_vars, log_record):
    mock_record = Mock(**log_record, threadName="threadName", thread="12345")
    mock_record.configure_mock(msg=Mock(__str__=lambda: 1 / 0))

    log_record["msg"] = "Incompatible log message"

    context_filter = uut.ContextFilter()

    expected = orjson.dumps(log_record).decode()

    actual = context_filter.filter(mock_record)

    assert actual is True
    assert mock_record.json == expected


def test__log_format_msg_string(log_record):
    expected_str = orjson.dumps(log_record).decode()

    actual_format = uut._log_format()  # pylint: disable=protected-access
    actual_str = actual_format % {"json": orjson.dumps(log_record).decode()}
    actual_dict = orjson.loads(actual_str)

    assert actual_str == expected_str
    assert isinstance(actual_dict, dict)


def test__log_format_msg_json(log_record):
    log_record["msg"] = {"message": "test"}

    expected_str = orjson.dumps(log_record).decode()

    actual_format = uut._log_format()  # pylint: disable=protected-access
    actual_str = actual_format % {"json": orjson.dumps(log_record).decode()}
    actual_dict = orjson.loads(actual_str)

    assert actual_str == expected_str
    assert isinstance(actual_dict, dict)


def test_get_logger_not_setup():
    actual = uut.get_logger("test_module")

    assert isinstance(actual, logging.Logger)


@patch(
    "app.core.logging.logging.getLogger",
    Mock(filters=True, handlers=True),
)
def test_get_logger_already_setup():
    actual = uut.get_logger("test_module")

    assert isinstance(actual, Mock)
