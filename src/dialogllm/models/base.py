"""Base models for dialogllm."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class Message(BaseModel):
    """Base message model for all communications."""
    content: str = Field(..., description="The content of the message")
    role: str = Field(..., description="The role of the sender (e.g., 'user', 'assistant')")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata for the message")
