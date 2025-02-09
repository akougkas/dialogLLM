# DialogueLLM

A system for facilitating continuous conversations between Large Language Models using Redis queues.

## Project Structure

```
dialogllm/
├── src/
│   └── dialogllm/
│       ├── analysis/    # Analysis and performance monitoring
│       │   ├── analysis_utils.py
│       │   ├── performance_calculators.py
│       │   └── visualization_helpers.py
│       ├── core/        # Core system components
│       │   ├── client.py
│       │   ├── connection.py
│       │   └── health.py
│       ├── models/      # Pydantic models
│       │   ├── base.py           # Base message models
│       │   ├── conversation.py   # Conversation models
│       │   ├── llm.py           # LLM-related models
│       │   └── queue.py         # Queue message models
│       ├── llm/         # LLM integration
│       │   ├── client.py
│       │   └── llm_provider_manager.py
│       ├── queue/       # Redis queue management
│       │   └── conversation_manager.py
│       └── utils/       # Utility functions
│           ├── errors.py
│           ├── logger.py
│           ├── metrics.py
│           └── timer.py
├── tests/              # Test files
    ├── analysis/       # Analysis module tests
    ├── core/           # Core module tests
    ├── llm/            # LLM module tests
    ├── models/         # Model tests
    ├── queue/          # Queue module tests
    └── utils/          # Utility tests
```

## Features

- Asynchronous message processing with Redis queues
- Support for multiple LLM providers
- Structured data validation with Pydantic models
- Comprehensive logging and monitoring
- High test coverage (96%+)

## Requirements

- Python 3.11+
- Redis server
- Ollama or other supported LLM providers

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dialogllm.git
cd dialogllm
```

2. Install the package:
```bash
# For development
pip install -e '.[dev]'

# For production
pip install .
```

## Development

### Code Quality

The project uses several tools to maintain code quality:
- Black for code formatting
- isort for import sorting
- Ruff for linting
- MyPy for type checking

Run the quality checks:
```bash
black src/ tests/
isort src/ tests/
ruff check src/ tests/
mypy src/
```

### Testing

Run the test suite:
```bash
pytest tests/ -v --cov=src/dialogllm
```

The project maintains high test coverage (currently 96%) and uses:
- pytest for testing
- pytest-asyncio for async tests
- pytest-cov for coverage reporting

### Project Organization

- **analysis/**: Performance monitoring and analysis tools
- **core/**: Core system components and client interfaces
- **models/**: Pydantic models for data validation
- **llm/**: LLM provider integration
- **queue/**: Redis queue management
- **utils/**: Utility functions and helpers

## License

[Your License Here]

├── prompts/          # Implementation prompts
├── pyproject.toml    # Project configuration
└── README.md         # This file
```

## Development Setup

1. Requirements:
   - Python 3.11+
   - Redis
   - Ollama

2. Installation:
   ```bash
   pip install -e ".[dev]"
   ```

3. Development Tools:
   - pytest for testing
   - black for formatting
   - isort for import sorting
   - mypy for type checking
   - ruff for linting

4. Testing:
   ```bash
   # Run all tests with coverage
   pytest tests -v --cov=dialogllm

   # Run specific module tests
   pytest tests/llm -v --cov=dialogllm.llm

   # Run specific test file
   pytest tests/llm/test_client.py -v
   ```

   The project maintains 100% test coverage. All new code must include tests.

## Implementation Plan

See [design/MVP_IMPLEMENTATION_PLAN.md](design/MVP_IMPLEMENTATION_PLAN.md) for detailed implementation plan.

## Project Rules

See [.windsurfrules.md](.windsurfrules.md) for comprehensive project rules and guidelines.
