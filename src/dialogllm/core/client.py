import asyncio
import json
import logging

from dialogllm.core.connection import QueueConnectionManager
from dialogllm.core.health import HealthMonitor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, redis_url: str):
        self.queue_manager = QueueConnectionManager(redis_url)
        self.health_monitor = HealthMonitor(self) # Instantiate HealthMonitor
        # Initialize message processor, etc.

    async def connect(self):
        """Connect to the message queue."""
        try:
            await self.queue_manager.connect()
            logger.info("LLMClient connected to queue.")
        except ConnectionError as e:
            logger.error(f"LLMClient failed to connect to queue: {e}")
            raise

    async def disconnect(self):
        """Disconnect from the message queue."""
        try:
            await self.queue_manager.disconnect()
            logger.info("LLMClient disconnected from queue.")
        except Exception as e:
            logger.warning(f"Error during disconnect (continuing anyway): {e}")

    async def process_message(self, message_data: bytes):
        """Process incoming messages from the queue."""
        try:
            message = json.loads(message_data.decode('utf-8'))
            logger.info(f"Processing message: {message}")
            # --- Message Processing Logic ---
            # Example: Assuming message is a dict with 'task' and 'payload'
            task_type = message.get('task')
            payload = message.get('payload')

            if task_type == 'generate_response':
                logger.info(f"Generating response for payload: {payload}")
                # Placeholder for actual LLM call
                await asyncio.sleep(1) # Simulate LLM processing time
                response = f"Response generated for task: {task_type} with payload: {payload}"
                logger.info(f"Generated response: {response}")
                # --- End of Message Processing Logic ---
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
                    logger.info("Message processing cancelled")
                    break
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        except asyncio.CancelledError:
            logger.info("Client run cancelled")
        except Exception as e:
            logger.error(f"Error during message processing loop: {e}")
            raise
        finally:
            if connected:
                try:
                    await self.disconnect()
                except Exception as e:
                    logger.error(f"Error during disconnect: {e}")

    async def health_check(self):
        """Perform a health check of the client."""
        health_status = await self.health_monitor.check_health()
        return {"status": "healthy", "components": health_status}