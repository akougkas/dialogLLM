"""Tests for the logging system."""
import json
import logging
import os
import shutil
import tempfile
from pathlib import Path
from io import StringIO
from logging.handlers import RotatingFileHandler

import pytest
from unittest.mock import patch, MagicMock, call

from dialogllm.utils.logger import Logger, JsonFormatter, LOG_DIR, LOG_FILE

@pytest.fixture(autouse=True)
def reset_logger():
    """Reset logger instance before each test."""
    # Store original state
    orig_log_dir = os.getenv('LOG_DIR', LOG_DIR)
    
    # Reset logger instance
    if Logger._instance and hasattr(Logger._instance, 'logger'):
        for handler in Logger._instance.logger.handlers:
            handler.close()
        Logger._instance.logger.handlers = []
    Logger._instance = None
    Logger._initialized = False
    
    yield
    
    # Restore original state
    os.environ['LOG_DIR'] = orig_log_dir

@pytest.fixture
def temp_log_dir():
    """Create a temporary log directory for testing."""
    temp_dir = tempfile.mkdtemp()
    os.environ['LOG_DIR'] = temp_dir
    yield temp_dir
    try:
        shutil.rmtree(temp_dir)
    except FileNotFoundError:
        pass  # Directory already removed

@pytest.fixture
def logger_instance(temp_log_dir):
    """Create a fresh logger instance for each test."""
    Logger._instance = None
    Logger._initialized = False
    return Logger()

def test_logger_singleton():
    """Test that Logger maintains singleton pattern."""
    logger1 = Logger()
    logger2 = Logger()
    assert logger1 is logger2

def test_json_formatter():
    """Test that JsonFormatter correctly formats log records."""
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    formatted = formatter.format(record)
    log_dict = json.loads(formatted)
    
    assert log_dict["level"] == "INFO"
    assert log_dict["name"] == "test"
    assert log_dict["message"] == "Test message"
    assert "timestamp" in log_dict
    assert "thread" in log_dict
    assert "process" in log_dict

def test_logger_levels(logger_instance):
    """Test that logger correctly handles different log levels."""
    stream = StringIO()
    with patch('sys.stdout', stream):
        # Replace the existing handlers with our test handler
        logger_instance.logger.handlers = []
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JsonFormatter())
        logger_instance.logger.addHandler(handler)
        
        logger_instance.debug("Debug message")
        logger_instance.info("Info message")
        logger_instance.warning("Warning message")
        logger_instance.error("Error message")
        
        output = stream.getvalue()
        log_entries = [json.loads(line) for line in output.strip().split('\n') if line]
        
        assert len(log_entries) == 4
        assert log_entries[0]["level"] == "DEBUG"
        assert log_entries[1]["level"] == "INFO"
        assert log_entries[2]["level"] == "WARNING"
        assert log_entries[3]["level"] == "ERROR"

def test_logger_extra_fields(logger_instance):
    """Test that logger correctly handles extra fields."""
    stream = StringIO()
    with patch('sys.stdout', stream):
        # Replace the existing handlers with our test handler
        logger_instance.logger.handlers = []
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JsonFormatter())
        logger_instance.logger.addHandler(handler)
        
        extra = {"user_id": "123", "action": "test"}
        logger_instance.info("Test with extra", extra=extra)
        
        output = stream.getvalue()
        log_dict = json.loads(output.strip())
        
        assert log_dict["user_id"] == "123"
        assert log_dict["action"] == "test"

def test_logger_exception_handling(logger_instance):
    """Test that logger correctly handles exceptions."""
    stream = StringIO()
    with patch('sys.stdout', stream):
        # Replace the existing handlers with our test handler
        logger_instance.logger.handlers = []
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JsonFormatter())
        logger_instance.logger.addHandler(handler)
        
        try:
            raise ValueError("Test error")
        except ValueError:
            logger_instance.exception("Error occurred")
        
        output = stream.getvalue()
        log_dict = json.loads(output.strip())
        
        assert "exc_info" in log_dict
        assert "ValueError: Test error" in log_dict["exc_info"]

def test_file_rotation(temp_log_dir):
    """Test log file rotation."""
    logger = Logger()
    
    # Generate a message that will be ~100KB when formatted as JSON
    msg_data = {
        "data": "x" * 100 * 1024,  # 100KB of raw data
        "metadata": {
            "timestamp": "2025-02-09T03:11:15-06:00",
            "level": "INFO",
            "context": "test"
        }
    }
    
    # Write enough logs to trigger rotation (>512KB)
    for i in range(10):  # Should write ~1MB total with JSON overhead
        logger.info(f"Large message {i}", extra=msg_data)
        # Force flush after each write
        for handler in logger.logger.handlers:
            if isinstance(handler, RotatingFileHandler):
                handler.flush()
    
    # Verify log files exist and have content
    log_files = sorted(Path(temp_log_dir).glob("*.log*"))
    assert len(log_files) > 1, f"Expected multiple log files due to rotation, found {len(log_files)}: {[f.name for f in log_files]}"
    
    # Verify each log file has content
    for log_file in log_files:
        assert log_file.stat().st_size > 0, f"Log file {log_file.name} is empty"

def test_log_directory_creation(temp_log_dir):
    """Test automatic creation of log directory."""
    # Remove the temp directory created by fixture
    shutil.rmtree(temp_log_dir)
    assert not os.path.exists(temp_log_dir)
    
    # Creating logger should create the directory
    logger = Logger()
    assert os.path.exists(temp_log_dir)

@pytest.fixture(autouse=True)
def cleanup_logger():
    """Clean up logger after each test."""
    yield
    if Logger._instance and hasattr(Logger._instance, 'logger'):
        Logger._instance.logger.handlers = []
