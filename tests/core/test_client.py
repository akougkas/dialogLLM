import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from dialogllm.core.client import LLMClient
from dialogllm.core.connection import QueueConnectionManager
from dialogllm.core.health import HealthMonitor

class StopLoopException(Exception):
    pass

@pytest.fixture
def llm_client():
    return LLMClient(redis_url="mock_redis_url")

@pytest.mark.asyncio
async def test_llm_client_connect(llm_client):
    with patch("dialogllm.core.connection.redis.from_url") as mock_from_url:
        mock_redis_client = AsyncMock()
        mock_from_url.return_value = mock_redis_client
        await llm_client.connect()
        mock_from_url.assert_called_once_with("mock_redis_url")
        mock_redis_client.ping.assert_called_once()

@pytest.mark.asyncio
async def test_llm_client_disconnect(llm_client):
    with patch("dialogllm.core.connection.redis.from_url") as mock_from_url:
        mock_redis_client = AsyncMock()
        mock_from_url.return_value = mock_redis_client
        llm_client.queue_manager._redis_client = mock_redis_client # Set mock client
        await llm_client.disconnect()
        mock_redis_client.close.assert_called_once()

@pytest.mark.asyncio
async def test_llm_client_process_message(llm_client):
    message_payload = {"task": "generate_response", "payload": {"prompt": "test prompt"}}
    message_bytes = json.dumps(message_payload).encode('utf-8')
    await llm_client.process_message(message_bytes)
    # In a real test, you would assert the side effects of message processing

@pytest.mark.asyncio
async def test_llm_client_run_message_processing(llm_client):
    with patch("dialogllm.core.connection.redis.from_url") as mock_from_url:
        mock_redis_client = AsyncMock()
        mock_from_url.return_value = mock_redis_client
        
        # Setup message queue behavior
        message = (None, json.dumps({"task": "generate_response", "payload": {"prompt": "test"}}).encode('utf-8'))
        mock_redis_client.blpop.side_effect = [
            message,  # First call returns a message
            asyncio.TimeoutError(),  # Second call times out
        ]
        
        task = None
        try:
            # Run client with longer timeout
            async with asyncio.timeout(2.0):
                task = asyncio.create_task(llm_client.run())
                # Give time for message processing but less than the simulated processing time
                await asyncio.sleep(0.1)
                if task:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass  # Expected
        finally:
            # Ensure cleanup happens
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except (asyncio.CancelledError, Exception):
                    pass
            await llm_client.disconnect()
        
        mock_redis_client.blpop.assert_called()
        mock_redis_client.close.assert_called_once()

@pytest.mark.asyncio
async def test_llm_client_health_check(llm_client):
    with patch("dialogllm.core.connection.redis.from_url") as mock_from_url:
        mock_redis_client = AsyncMock()
        mock_from_url.return_value = mock_redis_client
        llm_client.queue_manager._redis_client = mock_redis_client
        health_status = await llm_client.health_check()
        assert health_status["status"] == "healthy"
        assert "queue_connection" in health_status["components"]
        mock_redis_client.ping.assert_called_once()