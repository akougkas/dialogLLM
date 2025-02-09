"""Conversation models for dialogllm."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .base import Message


class Conversation(BaseModel):
    """Model representing a conversation."""
    id: str = Field(..., description="Unique identifier for the conversation")
    messages: List[Message] = Field(default_factory=list, description="List of messages in the conversation")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata for the conversation")


class ConversationState(BaseModel):
    """Model representing the state of a conversation."""
    conversation_id: str = Field(..., description="ID of the conversation")
    is_active: bool = Field(True, description="Whether the conversation is active")
    current_turn: int = Field(0, description="Current turn number in the conversation")
    last_update: float = Field(..., description="Timestamp of last update")
