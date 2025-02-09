"""Tests for health monitoring functionality"""
import pytest
from unittest.mock import AsyncMock, patch

from dialogllm.core.client import LLMClient
from dialogllm.core.health import HealthMonitor

@pytest.fixture
def health_monitor():
    client = LLMClient(redis_url="mock_redis_url")
    return HealthMonitor(client)

@pytest.mark.asyncio
async def test_health_check(health_monitor):
    """Test health check functionality"""
    with patch("dialogllm.core.connection.redis.from_url") as mock_from_url:
        mock_redis_client = AsyncMock()
        mock_from_url.return_value = mock_redis_client
        health_monitor.client.queue_manager._redis_client = mock_redis_client
        
        # Test successful health check
        mock_redis_client.ping.return_value = True
        health_status = await health_monitor.check_health()
        assert health_status["status"] == "healthy"
        assert health_status["queue_connection"] == "connected"
        
        # Test failed health check
        mock_redis_client.ping.side_effect = Exception("Connection failed")
        health_status = await health_monitor.check_health()
        assert health_status["status"] == "unhealthy"
        assert health_status["queue_connection"] == "disconnected"
