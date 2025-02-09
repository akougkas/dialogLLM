import asyncio
import json
import logging
from typing import Any, Dict, Optional

from dialogllm.core.connection import QueueConnectionManager
from dialogllm.core.health import HealthMonitor
from dialogllm.models.base import Message, Role

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, redis_url: str, client_id: Optional[str] = None):
        self.queue_manager = QueueConnectionManager(redis_url)
        self.health_monitor = HealthMonitor(self)
        self.client_id = client_id or f"llm_client_{id(self)}"

    async def connect(self):
        """Connect to the message queue."""
        try:
            await self.queue_manager.connect()
            logger.info(f"LLMClient {self.client_id} connected to queue.")
        except ConnectionError as e:
            logger.error(f"LLMClient {self.client_id} failed to connect to queue: {e}")
            raise

    async def disconnect(self):
        """Disconnect from the message queue."""
        try:
            await self.queue_manager.disconnect()
            logger.info(f"LLMClient {self.client_id} disconnected from queue.")
        except Exception as e:
            logger.warning(f"Error during disconnect (continuing anyway): {e}")

    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send a message to the queue."""
        try:
            await self.queue_manager.publish_message(message)
            logger.info(f"Message sent by {self.client_id}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise

    async def get_response(self, timeout: float = 5.0) -> Optional[Message]:
        """Get a response from the queue."""
        try:
            message_data = await self.queue_manager.get_message(timeout=timeout)
            if message_data:
                message_dict = json.loads(message_data.decode('utf-8'))
                return Message(**message_dict)
            return None
        except Exception as e:
            logger.error(f"Error getting response: {e}")
            raise

    async def process_message(self, message_data: bytes):
        """Process incoming messages from the queue."""
        try:
            message = json.loads(message_data.decode('utf-8'))
            logger.info(f"Processing message: {message}")
            
            task_type = message.get('task')
            payload = message.get('payload')

            if task_type == 'generate_response':
                logger.info(f"Generating response for payload: {payload}")
                # Simulate LLM response
                await asyncio.sleep(0.5)
                response = Message(
                    content=f"This is a simulated response from {self.client_id}",
                    role=Role.ASSISTANT,
                    metadata={"client_id": self.client_id}
                )
                
                # Send response back
                await self.queue_manager.publish_message(
                    response.dict(),
                    queue_name=self.queue_manager.response_queue
                )
                logger.info(f"Response sent: {response}")
            else:
                logger.warning(f"Unknown task type: {task_type}")
        except json.JSONDecodeError:
            logger.error(f"Failed to decode message as JSON: {message_data}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def run(self):
        """Start the LLM client to listen for messages."""
        connected = False
        try:
            await self.connect()
            connected = True
            async for message in self.queue_manager.message_consumer():
                try:
                    await self.process_message(message)
                except asyncio.CancelledError:
                    logger.info(f"{self.client_id}: Message processing cancelled")
                    break
                except Exception as e:
                    logger.error(f"{self.client_id}: Error processing message: {e}")
        except asyncio.CancelledError:
            logger.info(f"{self.client_id}: Client run cancelled")
        except Exception as e:
            logger.error(f"{self.client_id}: Error during message processing loop: {e}")
            raise
        finally:
            if connected:
                try:
                    await self.disconnect()
                except Exception as e:
                    logger.error(f"{self.client_id}: Error during disconnect: {e}")

    async def health_check(self):
        """Perform a health check of the client."""
        health_status = await self.health_monitor.check_health()
        return {"status": "healthy", "components": health_status}