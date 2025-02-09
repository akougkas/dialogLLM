# tests/analysis/test_performance_calculators.py

import pytest
import datetime
from src.dialogllm.analysis.performance_calculators import calculate_performance_metrics

def test_calculate_performance_metrics_empty_history():
    history = []
    metrics = calculate_performance_metrics(history)
    assert metrics == {
        "average_turn_time": 0,
        "user_turn_count": 0,
        "bot_turn_count": 0,
    }

def test_calculate_performance_metrics_basic():
    now = datetime.datetime.now()
    history = [
        {"user": "Hello", "bot": "Hi there!", "user_timestamp": now, "bot_timestamp": now + datetime.timedelta(seconds=2)},
        {"user": "How are you?", "bot": "I am good.", "user_timestamp": now + datetime.timedelta(seconds=5), "bot_timestamp": now + datetime.timedelta(seconds=8)}
    ]
    metrics = calculate_performance_metrics(history)
    assert metrics["user_turn_count"] == 2
    assert metrics["bot_turn_count"] == 2
    assert metrics["average_turn_time"] == 2.5  # (2 + 3) / 2

def test_calculate_performance_metrics_only_user_turns():
    history = [{"user": "Hello"}, {"user": "How are you?"}]
    metrics = calculate_performance_metrics(history)
    assert metrics["user_turn_count"] == 2
    assert metrics["bot_turn_count"] == 0
    assert metrics["average_turn_time"] == 0

def test_calculate_performance_metrics_only_bot_turns():
    history = [{"bot": "Hi there!"}, {"bot": "I am good."}]
    metrics = calculate_performance_metrics(history)
    assert metrics["user_turn_count"] == 0
    assert metrics["bot_turn_count"] == 2
    assert metrics["average_turn_time"] == 0