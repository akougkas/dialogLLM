import redis.asyncio as redis
import asyncio

class QueueConnectionManager:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._redis_client = None

    async def connect(self):
        """Establish connection to Redis."""
        try:
            self._redis_client = redis.from_url(self.redis_url)
            await self._redis_client.ping()  # Verify connection
            print("Connected to Redis successfully.")
        except redis.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    async def disconnect(self):
        """Close the connection to Redis."""
        if self._redis_client:
            await self._redis_client.close()
            print("Disconnected from Redis.")
            self._redis_client = None

    def message_consumer(self, queue_name: str = "llm_tasks"):
        """Asynchronously consume messages from the queue."""
        if not self._redis_client:
            raise Exception("Redis not connected. Call connect() first.")
            
        async def message_generator():
            while True:
                try:
                    # Use wait_for to handle timeouts more gracefully
                    message = await asyncio.wait_for(
                        self._redis_client.blpop(queue_name),
                        timeout=1.0
                    )
                    if message:
                        _, msg_data = message
                        yield msg_data
                except asyncio.TimeoutError:
                    # Expected timeout, just continue
                    continue
                except asyncio.CancelledError:
                    print("Message consumer cancelled")
                    break
                except redis.ConnectionError as e:
                    print(f"Redis connection error: {e}")
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    await asyncio.sleep(1)
                    
        return message_generator()