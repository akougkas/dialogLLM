#!/usr/bin/env python3
import asyncio
import json
import logging
import os
from typing import Optional

from dialogllm.core.client import LLMClient
from dialogllm.models.base import Message, Role
from dialogllm.queue.conversation_manager import ConversationManager
from dialogllm.utils.logger import setup_logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = setup_logger()
logging.getLogger().setLevel(logging.INFO)

async def display_message(message: Message):
    """Display a message in a formatted way in the terminal."""
    role_colors = {
        Role.ASSISTANT: "\033[92m",  # Green
        Role.USER: "\033[94m",       # Blue
        Role.SYSTEM: "\033[93m",     # Yellow
        Role.MANAGER: "\033[95m",    # Purple
    }
    reset_color = "\033[0m"
    
    color = role_colors.get(message.role, "")
    print(f"{color}[{message.role.value}]{reset_color}: {message.content}")

async def message_callback(message: Message):
    """Callback function to handle new messages in the conversation."""
    await display_message(message)

async def run_client(client: LLMClient):
    """Run a client in the background."""
    try:
        await client.run()
    except asyncio.CancelledError:
        await client.disconnect()

async def main():
    # Get Redis URL from environment
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # Initialize the conversation manager
    conversation_manager = ConversationManager()
    
    # Create two LLM clients with different roles
    client1 = LLMClient(redis_url=redis_url, client_id="Model1")
    client2 = LLMClient(redis_url=redis_url, client_id="Model2")
    
    # Connect the clients
    await client1.connect()
    await client2.connect()
    
    # Start client background tasks
    client1_task = asyncio.create_task(run_client(client1))
    client2_task = asyncio.create_task(run_client(client2))
    
    # Register the message callback
    conversation_manager.register_message_callback(message_callback)
    
    # Start the conversation with an initial message
    initial_message = Message(
        role=Role.SYSTEM,
        content="Let's have a short discussion about the future of AI. Model1 will start.",
        metadata={"timestamp": "2024-02-09T04:37:25"}
    )
    
    # Display the initial message
    await display_message(initial_message)
    
    # Start the conversation
    try:
        # Add initial message to start the conversation
        await conversation_manager.add_message(initial_message)
        
        # Let Model1 start
        await client1.send_message({
            'task': 'generate_response',
            'payload': initial_message.model_dump()
        })
        
        # Wait for Model1's response
        response = await client1.get_response()
        if response:
            await conversation_manager.add_message(response)
        
        # Have a back-and-forth conversation (3 turns each)
        for _ in range(3):
            # Model2's turn
            last_message = await conversation_manager.get_last_message()
            await client2.send_message({
                'task': 'generate_response',
                'payload': last_message.model_dump()
            })
            
            # Wait for Model2's response
            response = await client2.get_response()
            if response:
                await conversation_manager.add_message(response)
            
            # Model1's turn
            last_message = await conversation_manager.get_last_message()
            await client1.send_message({
                'task': 'generate_response',
                'payload': last_message.model_dump()
            })
            
            # Wait for Model1's response
            response = await client1.get_response()
            if response:
                await conversation_manager.add_message(response)
            
            # Small delay between turns for readability
            await asyncio.sleep(1)
        
        # End the conversation
        final_message = Message(
            role=Role.SYSTEM,
            content="Conversation ended successfully.",
            metadata={"timestamp": "2024-02-09T04:37:25"}
        )
        await conversation_manager.add_message(final_message)
        await display_message(final_message)
        
        # Cancel client tasks
        client1_task.cancel()
        client2_task.cancel()
        await asyncio.gather(client1_task, client2_task, return_exceptions=True)
        
    except Exception as e:
        logger.error(f"Error during conversation: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
