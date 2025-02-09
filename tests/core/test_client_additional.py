"""Additional tests for LLMClient."""
import pytest
import json
from unittest.mock import AsyncMock, patch

from dialogllm.core.client import LLMClient

@pytest.fixture
def llm_client():
    return LLMClient(redis_url="mock_redis_url")

@pytest.mark.asyncio
async def test_llm_client_process_message_unknown_task(llm_client):
    """Test processing message with unknown task type."""
    message_payload = {"task": "unknown_task", "payload": {}}
    message_bytes = json.dumps(message_payload).encode('utf-8')
    await llm_client.process_message(message_bytes)
    # No assertion needed, just verifying it doesn't raise an exception

@pytest.mark.asyncio
async def test_llm_client_process_message_invalid_json(llm_client):
    """Test processing message with invalid JSON."""
    message_bytes = b"invalid json"
    await llm_client.process_message(message_bytes)
    # No assertion needed, just verifying it doesn't raise an exception

@pytest.mark.asyncio
async def test_llm_client_process_message_missing_task(llm_client):
    """Test processing message with missing task field."""
    message_payload = {"payload": {}}
    message_bytes = json.dumps(message_payload).encode('utf-8')
    await llm_client.process_message(message_bytes)
    # No assertion needed, just verifying it doesn't raise an exception

@pytest.mark.asyncio
async def test_llm_client_connect_error(llm_client):
    """Test connection error handling."""
    with patch("dialogllm.core.connection.redis.from_url") as mock_from_url:
        mock_redis_client = AsyncMock()
        mock_redis_client.ping.side_effect = ConnectionError("Failed to connect")
        mock_from_url.return_value = mock_redis_client
        with pytest.raises(ConnectionError):
            await llm_client.connect()

@pytest.mark.asyncio
async def test_llm_client_disconnect_error(llm_client):
    """Test disconnection error handling."""
    with patch("dialogllm.core.connection.redis.from_url") as mock_from_url:
        mock_redis_client = AsyncMock()
        mock_redis_client.close.side_effect = Exception("Failed to disconnect")
        mock_from_url.return_value = mock_redis_client
        llm_client.queue_manager._redis_client = mock_redis_client
        
        # Should handle the exception gracefully
        try:
            await llm_client.disconnect()
        except Exception as e:
            pytest.fail(f"disconnect() should handle exceptions gracefully: {e}")

@pytest.mark.asyncio
async def test_llm_client_run_connection_error(llm_client):
    """Test run method with connection error."""
    with patch("dialogllm.core.connection.redis.from_url") as mock_from_url:
        mock_redis_client = AsyncMock()
        mock_redis_client.ping.side_effect = ConnectionError("Failed to connect")
        mock_from_url.return_value = mock_redis_client
        
        with pytest.raises(ConnectionError):
            await llm_client.run()

@pytest.mark.asyncio
async def test_llm_client_health_check_error(llm_client):
    """Test health check with connection error."""
    with patch("dialogllm.core.connection.redis.from_url") as mock_from_url:
        mock_redis_client = AsyncMock()
        mock_redis_client.ping.side_effect = Exception("Health check failed")
        mock_from_url.return_value = mock_redis_client
        llm_client.queue_manager._redis_client = mock_redis_client
        
        health_status = await llm_client.health_check()
        assert health_status["status"] == "healthy"  # Overall status is still healthy
        assert health_status["components"]["queue_connection"] == "disconnected"
