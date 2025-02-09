# tests/analysis/test_analysis_utils.py

import pytest
from src.dialogllm.analysis.analysis_utils import analyze_conversation

def test_analyze_conversation_empty_history():
    history = []
    metrics = analyze_conversation(history)
    assert metrics == {
        "total_messages": 0,
        "word_count": 0,
        "sentiment_distribution": {},
    }

def test_analyze_conversation_basic():
    history = ["Hello", "Hi there!", "How are you?"]
    metrics = analyze_conversation(history)
    assert metrics["total_messages"] == 3
    assert metrics["word_count"] == 6
    assert "hello" in metrics["word_frequency"]
    assert "hi" in metrics["word_frequency"]
    assert "there" in metrics["word_frequency"]
    assert "how" in metrics["word_frequency"]
    assert "are" in metrics["word_frequency"]
    assert "you" in metrics["word_frequency"]
    assert metrics["sentiment_distribution"] == {}

def test_analyze_conversation_word_frequency_counts():
    history = ["hello world", "world hello hello"]
    metrics = analyze_conversation(history)
    assert metrics["word_frequency"]["hello"] == 3
    assert metrics["word_frequency"]["world"] == 2

def test_analyze_conversation_punctuation_and_case():
    history = ["Hello, world!", "WORLD hello."]
    metrics = analyze_conversation(history)
    assert metrics["word_frequency"]["hello"] == 2
    assert metrics["word_frequency"]["world"] == 2