"""Tests for QueueConnectionManager."""
import pytest
import asyncio
import redis.asyncio as redis
from unittest.mock import AsyncMock, patch
from dialogllm.core.connection import QueueConnectionManager

@pytest.fixture
def queue_manager():
    return QueueConnectionManager(redis_url="redis://test:6379")

@pytest.mark.asyncio
async def test_connect_success(queue_manager):
    """Test successful connection to Redis."""
    with patch("dialogllm.core.connection.redis.from_url") as mock_from_url:
        mock_redis_client = AsyncMock()
        mock_from_url.return_value = mock_redis_client
        await queue_manager.connect()
        mock_from_url.assert_called_once_with("redis://test:6379")
        mock_redis_client.ping.assert_called_once()

@pytest.mark.asyncio
async def test_connect_failure(queue_manager):
    """Test connection failure handling."""
    with patch("dialogllm.core.connection.redis.from_url") as mock_from_url:
        mock_redis_client = AsyncMock()
        mock_redis_client.ping.side_effect = redis.ConnectionError("Connection failed")
        mock_from_url.return_value = mock_redis_client
        with pytest.raises(ConnectionError):
            await queue_manager.connect()

@pytest.mark.asyncio
async def test_disconnect(queue_manager):
    """Test disconnection from Redis."""
    mock_redis_client = AsyncMock()
    queue_manager._redis_client = mock_redis_client
    await queue_manager.disconnect()
    mock_redis_client.close.assert_called_once()
    assert queue_manager._redis_client is None

@pytest.mark.asyncio
async def test_message_consumer_not_connected(queue_manager):
    """Test message consumer when not connected."""
    with pytest.raises(Exception, match="Redis not connected"):
        consumer = queue_manager.message_consumer()
        await anext(consumer)

@pytest.mark.asyncio
async def test_message_consumer_success(queue_manager):
    """Test successful message consumption."""
    mock_redis_client = AsyncMock()
    mock_redis_client.blpop.side_effect = [
        (None, b"test_message"),
        asyncio.CancelledError(),  # To break the loop
    ]
    queue_manager._redis_client = mock_redis_client

    consumer = queue_manager.message_consumer()
    message = await anext(consumer)
    assert message == b"test_message"

@pytest.mark.asyncio
async def test_message_consumer_timeout(queue_manager):
    """Test message consumer timeout handling."""
    mock_redis_client = AsyncMock()
    mock_redis_client.blpop.side_effect = [
        asyncio.TimeoutError(),
        asyncio.CancelledError(),  # To break the loop
    ]
    queue_manager._redis_client = mock_redis_client

    consumer = queue_manager.message_consumer()
    try:
        await anext(consumer)
    except StopAsyncIteration:
        pass  # Expected behavior

@pytest.mark.asyncio
async def test_message_consumer_connection_error(queue_manager):
    """Test message consumer Redis connection error handling."""
    mock_redis_client = AsyncMock()
    mock_redis_client.blpop.side_effect = [
        redis.ConnectionError("Connection lost"),
        asyncio.CancelledError(),  # To break the loop
    ]
    queue_manager._redis_client = mock_redis_client

    consumer = queue_manager.message_consumer()
    try:
        await anext(consumer)
    except StopAsyncIteration:
        pass  # Expected behavior
