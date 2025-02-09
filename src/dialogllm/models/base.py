"""Base models for dialogllm."""
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class Role(str, Enum):
    """Enum for message roles."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    MANAGER = "manager"


class Message(BaseModel):
    """Base message model for all communications."""
    content: str = Field(..., description="The content of the message")
    role: Role = Field(..., description="The role of the sender")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata for the message")
