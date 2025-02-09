# DialogueLLM - MVP Implementation Plan

## MVP Scope Definition

The MVP will deliver a basic but functional network-based chat system enabling:
- Communication between two LLMs using Redis queues
- Real-time terminal observation of conversations
- Basic conversation logging (messages stay in the queue)
- Configurable conversation duration
- Simple analysis of conversation logs

### Out of MVP Scope
- Advanced scaling capabilities
- Complex analysis metrics
- GUI interfaces
- Advanced error recovery mechanisms

## System Flow Diagram
```
[Large LLM (Manager)] 
        ↓
    Generates
    - Story
    - Personas
        ↓
[Redis Queues]
    ├── request_queue_1  →  [LLM Client 1]
    ├── response_queue_1 ←   
    ├── request_queue_2  →  [LLM Client 2]
    └── response_queue_2 ←   
        ↓
[Terminal Observer]
    Displays conversation in real-time
```

## MVP Technical Stack

1. **Core Components:**
   - Python 3.11+ (for modern async features)
   - Redis (for message queuing)
   - Ollama (for LLM interaction)

2. **Key Libraries:**
   - `redis-py`: Redis client for Python
   - `ollama`: Local LLM integration
   - `pydantic`: Data validation
   - `asyncio`: Async operations
   - `logging`: System logging

## Critical MVP Focus Areas

1. **Message Queue Infrastructure**
   - Redis queue setup and management
   - Message format standardization
   - Queue monitoring and cleanup

2. **LLM Integration**
   - Ollama client setup
   - Prompt engineering
   - Response handling

3. **Conversation Management**
   - Message flow control
   - Conversation timing
   - Basic logging

## Implementation Roadmap

### Phase 1: Infrastructure Setup 
1. Set up development environment
   - Install Redis
   - Configure Python environment
   - Install required packages
   - Set up logging configuration

2. Implement basic Redis queue management
   - Create queue handler class
   - Implement basic pub/sub operations
   - Add queue monitoring

### Phase 2: LLM Integration 
1. Implement Ollama client wrapper
   - Basic LLM interaction
   - Prompt template system
   - Response parsing

2. Create conversation manager
   - Message routing logic
   - Basic conversation flow control
   - Timer implementation

### Phase 3: Core Communication
1. Implement client nodes
   - LLM client setup
   - Queue connection handling
   - Message processing

2. Develop manager node
   - Story/persona generation
   - Conversation initialization
   - Basic monitoring

### Phase 4: Logging and Analysis 
1. Implement logging system
   - Conversation logging
   - System state logging
   - Error logging

2. Basic analysis capabilities
   - Simple metrics collection
   - Basic conversation analysis
   - Log parsing utilities

### Phase 5: Testing and Integration 
1. System testing
   - Component testing
   - Integration testing
   - Performance testing


## MVP Templates

### Message Format
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class MessageMetadata(BaseModel):
    conversation_id: str
    sequence_number: int
    tokens_generated: int
    generation_time_ms: float

class DialogMessage(BaseModel):
    # Auto-generated fields for queue management
    queue_timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_id: str = Field(..., description="Unique message identifier")
    
    # Core message fields
    role: str = Field(..., description="Role of the message sender (e.g., 'user', 'assistant')")
    content: Dict[str, Any] = Field(..., description="Structured content based on message type")
    
    # Metadata for analysis
    metadata: MessageMetadata

# Example Structured Content Types
class StoryContent(BaseModel):
    setting: str
    characters: list[str]
    initial_situation: str

class ConversationContent(BaseModel):
    message: str
    sentiment: Optional[float] = None
    references: list[str] = Field(default_factory=list)
    
# Usage with Ollama:
'''
response = chat(
    messages=[{"role": "user", "content": prompt}],
    model="llama2",
    format=ConversationContent.model_json_schema()
)

# Validate response
content = ConversationContent.model_validate_json(response.message.content)
'''
```

Key improvements:
1. Native Redis timestamp support for message ordering
2. Structured content validation using Pydantic
3. Performance metrics (tokens, generation time)
4. Type safety and validation
5. Extensible for different message types
6. Direct integration with Ollama structured outputs

### Configuration Template
```python
{
    "redis": {
        "host": "localhost",
        "port": 6379,
        "db": 0
    },
    "conversation": {
        "duration_seconds": 300,
        "max_turns": 50
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}
```

## Success Criteria
- Two LLMs can exchange messages through Redis queues
- Conversations are properly timed and logged
- LLM token production and rates are also captured
- Terminal displays real-time conversation updates
- Basic conversation analysis is performed at the end
- System can run continuously for the configured duration

## Next Steps After MVP
1. Enhanced error handling and recovery
2. Advanced conversation analysis
3. Scaling to multiple LLM pairs
4. Web interface for monitoring
5. Advanced metrics and reporting
