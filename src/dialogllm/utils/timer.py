# src/dialogllm/utils/timer.py
import asyncio
import time

class Timer:
    """Timer utility for measuring elapsed time and implementing delays.
    
    This class provides functionality for:
    - Starting a timer
    - Measuring elapsed time
    - Implementing asynchronous delays
    
    The timer uses monotonic time to ensure accurate measurements even if the system
    clock is adjusted during timing.
    """
    def __init__(self):
        """Initialize a new Timer instance with no start time."""
        self._start_time = None

    def start(self):
        """Start the timer using monotonic time."""
        self._start_time = time.monotonic()

    def elapsed_time(self) -> float:
        """Get the elapsed time since the timer was started.
        
        Returns:
            float: The elapsed time in seconds. Returns 0.0 if timer wasn't started.
        """
        if self._start_time is None:
            return 0.0
        return time.monotonic() - self._start_time

    async def delay(self, seconds: float) -> None:
        """Implement an asynchronous delay.
        
        Args:
            seconds (float): The number of seconds to delay.
        """
        await asyncio.sleep(seconds)