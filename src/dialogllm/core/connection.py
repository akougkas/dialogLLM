import json
import logging
from typing import Any, Dict

import redis.asyncio as redis
import asyncio

logger = logging.getLogger(__name__)

class QueueConnectionManager:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._redis_client = None
        self.response_queue = "llm_responses"
        self.task_queue = "llm_tasks"

    async def connect(self):
        """Establish connection to Redis."""
        try:
            self._redis_client = redis.from_url(self.redis_url)
            await self._redis_client.ping()  # Verify connection
            logger.info("Connected to Redis successfully.")
        except redis.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    async def disconnect(self):
        """Close the connection to Redis."""
        if self._redis_client:
            await self._redis_client.close()
            logger.info("Disconnected from Redis.")
            self._redis_client = None

    async def publish_message(self, message: Dict[str, Any], queue_name: str = None) -> None:
        """Publish a message to a Redis queue."""
        if not self._redis_client:
            raise Exception("Redis not connected. Call connect() first.")

        queue = queue_name or self.task_queue
        try:
            message_data = json.dumps(message).encode('utf-8')
            await self._redis_client.rpush(queue, message_data)
            logger.debug(f"Published message to {queue}: {message}")
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            raise

    async def get_message(self, queue_name: str = None, timeout: float = 1.0) -> bytes:
        """Get a single message from a Redis queue."""
        if not self._redis_client:
            raise Exception("Redis not connected. Call connect() first.")

        queue = queue_name or self.response_queue
        try:
            result = await asyncio.wait_for(
                self._redis_client.blpop(queue),
                timeout=timeout
            )
            if result:
                _, msg_data = result
                return msg_data
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Failed to get message: {e}")
            raise

    async def message_consumer(self, queue_name: str = None):
        """Asynchronously consume messages from the queue."""
        if not self._redis_client:
            raise Exception("Redis not connected. Call connect() first.")

        queue = queue_name or self.task_queue
        while True:
            try:
                message = await self.get_message(queue)
                if message:
                    yield message
                await asyncio.sleep(0.1)  # Prevent busy waiting
            except asyncio.CancelledError:
                logger.info("Message consumer cancelled")
                break
            except Exception as e:
                logger.error(f"Error in message consumer: {e}")
                await asyncio.sleep(1)  # Back off on error