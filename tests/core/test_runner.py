"""Tests for the runner module."""
import pytest
from unittest.mock import AsyncMock, patch
from dialogllm.core.runner import main

@pytest.mark.asyncio
async def test_main():
    """Test the main function."""
    with patch("dialogllm.core.runner.LLMClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        # Test with default Redis URL
        await main()
        mock_client_class.assert_called_once_with(redis_url="redis://localhost:6379")
        mock_client.run.assert_called_once()

@pytest.mark.asyncio
async def test_main_with_custom_redis_url():
    """Test the main function with custom Redis URL."""
    with patch("dialogllm.core.runner.LLMClient") as mock_client_class, \
         patch.dict("os.environ", {"REDIS_URL": "redis://custom:6379"}):
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        await main()
        mock_client_class.assert_called_once_with(redis_url="redis://custom:6379")
        mock_client.run.assert_called_once()
