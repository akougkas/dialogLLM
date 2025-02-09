"""Tests for the timer utility."""
import asyncio
import time
import pytest
from dialogllm.utils.timer import Timer

def test_timer_initialization():
    """Test timer initialization."""
    timer = Timer()
    assert timer._start_time is None
    assert timer.elapsed_time() == 0.0

def test_timer_start():
    """Test timer start functionality."""
    timer = Timer()
    timer.start()
    assert timer._start_time is not None
    assert isinstance(timer._start_time, float)

@pytest.mark.asyncio
async def test_timer_elapsed_time():
    """Test timer elapsed time calculation."""
    timer = Timer()
    timer.start()
    # Sleep for a short duration
    await asyncio.sleep(0.1)
    elapsed = timer.elapsed_time()
    assert elapsed > 0.0
    assert 0.1 <= elapsed <= 0.2  # Allow some timing variance

@pytest.mark.asyncio
async def test_timer_delay():
    """Test timer delay functionality."""
    timer = Timer()
    start_time = time.monotonic()
    
    await timer.delay(0.1)
    
    elapsed = time.monotonic() - start_time
    assert 0.1 <= elapsed <= 0.2  # Allow some timing variance

@pytest.mark.asyncio
async def test_timer_multiple_measurements():
    """Test multiple timer measurements."""
    timer = Timer()
    
    # First measurement
    timer.start()
    await asyncio.sleep(0.1)
    first_elapsed = timer.elapsed_time()
    
    # Second measurement
    await asyncio.sleep(0.1)
    second_elapsed = timer.elapsed_time()
    
    assert 0.1 <= first_elapsed <= 0.2
    assert second_elapsed > first_elapsed
    assert 0.2 <= second_elapsed <= 0.3

def test_timer_no_start():
    """Test timer behavior when not started."""
    timer = Timer()
    assert timer.elapsed_time() == 0.0

@pytest.mark.asyncio
async def test_multiple_delays():
    """Test multiple sequential delays."""
    timer = Timer()
    start_time = time.monotonic()
    
    # Multiple short delays
    for _ in range(3):
        await timer.delay(0.1)
    
    elapsed = time.monotonic() - start_time
    assert 0.3 <= elapsed <= 0.4  # Allow some timing variance

@pytest.mark.asyncio
async def test_timer_concurrent_delays():
    """Test concurrent delays using asyncio.gather."""
    timer = Timer()
    start_time = time.monotonic()
    
    # Run three 0.1s delays concurrently
    await asyncio.gather(
        timer.delay(0.1),
        timer.delay(0.1),
        timer.delay(0.1)
    )
    
    elapsed = time.monotonic() - start_time
    # Should take ~0.1s total since delays run concurrently
    assert 0.1 <= elapsed <= 0.2
