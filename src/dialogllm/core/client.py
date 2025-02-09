import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from dialogllm.core.connection import QueueConnectionManager
from dialogllm.core.health import HealthMonitor
from dialogllm.models.base import Message, Role

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, redis_url: str, client_id: Optional[str] = None,
                 model_name: Optional[str] = None,
                 model_provider: Optional[str] = None,
                 temperature: Optional[float] = None):
        """Initialize LLMClient.
        
        Args:
            redis_url: URL for Redis connection
            client_id: Optional client identifier
            model_name: Optional model name
            model_provider: Optional model provider
            temperature: Optional temperature for model generation
        """
        self.client_id = client_id or f"llm_client_{id(self)}"
        
        # Create queue names based on client_id
        self.task_queue = f"llm_tasks_{self.client_id}"
        self.response_queue = f"llm_responses_{self.client_id}"
        
        # Initialize queue manager with custom queues
        self.queue_manager = QueueConnectionManager(
            redis_url,
            task_queue=self.task_queue,
            response_queue=self.response_queue
        )
        self.health_monitor = HealthMonitor(self)
        
        # Model configuration
        self.model_name = model_name
        self.model_provider = model_provider
        self.temperature = temperature

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
            # Add client and model information to message
            message.update({
                "client_id": self.client_id,
                "response_queue": self.response_queue
            })
            
            # Add model configuration if available
            if self.model_name:
                message["model_name"] = self.model_name
            if self.model_provider:
                message["model_provider"] = self.model_provider
            if self.temperature is not None:
                message["temperature"] = self.temperature
                
            await self.queue_manager.publish_message(message)
            logger.info(f"Message sent by {self.client_id} to {self.task_queue}")
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
            
    async def generate_response(
        self, 
        prompt: str, 
        role: Role = Role.ASSISTANT,
        metadata: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0  # Increased timeout for model responses
    ) -> Message:
        """Generate a response using the configured model.
        
        Args:
            prompt: The prompt to generate a response for
            role: The role of the message sender (default: ASSISTANT)
            metadata: Optional metadata to include with the message
            timeout: Timeout in seconds for waiting for model response
            
        Returns:
            Message: The generated response message
        """
        try:
            # Create message with prompt and metadata
            message = {
                "role": role.value,
                "content": prompt,
                "timestamp": str(datetime.now()),
                "request_id": f"{self.client_id}_{int(datetime.now().timestamp())}"
            }
            
            # Add metadata if provided
            if metadata:
                message.update(metadata)
            
            # Send message and wait for response
            await self.send_message(message)
            logger.info(f"Waiting for response on {self.response_queue} (timeout: {timeout}s)")
            response = await self.get_response(timeout=timeout)
            
            if not response:
                raise TimeoutError(f"No response received from model after {timeout} seconds")
                
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
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