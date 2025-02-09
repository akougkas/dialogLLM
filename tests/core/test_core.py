"""Tests for core functionality"""
from dialogllm.core import get_version

def test_get_version():
    """Test that version is returned correctly"""
    version = get_version()
    assert isinstance(version, str)
    assert version == "0.1.0"
