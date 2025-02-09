class DialogLLMError(Exception):
    """Base class for all DialogLLM exceptions."""
    pass

class ConfigurationError(DialogLLMError):
    """Exception raised for configuration related errors."""
    pass

class LLMClientError(DialogLLMError):
    """Exception raised for errors in LLM client interactions."""
    pass

class QueueError(DialogLLMError):
    """Exception raised for queue related errors."""
    pass

class StateError(DialogLLMError):
    """Exception raised for state management errors."""
    pass
