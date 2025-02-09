import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Callable, Optional, Awaitable

from dialogllm.core.connection import QueueConnectionManager
from dialogllm.models.base import Message, Role

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, redis_url: str):
        """Initialize the conversation manager.
        
        Args:
            redis_url: URL for Redis connection
        """
        self.messages: List[Message] = []
        self.message_callbacks: List[Callable[[Message], Awaitable[None]]] = []
        self.queue_manager = QueueConnectionManager(redis_url)
        self.active_personas: Dict[str, Dict[str, Any]] = {}
        self.conversation_active = False
        
    async def connect(self) -> None:
        """Connect to Redis."""
        await self.queue_manager.connect()
        logger.info("Conversation manager connected to Redis")
        
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        await self.queue_manager.disconnect()
        logger.info("Conversation manager disconnected from Redis")
        
    def register_message_callback(self, callback: Callable[[Message], Awaitable[None]]) -> None:
        """Register a callback for when new messages are added."""
        self.message_callbacks.append(callback)
        
    async def notify_callbacks(self, message: Message) -> None:
        """Notify all callbacks about a new message."""
        for callback in self.message_callbacks:
            try:
                await callback(message)
            except Exception as e:
                logger.error(f"Error in message callback: {e}")

    async def add_message(self, message: Message) -> None:
        """Add a new message to the conversation and notify callbacks."""
        self.messages.append(message)
        await self.notify_callbacks(message)
        
    async def process_message(self, message_data: bytes) -> None:
        """Process an incoming message from Redis."""
        try:
            # Parse message
            message = json.loads(message_data.decode('utf-8'))
            
            # Create Message object
            msg = Message(
                role=Role(message['role']),
                content=message['content'],
                metadata=message.get('metadata', {})
            )
            
            # Add to conversation history
            await self.add_message(msg)
            
            # Handle based on role
            if msg.role == Role.ASSISTANT:
                await self.handle_assistant_message(msg)
            elif msg.role == Role.USER:
                await self.handle_user_message(msg)
            elif msg.role == Role.SYSTEM:
                await self.handle_system_message(msg)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            
    async def handle_assistant_message(self, message: Message) -> None:
        """Handle a message from an assistant (persona)."""
        try:
            # Get persona info
            persona_id = message.metadata.get('persona_id')
            if not persona_id or persona_id not in self.active_personas:
                logger.error(f"Unknown persona ID: {persona_id}")
                return
                
            # Update persona state
            persona = self.active_personas[persona_id]
            persona['last_message_time'] = datetime.now()
            
            # Check for conversation end
            if self.should_end_conversation(message):
                await self.end_conversation()
                
        except Exception as e:
            logger.error(f"Error handling assistant message: {e}")
            
    async def handle_user_message(self, message: Message) -> None:
        """Handle a message from the user."""
        try:
            # Distribute message to all active personas
            for persona_id, persona in self.active_personas.items():
                response_queue = f"llm_responses_{persona_id}"
                await self.queue_manager.publish_message(
                    message={
                        "role": "user",
                        "content": message.content,
                        "timestamp": str(datetime.now()),
                        "persona_id": persona_id,
                        "response_queue": response_queue
                    },
                    queue_name=f"llm_tasks_{persona_id}"
                )
                
        except Exception as e:
            logger.error(f"Error handling user message: {e}")
            
    async def handle_system_message(self, message: Message) -> None:
        """Handle a system message."""
        try:
            command = message.metadata.get('command')
            if command == 'start_conversation':
                await self.start_conversation(message.metadata.get('personas', []))
            elif command == 'end_conversation':
                await self.end_conversation()
                
        except Exception as e:
            logger.error(f"Error handling system message: {e}")
            
    def should_end_conversation(self, message: Message) -> bool:
        """Check if the conversation should end based on the message."""
        # Add your conversation ending logic here
        # For example, check for specific keywords or conditions
        return False
            
    async def start_conversation(self, personas: List[Dict[str, Any]]) -> None:
        """Start a new conversation with the given personas."""
        try:
            self.active_personas.clear()
            for persona in personas:
                self.active_personas[persona['id']] = {
                    **persona,
                    'last_message_time': datetime.now()
                }
            self.conversation_active = True
            logger.info(f"Started conversation with {len(personas)} personas")
            
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            
    async def end_conversation(self) -> None:
        """End the current conversation."""
        try:
            self.active_personas.clear()
            self.conversation_active = False
            logger.info("Conversation ended")
            
        except Exception as e:
            logger.error(f"Error ending conversation: {e}")
            
    async def run(self) -> None:
        """Run the conversation manager."""
        try:
            await self.connect()
            
            # Listen for messages on all relevant queues
            async for message in self.queue_manager.message_consumer():
                if not self.conversation_active:
                    continue
                await self.process_message(message)
                
        except asyncio.CancelledError:
            logger.info("Conversation manager cancelled")
        except Exception as e:
            logger.error(f"Conversation manager error: {e}")
        finally:
            await self.disconnect()
            
    def get_all_messages(self) -> List[Message]:
        """Get all messages in the conversation."""
        return self.messages.copy()

    def clear_messages(self) -> None:
        """Clear all messages from the conversation."""
        self.messages.clear()