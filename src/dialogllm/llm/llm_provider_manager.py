import ollama
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class LLMProviderManager:
    def __init__(self):
        self.model_name = os.getenv("OLLAMA_MODEL", "deepseek-r1:32b") # Default model
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") # Default URL
        ollama.base_url = self.base_url # Set Ollama base URL

    async def generate_story(self, prompt: str) -> str:
        """Generates text using the Ollama model."""
        try:
            response = await ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    }
                ]
            )
            story_framework = response['message']['content']
            return story_framework
        except Exception as e:
            print(f"Error generating text with Ollama: {e}")
            return "Failed to generate text."