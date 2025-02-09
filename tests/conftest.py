"""Global test fixtures for dialogllm."""
from typing import Type
import pytest
from pydantic import BaseModel, Field


@pytest.fixture
def mock_redis(mocker):
    """Mock Redis client fixture."""
    mock_redis_client = mocker.Mock()
    return mock_redis_client


@pytest.fixture
def mock_ollama(mocker):
    """Mock Ollama client fixture."""
    mock_ollama_client = mocker.Mock()
    return mock_ollama_client


@pytest.fixture
def test_model() -> Type[BaseModel]:
    """Fixture providing a test Pydantic model for validation testing."""
    class _TestModel(BaseModel):
        """A test model for validating structured responses."""
        field1: str = Field(..., description="A test string field")
        field2: int = Field(..., description="A test integer field")
        field3: bool = Field(False, description="A test boolean field")
    
    return _TestModel