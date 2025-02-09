import time
from typing import Dict, Any, Optional
from dialogllm.utils.logger import logger

class MetricsManager:
    """Singleton class for managing application metrics."""
    _instance: Optional['MetricsManager'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'MetricsManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._metrics: Dict[str, Any] = {}
            self._initialized = True
    
    def increment(self, name: str, value: int = 1) -> None:
        """Increment a metric by the specified value."""
        self._metrics[name] = self._metrics.get(name, 0) + value
        logger.debug(f"Incremented metric {name}", extra={"metric": name, "value": value})
    
    def record(self, name: str, value: Any) -> None:
        """Record a metric value."""
        self._metrics[name] = value
        logger.debug(f"Recorded metric {name}", extra={"metric": name, "value": value})
    
    def get(self, name: str) -> Any:
        """Get the current value of a metric."""
        return self._metrics.get(name)
    
    def export(self) -> Dict[str, Any]:
        """Export all metrics."""
        logger.info("Exporting metrics", extra={"metrics": self._metrics})
        return self._metrics.copy()
    
    def clear(self) -> None:
        """Clear all metrics."""
        self._metrics.clear()
        logger.info("Cleared all metrics")

class Timer:
    """Context manager for timing code blocks and recording metrics."""
    def __init__(self, name: str):
        self.name = name
        self.start_time: Optional[float] = None
        self.metrics = MetricsManager()
    
    def __enter__(self) -> 'Timer':
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.start_time is None:
            logger.error(f"Timer {self.name} was not properly initialized")
            return
            
        elapsed_time = time.time() - self.start_time
        self.metrics.record(f"timer_{self.name}", elapsed_time)
        logger.debug(
            f"Timer '{self.name}' finished", 
            extra={
                "timer": self.name,
                "duration": elapsed_time,
                "unit": "seconds"
            }
        )

# Global metrics instance
metrics = MetricsManager()