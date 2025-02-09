"""Tests for the state manager utility."""
import pytest
from dialogllm.utils.state_manager import StateManager

def test_state_manager_initialization():
    """Test state manager initialization."""
    manager = StateManager()
    assert isinstance(manager._state, dict)
    assert len(manager._state) == 0

def test_get_nonexistent_state():
    """Test getting a state key that doesn't exist."""
    manager = StateManager()
    assert manager.get_state("nonexistent") is None

def test_set_and_get_state():
    """Test setting and getting state values."""
    manager = StateManager()
    
    # Test with different types of values
    test_cases = [
        ("string_key", "test_value"),
        ("int_key", 42),
        ("list_key", [1, 2, 3]),
        ("dict_key", {"a": 1, "b": 2}),
        ("bool_key", True),
        ("none_key", None)
    ]
    
    # Set all test values
    for key, value in test_cases:
        manager.set_state(key, value)
    
    # Verify all values were stored correctly
    for key, expected_value in test_cases:
        assert manager.get_state(key) == expected_value

def test_update_existing_state():
    """Test updating an existing state value."""
    manager = StateManager()
    
    # Set initial value
    manager.set_state("test_key", "initial_value")
    assert manager.get_state("test_key") == "initial_value"
    
    # Update value
    manager.set_state("test_key", "updated_value")
    assert manager.get_state("test_key") == "updated_value"

def test_clear_existing_state():
    """Test clearing an existing state value."""
    manager = StateManager()
    
    # Set and verify initial value
    manager.set_state("test_key", "test_value")
    assert manager.get_state("test_key") == "test_value"
    
    # Clear and verify it's gone
    manager.clear_state("test_key")
    assert manager.get_state("test_key") is None

def test_clear_nonexistent_state():
    """Test clearing a nonexistent state key."""
    manager = StateManager()
    
    # Should not raise an error
    manager.clear_state("nonexistent")
    assert manager.get_state("nonexistent") is None

def test_multiple_instances():
    """Test that different instances maintain separate state."""
    manager1 = StateManager()
    manager2 = StateManager()
    
    # Set state in first instance
    manager1.set_state("key", "value1")
    assert manager1.get_state("key") == "value1"
    assert manager2.get_state("key") is None
    
    # Set state in second instance
    manager2.set_state("key", "value2")
    assert manager1.get_state("key") == "value1"
    assert manager2.get_state("key") == "value2"
