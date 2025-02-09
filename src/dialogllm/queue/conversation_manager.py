from typing import Any, Dict, List, Callable, Optional, Awaitable
from dialogllm.models.base import Message

class ConversationManager:
    def __init__(self):
        self.messages: List[Message] = []
        self.message_callbacks: List[Callable[[Message], Awaitable[None]]] = []

    def register_message_callback(self, callback: Callable[[Message], Awaitable[None]]) -> None:
        """Register a callback for when new messages are added."""
        self.message_callbacks.append(callback)

    async def add_message(self, message: Message) -> None:
        """Add a new message to the conversation."""
        self.messages.append(message)
        # Notify all callbacks
        for callback in self.message_callbacks:
            await callback(message)

    async def get_last_message(self) -> Optional[Message]:
        """Get the last message in the conversation."""
        if not self.messages:
            return None
        return self.messages[-1]

    def get_all_messages(self) -> List[Message]:
        """Get all messages in the conversation."""
        return self.messages.copy()

    def clear_messages(self) -> None:
        """Clear all messages from the conversation."""
        self.messages.clear()