"""Tests for dialogllm models."""
import pytest
from dialogllm.models import (
    Message,
    Conversation,
    ConversationState,
    LLMConfig,
    LLMResponse,
    QueueMessage,
)


def test_message_model():
    """Test Message model."""
    msg = Message(content="Hello", role="user")
    assert msg.content == "Hello"
    assert msg.role == "user"
    assert msg.metadata is None

    msg_with_metadata = Message(
        content="Hello",
        role="assistant",
        metadata={"confidence": 0.9}
    )
    assert msg_with_metadata.metadata["confidence"] == 0.9


def test_conversation_model():
    """Test Conversation model."""
    msg1 = Message(content="Hello", role="user")
    msg2 = Message(content="Hi there!", role="assistant")
    
    conv = Conversation(
        id="test-conv-1",
        messages=[msg1, msg2],
        metadata={"topic": "greeting"}
    )
    assert conv.id == "test-conv-1"
    assert len(conv.messages) == 2
    assert conv.metadata["topic"] == "greeting"


def test_conversation_state_model():
    """Test ConversationState model."""
    state = ConversationState(
        conversation_id="test-conv-1",
        is_active=True,
        current_turn=5,
        last_update=1234567890.0
    )
    assert state.conversation_id == "test-conv-1"
    assert state.is_active
    assert state.current_turn == 5
    assert state.last_update == 1234567890.0


def test_llm_config_model():
    """Test LLMConfig model."""
    config = LLMConfig(
        provider="openai",
        model="gpt-4",
        api_key="test-key",
        parameters={"temperature": 0.7}
    )
    assert config.provider == "openai"
    assert config.model == "gpt-4"
    assert config.api_key == "test-key"
    assert config.parameters["temperature"] == 0.7


def test_llm_response_model():
    """Test LLMResponse model."""
    response = LLMResponse(
        content="Test response",
        model="gpt-4",
        tokens_used=150,
        metadata={"finish_reason": "stop"}
    )
    assert response.content == "Test response"
    assert response.model == "gpt-4"
    assert response.tokens_used == 150
    assert response.metadata["finish_reason"] == "stop"


def test_queue_message_model():
    """Test QueueMessage model."""
    msg = QueueMessage(
        message_id="msg-1",
        conversation_id="conv-1",
        content={"text": "Hello"},
        priority=1,
        timestamp=1234567890.0,
        metadata={"source": "web"}
    )
    assert msg.message_id == "msg-1"
    assert msg.conversation_id == "conv-1"
    assert msg.content["text"] == "Hello"
    assert msg.priority == 1
    assert msg.timestamp == 1234567890.0
    assert msg.metadata["source"] == "web"
