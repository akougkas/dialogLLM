"""Queue-related models for dialogllm."""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class QueueMessage(BaseModel):
    """Model for messages in the queue."""
    message_id: str = Field(..., description="Unique identifier for the message")
    conversation_id: str = Field(..., description="ID of the conversation this message belongs to")
    content: Dict[str, Any] = Field(..., description="The actual message content")
    priority: int = Field(0, description="Message priority (higher numbers = higher priority)")
    timestamp: float = Field(..., description="When the message was queued")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional message metadata")
