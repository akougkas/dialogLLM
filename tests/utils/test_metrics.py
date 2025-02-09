"""Tests for the metrics system."""
import time
import pytest
from unittest.mock import patch, MagicMock

from dialogllm.utils.metrics import MetricsManager, Timer
from dialogllm.utils.logger import Logger

@pytest.fixture
def metrics_manager():
    """Create a fresh metrics manager instance for each test."""
    MetricsManager._instance = None
    MetricsManager._initialized = False
    return MetricsManager()

def test_metrics_singleton():
    """Test that MetricsManager maintains singleton pattern."""
    manager1 = MetricsManager()
    manager2 = MetricsManager()
    assert manager1 is manager2

def test_metrics_initialization(metrics_manager):
    """Test metrics manager initialization."""
    assert metrics_manager._metrics == {}
    assert metrics_manager._initialized is True
    
    # Test reinitialization doesn't reset metrics
    metrics_manager.record("test", 1)
    metrics_manager.__init__()
    assert metrics_manager.get("test") == 1

def test_increment_metric(metrics_manager):
    """Test incrementing metrics."""
    # Test basic increment
    metrics_manager.increment("test_counter")
    assert metrics_manager.get("test_counter") == 1
    
    # Test increment with value
    metrics_manager.increment("test_counter", 2)
    assert metrics_manager.get("test_counter") == 3
    
    # Test increment with negative value
    metrics_manager.increment("test_counter", -1)
    assert metrics_manager.get("test_counter") == 2

def test_record_metric(metrics_manager):
    """Test recording metric values."""
    # Test recording different types
    test_values = [
        ("string_metric", "test"),
        ("int_metric", 42),
        ("float_metric", 42.5),
        ("bool_metric", True),
        ("list_metric", [1, 2, 3]),
        ("dict_metric", {"key": "value"})
    ]
    
    for name, value in test_values:
        metrics_manager.record(name, value)
        assert metrics_manager.get(name) == value

def test_export_metrics(metrics_manager):
    """Test exporting all metrics."""
    # Record various metrics
    metrics_manager.increment("counter1")
    metrics_manager.record("gauge1", 42.5)
    metrics_manager.record("string1", "test")
    
    exported = metrics_manager.export()
    
    # Verify all metrics are exported
    assert exported["counter1"] == 1
    assert exported["gauge1"] == 42.5
    assert exported["string1"] == "test"
    
    # Verify export is a copy
    exported["counter1"] = 999
    assert metrics_manager.get("counter1") == 1
    
    # Test empty export
    metrics_manager.clear()
    assert metrics_manager.export() == {}

def test_clear_metrics(metrics_manager):
    """Test clearing all metrics."""
    # Record multiple metrics
    metrics_manager.increment("counter1")
    metrics_manager.record("gauge1", 42.5)
    metrics_manager.record("string1", "test")
    
    # Verify metrics are recorded
    assert len(metrics_manager.export()) == 3
    
    # Clear and verify
    metrics_manager.clear()
    assert len(metrics_manager.export()) == 0
    assert metrics_manager.get("counter1") is None
    assert metrics_manager.get("gauge1") is None
    assert metrics_manager.get("string1") is None

def test_timer_basic():
    """Test basic Timer functionality."""
    metrics = MetricsManager()
    metrics.clear()
    
    with Timer("test_operation"):
        time.sleep(0.1)  # Simulate work
    
    timer_value = metrics.get("timer_test_operation")
    assert timer_value is not None
    assert 0.1 <= timer_value <= 0.2  # Allow some timing variance

def test_timer_with_error():
    """Test Timer handles errors correctly."""
    metrics = MetricsManager()
    metrics.clear()
    
    try:
        with Timer("error_operation"):
            raise ValueError("Test error")
    except ValueError:
        pass
    
    timer_value = metrics.get("timer_error_operation")
    assert timer_value is not None
    assert timer_value > 0

def test_timer_nested():
    """Test nested Timer usage."""
    metrics = MetricsManager()
    metrics.clear()
    
    with Timer("outer"):
        time.sleep(0.1)
        with Timer("inner"):
            time.sleep(0.1)
    
    outer_time = metrics.get("timer_outer")
    inner_time = metrics.get("timer_inner")
    
    assert outer_time is not None
    assert inner_time is not None
    assert outer_time >= inner_time
    assert inner_time >= 0.1

def test_timer_uninitialized():
    """Test Timer when start_time is not initialized."""
    timer = Timer("test")
    # Force uninitialized state
    timer.start_time = None
    timer.__exit__(None, None, None)
    
    metrics = MetricsManager()
    assert metrics.get("timer_test") is None
