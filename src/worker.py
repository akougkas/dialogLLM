#!/usr/bin/env python3
import asyncio
import json
import logging
import os
from datetime import datetime

from dotenv import load_dotenv

from dialogllm.core.connection import QueueConnectionManager
from dialogllm.llm.client import OllamaClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "name": "%(name)s", "thread": %(thread)d, "process": %(process)d}'
)
logger = logging.getLogger("dialogllm.worker")

class LLMWorker:
    def __init__(self, redis_url: str, ollama_url: str = "http://localhost:11434"):
        self.redis_url = redis_url
        self.queue_manager = QueueConnectionManager(redis_url)
        self.ollama_client = OllamaClient(ollama_url)
        
    async def connect(self):
        """Connect to Redis."""
        await self.queue_manager.connect()
        
    async def disconnect(self):
        """Disconnect from Redis."""
        await self.queue_manager.disconnect()
        
    async def process_message(self, message_data: bytes):
        """Process a message from the queue."""
        try:
            # Parse message
            message = json.loads(message_data.decode('utf-8'))
            logger.info(f"Processing message: {message.get('request_id')}")
            
            # Generate response using Ollama
            model = message.get('model_name', 'llama2')
            response = await self.ollama_client.generate(
                prompt=message['content'],
                model=model
            )
            
            # Create response message
            response_message = {
                "role": "assistant",
                "content": response['response'],
                "timestamp": str(datetime.now()),
                "request_id": message.get('request_id'),
                "model": model
            }
            
            # Get response queue from message or use default
            response_queue = message.get('response_queue', 'llm_responses')
            
            # Send response back
            await self.queue_manager.publish_message(
                response_message,
                queue_name=response_queue
            )
            logger.info(f"Response sent to {response_queue}")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Try to send error response if possible
            if 'response_queue' in message and 'request_id' in message:
                error_message = {
                    "role": "error",
                    "content": str(e),
                    "timestamp": str(datetime.now()),
                    "request_id": message['request_id']
                }
                try:
                    await self.queue_manager.publish_message(
                        error_message,
                        queue_name=message['response_queue']
                    )
                except Exception as e2:
                    logger.error(f"Failed to send error response: {e2}")
    
    async def run(self):
        """Run the worker, processing messages from the queue."""
        try:
            await self.connect()
            logger.info("LLM Worker started")
            
            async for message in self.queue_manager.message_consumer():
                await self.process_message(message)
                
        except asyncio.CancelledError:
            logger.info("Worker cancelled")
        except Exception as e:
            logger.error(f"Worker error: {e}")
        finally:
            await self.disconnect()

async def main():
    # Load environment variables
    load_dotenv()
    
    # Get Redis URL from environment
    redis_url = f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}"
    ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    
    # Create and run worker
    worker = LLMWorker(redis_url, ollama_url)
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
