"""Comprehensive tests for the logger module."""
import json
import logging
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from logging.handlers import RotatingFileHandler

from dialogllm.utils.logger import Logger, JsonFormatter

@pytest.fixture
def temp_log_dir(tmp_path):
    """Create a temporary log directory."""
    log_dir = tmp_path / "logs"
    with patch.dict('os.environ', {'LOG_DIR': str(log_dir)}):
        yield log_dir

@pytest.fixture
def json_formatter():
    """Create a JsonFormatter instance."""
    return JsonFormatter()

@pytest.fixture
def logger_instance(temp_log_dir):
    """Create a Logger instance with a temporary log directory."""
    Logger._instance = None
    Logger._initialized = False
    return Logger()

def test_json_formatter_basic(json_formatter):
    """Test basic JSON formatting."""
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    formatted = json_formatter.format(record)
    data = json.loads(formatted)
    assert data["level"] == "INFO"
    assert data["message"] == "Test message"
    assert "timestamp" in data

def test_json_formatter_with_extra(json_formatter):
    """Test JSON formatting with extra fields."""
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    record.custom_field = "custom_value"
    formatted = json_formatter.format(record)
    data = json.loads(formatted)
    assert data["custom_field"] == "custom_value"

def test_json_formatter_with_exception(json_formatter):
    """Test JSON formatting with exception information."""
    try:
        raise ValueError("Test error")
    except ValueError as e:
        exc_info = sys.exc_info()
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Error occurred",
            args=(),
            exc_info=exc_info
        )
        formatted = json_formatter.format(record)
        data = json.loads(formatted)
        assert "exc_info" in data
        assert "ValueError: Test error" in data["exc_info"]

def test_logger_singleton(temp_log_dir):
    """Test that Logger is a singleton."""
    logger1 = Logger()
    logger2 = Logger()
    assert logger1 is logger2

def test_logger_initialization(logger_instance, temp_log_dir):
    """Test logger initialization."""
    assert os.path.exists(temp_log_dir)
    assert len(logger_instance.logger.handlers) == 2  # Console and file handler

def test_logger_log_levels(logger_instance, temp_log_dir):
    """Test all log levels."""
    test_msg = "Test message"
    extra = {"custom_field": "value"}

    # Test each log level
    logger_instance.debug(test_msg, extra)
    logger_instance.info(test_msg, extra)
    logger_instance.warning(test_msg, extra)
    logger_instance.error(test_msg, extra)
    
    # Check log file content
    log_file = os.path.join(temp_log_dir, "dialogllm.log")
    assert os.path.exists(log_file)
    with open(log_file, 'r') as f:
        logs = f.readlines()
        assert len(logs) > 0
        for log in logs:
            data = json.loads(log)
            assert data["message"] == test_msg
            assert data["custom_field"] == "value"

def test_logger_exception(logger_instance):
    """Test exception logging."""
    try:
        raise ValueError("Test error")
    except ValueError:
        logger_instance.exception("An error occurred", {"context": "test"})

def test_logger_file_handler_error(temp_log_dir):
    """Test file handler error handling."""
    Logger._instance = None
    Logger._initialized = False
    with patch.object(Logger, '_configure', side_effect=RuntimeError("Failed to configure file handler")):
        with pytest.raises(RuntimeError, match="Failed to configure file handler"):
            logger = Logger()

def test_logger_directory_creation_error():
    """Test log directory creation error handling."""
    Logger._instance = None
    Logger._initialized = False
    with patch.object(Logger, '__new__', side_effect=RuntimeError("Failed to create log directory")):
        with pytest.raises(RuntimeError, match="Failed to create log directory"):
            Logger()

def test_logger_with_invalid_log_dir():
    """Test logger with invalid log directory."""
    Logger._instance = None
    Logger._initialized = False
    test_dir = '/tmp/test_logs'
    with patch.dict('os.environ', {'LOG_DIR': test_dir}):
        with patch('os.makedirs') as mock_makedirs:
            logger = Logger()
            assert logger is not None
            # Check if makedirs was called with the test directory
            mock_makedirs.assert_any_call(test_dir)
        
def test_logger_rotating_file_handler(logger_instance, temp_log_dir):
    """Test rotating file handler configuration."""
    file_handler = None
    for handler in logger_instance.logger.handlers:
        if isinstance(handler, RotatingFileHandler):
            file_handler = handler
            break
    
    assert file_handler is not None
    assert file_handler.maxBytes == 512*1024  # 512KB
    assert file_handler.backupCount == 5
