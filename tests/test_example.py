from dialogllm.core import get_version

def test_version():
    """Test that version is returned correctly"""
    assert get_version() == "0.1.0"