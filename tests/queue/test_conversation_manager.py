from dialogllm.queue.conversation_manager import ManagerNode
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_manager_node(mocker):
    # Mock LLMProviderManager and its methods
    mock_llm_manager = AsyncMock()
    mocker.patch('dialogllm.queue.conversation_manager.LLMProviderManager', return_value=mock_llm_manager)

    # Mock the return values of the LLMProviderManager methods
    mock_llm_manager.generate_story.return_value = "Mock Story"

    manager = ManagerNode()

    story = await manager.generate_story() # generate_story calls llm_manager.generate_story
    print(f"Generated Story: {story}")
    assert isinstance(story, str)
    assert story == "Mock Story"

    conversation_data = await manager.initialize_conversation() # initialize_conversation calls generate_story
    print(f"Conversation Data: {conversation_data}")
    assert isinstance(conversation_data, dict)
    assert conversation_data["status"] == "initialized"
    assert conversation_data["story"] == "Mock Story"

    # Mock return value for monitor_conversation
    mock_monitoring_data = {"status": "monitoring", "active_participants": 2, "message_count": 10, "errors": 0}
    mock_llm_manager.monitor_conversation.return_value = mock_monitoring_data  # Assuming monitor_conversation is also managed by LLMProviderManager
    monitoring_data = manager.monitor_conversation() # monitor_conversation is just a placeholder
    print(f"Monitoring Data: {monitoring_data}")
    assert isinstance(monitoring_data, dict)
    assert monitoring_data["status"] == "monitoring"
