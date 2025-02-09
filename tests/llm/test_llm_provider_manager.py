"""Tests for LLMProviderManager."""
import pytest
from unittest.mock import AsyncMock
from dialogllm.llm.llm_provider_manager import LLMProviderManager

@pytest.fixture
def mock_ollama(mocker):
    mock_chat = AsyncMock()
    mock_chat.return_value = {
        'message': {
            'content': 'Test story content'
        }
    }
    mocker.patch('dialogllm.llm.llm_provider_manager.ollama.chat', mock_chat)
    return mock_chat

@pytest.fixture
def mock_env_vars(mocker):
    mocker.patch.dict('os.environ', {
        'OLLAMA_MODEL': 'test-model',
        'OLLAMA_BASE_URL': 'http://test-url:11434'
    })

@pytest.mark.asyncio
async def test_init_with_env_vars(mock_env_vars):
    """Test initialization with environment variables."""
    manager = LLMProviderManager()
    assert manager.model_name == 'test-model'
    assert manager.base_url == 'http://test-url:11434'

@pytest.mark.asyncio
async def test_init_with_defaults():
    """Test initialization with default values."""
    manager = LLMProviderManager()
    assert manager.model_name == 'deepseek-r1:32b'
    assert manager.base_url == 'http://localhost:11434'

@pytest.mark.asyncio
async def test_generate_story_success(mock_ollama):
    """Test successful story generation."""
    manager = LLMProviderManager()
    story = await manager.generate_story("Test prompt")
    assert story == "Test story content"
    mock_ollama.assert_called_once_with(
        model=manager.model_name,
        messages=[{
            'role': 'system',
            'content': 'Test prompt'
        }]
    )

@pytest.mark.asyncio
async def test_generate_story_error(mock_ollama):
    """Test error handling in story generation."""
    mock_ollama.side_effect = Exception("Test error")
    manager = LLMProviderManager()
    story = await manager.generate_story("Test prompt")
    assert story == "Failed to generate text."
