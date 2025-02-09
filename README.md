# DialogueLLM

A system for facilitating continuous conversations between Large Language Models using Redis queues.

## Project Structure

```
dialogllm/
├── src/
│   └── dialogllm/
│       ├── core/        # Core system components
│       │   └── __init__.py
│       ├── models/      # Pydantic models
│       │   └── __init__.py
│       ├── llm/         # LLM integration
│       │   └── __init__.py
│       ├── queue/       # Redis queue management
│       │   └── __init__.py
│       └── utils/       # Utility functions
│           └── __init__.py
├── tests/              # Test files
├── docs/              # Documentation
├── examples/          # Example usage
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

## Implementation Plan

See [design/MVP_IMPLEMENTATION_PLAN.md](design/MVP_IMPLEMENTATION_PLAN.md) for detailed implementation plan.

## Project Rules

See [.windsurfrules.md](.windsurfrules.md) for comprehensive project rules and guidelines.
