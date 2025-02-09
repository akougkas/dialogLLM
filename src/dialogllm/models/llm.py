"""LLM-related models for dialogllm."""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """Configuration for LLM providers."""
    provider: str = Field(..., description="Name of the LLM provider")
    model: str = Field(..., description="Name of the model to use")
    api_key: Optional[str] = Field(None, description="API key for the provider")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Additional parameters for the LLM")


class LLMResponse(BaseModel):
    """Model for LLM responses."""
    content: str = Field(..., description="The generated content")
    model: str = Field(..., description="The model that generated the response")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata about the response")
