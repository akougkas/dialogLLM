# Setting Up and Running DialogLLM

Let's set up and run DialogLLM with Redis and Ollama, including configuration of environment variables and model settings.

## Tasks

1. Set up the environment file with model configurations
2. Configure Redis connection
3. Set up Ollama with required models
4. Create a simple chat application to test the system
5. Monitor and validate the conversation flow

## Implementation Steps

### 1. Environment Configuration

Create a comprehensive `.env` file with model configurations:

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # Optional, if authentication is enabled

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_TIMEOUT=30

# Model Configurations
AVAILABLE_MODELS={
    "llama2": {
        "name": "llama2",
        "provider": "ollama",
        "capabilities": [
            "general_conversation",
            "code_generation",
            "analysis"
        ],
        "context_length": 4096,
        "parameters": {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40
        }
    },
    "codellama": {
        "name": "codellama",
        "provider": "ollama",
        "capabilities": [
            "code_generation",
            "code_explanation",
            "debugging",
            "technical_writing"
        ],
        "context_length": 8192,
        "parameters": {
            "temperature": 0.5,
            "top_p": 0.95,
            "top_k": 50
        }
    },
    "mistral": {
        "name": "mistral",
        "provider": "ollama",
        "capabilities": [
            "general_conversation",
            "analysis",
            "summarization"
        ],
        "context_length": 8192,
        "parameters": {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40
        }
    }
}

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=dialogllm.log

# Performance Monitoring
ENABLE_MONITORING=true
METRICS_COLLECTION_INTERVAL=60  # seconds
PERFORMANCE_THRESHOLD_MS=100    # Response time threshold
```

### 2. Example Chat Application

Create a simple chat application (`examples/chat.py`):

```python
import asyncio
import os
from typing import Dict, Any
import json
from dotenv import load_dotenv

from dialogllm.core.client import LLMClient
from dialogllm.models import Message, Conversation
from dialogllm.queue.conversation_manager import ConversationManager
from dialogllm.utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger()

async def main():
    # Initialize clients
    llm_client = LLMClient()
    await llm_client.connect()
    
    conv_manager = ConversationManager()
    await conv_manager.connect()
    
    # Create a new conversation
    conversation = Conversation(
        id="test-conversation-1",
        messages=[],
        metadata={"topic": "general"}
    )
    
    try:
        while True:
            # Get user input
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                break
                
            # Create user message
            user_message = Message(
                content=user_input,
                role="user"
            )
            conversation.messages.append(user_message)
            
            # Get model configuration
            model_config = json.loads(os.getenv("AVAILABLE_MODELS"))["llama2"]
            
            # Generate response
            response = await llm_client.generate(
                prompt=user_input,
                model=model_config["name"]
            )
            
            # Create assistant message
            assistant_message = Message(
                content=response["response"],
                role="assistant"
            )
            conversation.messages.append(assistant_message)
            
            # Store conversation state
            await conv_manager.save_conversation(conversation)
            
            print(f"Assistant: {assistant_message.content}")
            
    except KeyboardInterrupt:
        print("\nGracefully shutting down...")
    finally:
        await llm_client.disconnect()
        await conv_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Setup Instructions

1. Start Redis:
```bash
# Install Redis if not already installed
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis

# Verify Redis is running
redis-cli ping  # Should return PONG
```

2. Install and start Ollama:
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Pull required models
ollama pull llama2
ollama pull codellama
ollama pull mistral
```

3. Run the chat application:
```bash
# Install the package
pip install -e .

# Run the example
python examples/chat.py
```

### 4. Monitoring

Monitor the conversation in real-time:

1. View logs:
```bash
tail -f dialogllm.log
```

2. Monitor Redis:
```bash
# Connect to Redis CLI
redis-cli

# Monitor conversations
KEYS "conversation:*"
```

3. Check Ollama status:
```bash
curl http://localhost:11434/api/tags
```

### 5. Testing Different Models

To test different models, modify the model selection in the chat application:

```python
# Example: Use codellama for code-related questions
model_config = json.loads(os.getenv("AVAILABLE_MODELS"))["codellama"]

# Example: Use mistral for analysis
model_config = json.loads(os.getenv("AVAILABLE_MODELS"))["mistral"]
```

# DialogLLM Distributed Deployment Setup

## System Architecture

### 1. Manager Node (Desktop)
- **Hostname**: desktop
- **IP**: 192.168.86.139
- **LLM Service**: 
  - Ollama running on port 11434
  - Model: mistral-small:latest
  - Role: Story generation and conversation orchestration
- **Components**:
  - ConversationManager
  - Redis message broker
  - Master template processing
  - Logging and monitoring

### 2. Participant Node 1 (Laptop)
- **Hostname**: laptop
- **IP**: 192.168.86.200
- **Hardware**: 8GB NVIDIA RTX 4070
- **LLM Service**: 
  - Ollama with all available models
  - Dedicated persona instance
  - Custom model configuration

### 3. Participant Node 2 (Mini)
- **Hostname**: mini
- **IP**: 192.168.86.249
- **Hardware**: 16GB AMD Radeon 6950XT
- **LLM Service**: 
  - Ollama with all available models
  - Dedicated persona instance
  - Custom model configuration

## Deployment Flow

### Phase 1: Manager Initialization
1. Load master template from XML
2. Connect to Redis message broker
3. Initialize ConversationManager
4. Use mistral-small to:
   - Generate storyline and concepts
   - Define participant personas
   - Create custom prompts for each persona

### Phase 2: Participant Setup
1. Deploy participant services to laptop and mini
2. Each participant:
   - Receives persona configuration
   - Loads appropriate LLM model
   - Connects to Redis queues
   - Initializes message handlers

### Phase 3: Conversation Flow
1. Manager routes messages between participants
2. Each participant:
   - Listens on dedicated queue
   - Processes messages through LLM
   - Responds based on persona
3. Manager:
   - Logs all interactions
   - Monitors conversation flow
   - Handles error recovery

## Configuration Requirements

### Environment Variables
```env
# Manager Node
REDIS_HOST=192.168.86.139
REDIS_PORT=6379
OLLAMA_URL=http://localhost:11434
MANAGER_MODEL=mistral-small:latest

# Participant Nodes
REDIS_HOST=192.168.86.139  # Same for all to connect to manager
REDIS_PORT=6379
OLLAMA_URL=http://localhost:11434  # Local to each node
```

### Redis Queue Structure
```
llm_tasks_{persona_id}      # Input queue for each persona
llm_responses_{persona_id}  # Output queue for each persona
manager_queue              # System control messages
```

### Logging Requirements
- Conversation history
- Model performance metrics
- System health status
- Error tracking
- Network latency

## Testing Procedure

1. Start manager node:
   ```bash
   # On desktop (192.168.86.139)
   python src/main.py --role manager
   ```

2. Start participant nodes:
   ```bash
   # On laptop (192.168.86.200)
   python src/main.py --role participant --node-id 1

   # On mini (192.168.86.249)
   python src/main.py --role participant --node-id 2
   ```

3. Verify:
   - Redis connectivity
   - Model loading
   - Message routing
   - Conversation flow

## Success Criteria

1. Manager successfully:
   - Generates story and personas
   - Routes messages
   - Maintains conversation state

2. Participants successfully:
   - Load correct models
   - Process messages
   - Maintain persona consistency

3. System demonstrates:
   - Reliable message delivery
   - Proper error handling
   - Consistent performance

## Error Handling

1. Node Failures:
   - Detect disconnected participants
   - Attempt reconnection
   - Save conversation state

2. Model Errors:
   - Retry failed generations
   - Fall back to alternative models
   - Log errors for analysis

3. Network Issues:
   - Handle Redis connection loss
   - Buffer messages when needed
   - Resync on reconnection


### Next Steps

1. Implement model selection based on message content/intent
2. Add conversation history management
3. Implement rate limiting and queue management
4. Add error recovery and retry mechanisms
5. Implement conversation backup and restore
