#!/usr/bin/env python3
import asyncio
import json
import logging
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

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
    """Display a message in a formatted way in the terminal with enhanced formatting."""
    # Color definitions
    colors = {
        Role.ASSISTANT: "\033[38;5;39m",   # Bright Blue
        Role.USER: "\033[38;5;255m",       # Bright White
        Role.SYSTEM: "\033[38;5;208m",     # Orange
        Role.MANAGER: "\033[38;5;141m",    # Purple
    }
    reset = "\033[0m"
    dim = "\033[2m"
    bold = "\033[1m"
    
    # Get timestamp from metadata or use current time
    timestamp = message.metadata.get("timestamp", "")
    if timestamp:
        time_str = f"{dim}[{timestamp}]{reset} "
    else:
        time_str = ""
    
    # Format based on role
    color = colors.get(message.role, reset)
    if message.role == Role.SYSTEM:
        print(f"\n{color}💡 System Message:{reset}\n{dim}{message.content}{reset}\n")
    elif message.role == Role.MANAGER:
        print(f"\n{color}🔄 Manager:{reset} {message.content}\n")
    else:
        model_name = message.metadata.get("model_name", message.role.value)
        print(f"{time_str}{color}{bold}{model_name}:{reset} {message.content}")

async def message_callback(message: Message):
    """Callback function to handle new messages in the conversation."""
    await display_message(message)

async def run_client(client: LLMClient):
    """Run a client in the background."""
    try:
        await client.run()
    except asyncio.CancelledError:
        await client.disconnect()

@dataclass
class DialogueConfig:
    duration_minutes: int
    exchange_count: int
    pause_between_exchanges: float

@dataclass
class PersonaConfig:
    name: str
    role: str
    style: str
    model_name: str
    model_provider: str
    temperature: float

class DialogueManager:
    def __init__(self, master_prompt_path: str):
        self.master_prompt_path = master_prompt_path
        self.tree = ET.parse(master_prompt_path)
        self.root = self.tree.getroot()
        self.director_model = self._init_director_model()
    
    def _init_director_model(self) -> Dict:
        """Initialize the director (large) model configuration."""
        return {
            "name": os.getenv("LLAMA3_2_LATEST_NAME"),
            "provider": os.getenv("LLAMA3_2_LATEST_PROVIDER"),
            "temperature": float(os.getenv("LLAMA3_2_LATEST_TEMPERATURE")),
        }
    
    def load_config(self) -> DialogueConfig:
        """Load dialogue configuration from XML."""
        config = self.root.find("configuration")
        return DialogueConfig(
            duration_minutes=int(config.find("duration_minutes").text),
            exchange_count=int(config.find("exchange_count").text),
            pause_between_exchanges=float(config.find("pause_between_exchanges").text)
        )
    
    async def generate_story_and_personas(self, director: LLMClient) -> tuple[str, List[PersonaConfig]]:
        """Use the director model to generate the story and personas."""
        # Extract story generation prompt from XML
        story_gen = self.root.find("story_generation")
        instruction = story_gen.find("instruction").text
        constraints = story_gen.find("constraints")
        
        # Create the story generation prompt
        story_prompt = f"{instruction}\nConstraints:\n"
        for elem in constraints:
            story_prompt += f"- {elem.tag}: {elem.text}\n"
        
        # Get story and topic from director model
        story_response = await director.generate_response(
            prompt=story_prompt,
            metadata={"type": "story_generation"}
        )
        
        # Now generate personas based on the story
        persona_template = self.root.find("persona_template").text
        personas_prompt = f"Based on the story: {story_response.content}\n"
        personas_prompt += f"Generate two contrasting personas using this template:\n{persona_template}"
        
        personas_response = await director.generate_response(
            prompt=personas_prompt,
            metadata={"type": "persona_generation"}
        )
        
        # Parse the response into PersonaConfig objects
        # This is a simplified version - in reality we'd need more robust parsing
        personas = [
            PersonaConfig(
                name="Model1",
                role=personas_response.content.split("\n")[0],
                style=personas_response.content.split("\n")[1],
                model_name=os.getenv("MISTRAL_SMALL_LATEST_NAME"),
                model_provider=os.getenv("MISTRAL_SMALL_LATEST_PROVIDER"),
                temperature=float(os.getenv("MISTRAL_SMALL_LATEST_TEMPERATURE"))
            ),
            PersonaConfig(
                name="Model2",
                role=personas_response.content.split("\n")[2],
                style=personas_response.content.split("\n")[3],
                model_name=os.getenv("QWEN2_5_CODER_0_5B_NAME"),
                model_provider=os.getenv("QWEN2_5_CODER_0_5B_PROVIDER"),
                temperature=float(os.getenv("QWEN2_5_CODER_0_5B_TEMPERATURE"))
            )
        ]
        
        return story_response.content, personas

async def main():
    try:
        # Load environment variables
        load_dotenv()
        
        # Setup logging
        logger = setup_logger()
        
        # Initialize DialogueManager with master prompt
        dialogue_manager = DialogueManager("prompts/master_template.xml")
        config = dialogue_manager.load_config()
        
        # Get Redis URL from environment
        redis_url = f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}"
        
        # Initialize the conversation manager
        conversation_manager = ConversationManager(redis_url)
        conversation_manager.register_message_callback(message_callback)
        await conversation_manager.connect()
        
        # Create and connect director (large) model client
        director = LLMClient(
            redis_url=redis_url,
            client_id="Director",
            model_name=dialogue_manager.director_model["name"],
            model_provider=dialogue_manager.director_model["provider"],
            temperature=dialogue_manager.director_model["temperature"]
        )
        await director.connect()
        
        # Generate story and personas using the director model
        story, personas = await dialogue_manager.generate_story_and_personas(director)
        
        # Start conversation with generated personas
        await conversation_manager.start_conversation([
            {
                "id": f"persona_{i}",
                "name": persona.name,
                "role": persona.role,
                "style": persona.style,
                "model_name": persona.model_name,
                "model_provider": persona.model_provider,
                "temperature": persona.temperature
            } for i, persona in enumerate(personas)
        ])
        
        # Run the conversation manager
        await conversation_manager.run()
        
        model_clients = []
        for persona in personas:
            client = LLMClient(
                redis_url=redis_url,
                client_id=persona.name,
                model_name=persona.model_name,
                model_provider=persona.model_provider,
                temperature=persona.temperature
            )
            await client.connect()
            model_clients.append(client)
        
        # Start client background tasks
        client_tasks = [asyncio.create_task(run_client(client)) for client in model_clients]
        
        # Initialize the conversation with generated content
        system_prompts = [
            Message(
                role=Role.SYSTEM,
                content=f"Welcome to today's dialogue. {story}",
                metadata={"type": "init", "timestamp": datetime.now().isoformat()}
            )
        ]
        
        # Add persona prompts
        for persona in personas:
            system_prompts.append(Message(
                role=Role.SYSTEM,
                content=f"{persona.role}\n{persona.style}",
                metadata={
                    "type": "persona",
                    "model_name": persona.name,
                    "model": persona.model_name,
                    "timestamp": datetime.now().isoformat()
                }
            ))
        
        # Initialize the conversation
        for prompt in system_prompts:
            await conversation_manager.add_message(prompt)
            await display_message(prompt)
            await asyncio.sleep(0.5)
        
        # Run the dialogue for specified duration
        start_time = datetime.now()
        exchange_count = 0
        
        while (datetime.now() - start_time).total_seconds() < config.duration_minutes * 60:
            for i, client in enumerate(model_clients):
                # Get last message
                last_message = await conversation_manager.get_last_message()
                
                # Generate response
                response = await client.generate_response(
                    prompt=last_message.content,
                    metadata={
                        "model_name": personas[i].name,
                        "model": personas[i].model_name,
                        "temperature": personas[i].temperature,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                if response:
                    await conversation_manager.add_message(response)
                    await asyncio.sleep(config.pause_between_exchanges)
            
            exchange_count += 1
            if exchange_count >= config.exchange_count:
                break
        
        # Generate conclusion using director
        conclusion_prompt = "Based on the dialogue so far, generate a thoughtful conclusion that synthesizes the key insights."
        conclusion = await director.generate_response(
            prompt=conclusion_prompt,
            metadata={"type": "conclusion", "timestamp": datetime.now().isoformat()}
        )
        
        if conclusion:
            await conversation_manager.add_message(conclusion)
            await display_message(conclusion)
    
    except Exception as e:
        logger.error(f"Error during dialogue: {str(e)}")
        raise
    
    finally:
        # Clean up
        for task in client_tasks:
            task.cancel()
        await asyncio.gather(*client_tasks, return_exceptions=True)
        
        for client in model_clients:
            await client.disconnect()
        await director.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
