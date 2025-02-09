"""Tests for the error classes."""
import pytest
from dialogllm.utils.errors import (
    DialogLLMError,
    ConfigurationError,
    LLMClientError,
    QueueError,
    StateError,
)

def test_dialogllm_error():
    """Test DialogLLMError base class."""
    error_msg = "Test error"
    with pytest.raises(DialogLLMError) as exc_info:
        raise DialogLLMError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, Exception)

def test_configuration_error():
    """Test ConfigurationError class."""
    error_msg = "Invalid configuration"
    with pytest.raises(ConfigurationError) as exc_info:
        raise ConfigurationError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, DialogLLMError)
    assert isinstance(exc_info.value, Exception)

def test_llm_client_error():
    """Test LLMClientError class."""
    error_msg = "LLM client failed"
    with pytest.raises(LLMClientError) as exc_info:
        raise LLMClientError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, DialogLLMError)
    assert isinstance(exc_info.value, Exception)

def test_queue_error():
    """Test QueueError class."""
    error_msg = "Queue operation failed"
    with pytest.raises(QueueError) as exc_info:
        raise QueueError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, DialogLLMError)
    assert isinstance(exc_info.value, Exception)

def test_state_error():
    """Test StateError class."""
    error_msg = "Invalid state"
    with pytest.raises(StateError) as exc_info:
        raise StateError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, DialogLLMError)
    assert isinstance(exc_info.value, Exception)

def test_error_hierarchy():
    """Test error class hierarchy relationships."""
    # Create instances of each error type
    errors = [
        DialogLLMError("base"),
        ConfigurationError("config"),
        LLMClientError("llm"),
        QueueError("queue"),
        StateError("state")
    ]
    
    # Verify all errors are instances of DialogLLMError
    for error in errors:
        assert isinstance(error, DialogLLMError)
        assert isinstance(error, Exception)

def test_error_with_complex_message():
    """Test errors with complex messages including formatting."""
    # Test with multiline message
    multiline_msg = """
    Error occurred:
    - Reason: Test failure
    - Code: 500
    """
    error = DialogLLMError(multiline_msg)
    assert str(error) == multiline_msg
    
    # Test with formatted message
    formatted_msg = f"Error code: {500}, message: {'test'}"
    error = DialogLLMError(formatted_msg)
    assert str(error) == formatted_msg
