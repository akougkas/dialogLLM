# src/dialogllm/llm/client.py
import httpx
from pydantic import BaseModel, ValidationError
from typing import Type, Dict, Any

class OllamaClient:
    def __init__(self, api_url: str = "http://localhost:11434"):
        self.api_url = api_url

    async def generate(self, prompt: str, model: str = "llama2") -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/api/generate",
                json={
                    "prompt": prompt,
                    "model": model,
                    "stream": False,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[BaseModel],
        model: str = "llama2",
    ) -> BaseModel:
        llm_response = await self.generate(prompt, model)
        try:
            # Assuming Ollama returns json in 'response' field. Adjust as needed.
            return response_model.model_validate_json(llm_response["response"])
        except ValidationError as e:
            raise ValueError(f"Failed to parse LLM response to Pydantic model: {e}")
        except KeyError:
            raise ValueError(f"LLM response missing 'response' field: {llm_response}")