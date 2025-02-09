# DialogueLLM Implementation Prompts

This document contains carefully crafted prompts for each phase of the DialogueLLM implementation. Each prompt follows best practices in prompt engineering:
- Clear context and objectives
- Specific requirements and constraints
- Expected outputs and validation criteria
- Step-by-step guidance
- Error handling considerations

## Phase 1: Infrastructure Setup

### 1.1 Redis Setup and Configuration
```xml
<prompt role="system">
Task: Set up and configure Redis for DialogueLLM message queuing
Context: We need a Redis instance configured for optimal message queue performance
Constraints:
- Python 3.11+ compatibility
- Message persistence requirements
- Queue monitoring capabilities

Please implement:
1. Redis connection configuration
2. Queue structure definition
3. Basic monitoring setup
4. Error handling patterns

Expected Output:
- src/dialogllm/queue/connection.py with connection handling
- src/dialogllm/queue/manager.py with core queue operations
- src/dialogllm/queue/monitoring.py with monitoring utilities
- Documentation in module docstrings
</prompt>
```

### 1.2 Python Environment Setup
```xml
<prompt role="system">
Task: Create Python project structure with dependency management
Context: Setting up a clean, maintainable Python project structure
Requirements:
- Python 3.11+ environment
- Dependencies: redis-py, ollama, pydantic
- Development tools setup

Please implement:
1. Update pyproject.toml if needed
2. Create src/dialogllm/utils/logging.py
3. Create tests/conftest.py with fixtures
4. Update development tool configurations

Validation Criteria:
- All dependencies install cleanly
- Development tools function correctly
- Project structure follows best practices
</prompt>
```

## Phase 2: LLM Integration

### 2.1 Ollama Client Implementation
```xml
<prompt role="system">
Task: Implement Ollama client with structured outputs
Context: We need a robust Ollama client supporting our Pydantic models
Reference: Previous message format definitions

Please implement:
1. OllamaClient class with structured output support
2. Message validation using Pydantic models
3. Error handling for LLM responses
4. Performance monitoring integration

Expected Output:
- src/dialogllm/llm/client.py with complete implementation
- tests/llm/test_client.py with integration tests
- src/dialogllm/llm/monitoring.py with performance utilities
</prompt>
```

### 2.2 Conversation Manager
```xml
<prompt role="system">
Task: Implement conversation flow management
Context: Managing message flow between LLMs using Redis queues
Requirements:
- Message routing logic
- Conversation timing control
- State management

Please implement:
1. ConversationManager class
2. Timer implementation
3. State management utilities
4. Error recovery mechanisms

Validation Criteria:
- Proper message routing
- Accurate conversation timing
- Robust error handling
</prompt>
```

## Phase 3: Core Communication

### 3.1 Client Node Implementation
```xml
<prompt role="system">
Task: Implement LLM client nodes
Context: Creating independent LLM clients that connect to Redis
Requirements:
- Asynchronous message handling
- Queue connection management
- Message processing logic

Please implement:
1. LLMClient class
2. Queue connection handling
3. Message processing pipeline
4. Health monitoring

Expected Output:
- src/dialogllm/core/client.py with async implementation
- src/dialogllm/core/connection.py with connection utilities
- src/dialogllm/core/health.py with health checks
</prompt>
```

### 3.2 Manager Node Implementation
```xml
<prompt role="system">
Task: Implement conversation manager node
Context: Central node managing conversation flow
Requirements:
- Story/persona generation
- Conversation initialization
- Monitoring and control

Please implement:
1. ManagerNode class
2. Story generation logic
3. Conversation initialization
4. Monitoring dashboard

Validation Criteria:
- Successful story generation
- Proper conversation initialization
- Effective monitoring
</prompt>
```

## Phase 4: Logging and Analysis

### 4.1 Logging System
```xml
<prompt role="system">
Task: Implement comprehensive logging system
Context: Capturing all relevant conversation and system data
Requirements:
- Structured logging
- Performance metrics
- Error tracking

Please implement:
1. Logging configuration
2. Metric collection
3. Error tracking system
4. Log rotation and management

Expected Output:
- src/dialogllm/utils/logging.py
- src/dialogllm/utils/metrics.py
- src/dialogllm/utils/errors.py
</prompt>
```

### 4.2 Analysis Tools
```xml
<prompt role="system">
Task: Implement conversation analysis tools
Context: Tools for analyzing conversation quality and performance
Requirements:
- Basic metrics calculation
- Conversation analysis
- Performance reporting

Please implement:
1. Analysis utilities
2. Report generation
3. Performance calculators
4. Visualization helpers

Validation Criteria:
- Accurate metrics calculation
- Useful analysis output
- Performance insights
</prompt>
```

## Phase 5: Testing and Integration

### 5.1 System Testing
```xml
<prompt role="system">
Task: Implement system-wide testing
Context: Ensuring all components work together correctly
Requirements:
- Component testing
- Integration testing
- Performance testing

Please implement:
1. Test suite structure
2. Component tests
3. Integration tests
4. Performance benchmarks

Expected Output:
- Complete test suite
- CI/CD configuration
- Performance test results
</prompt>
```

## Usage Guidelines

1. Each prompt should be used sequentially within its phase
2. Validate outputs against provided criteria before moving to next step
3. Document any deviations or additional requirements
4. Maintain consistent code style and documentation
5. Update prompts based on implementation feedback

## Success Metrics

For each prompt:
1. Code passes all tests
2. Documentation is complete
3. Error handling is robust
4. Performance meets requirements
5. Integration is successful
