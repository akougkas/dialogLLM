# tests/analysis/test_report_generation.py

from src.dialogllm.analysis.report_generation import generate_report

def test_generate_report_empty_metrics():
    analysis_metrics = {}
    performance_metrics = {}
    report = generate_report(analysis_metrics, performance_metrics)
    assert "Analysis Metrics:" in report
    assert "- " not in report  # No analysis metrics listed
    assert "Performance Metrics:" in report
    assert "- " not in report  # No performance metrics listed

def test_generate_report_with_metrics():
    analysis_metrics = {
        "total_messages": 3,
        "word_count": 10,
        "word_frequency": {"hello": 2, "world": 1},
    }
    performance_metrics = {
        "average_turn_time": 1.5,
        "user_turn_count": 2,
        "bot_turn_count": 2,
    }
    report = generate_report(analysis_metrics, performance_metrics)
    assert "Analysis Metrics:" in report
    assert "- total_messages: 3" in report
    assert "- word_count: 10" in report
    assert "- word_frequency: {'hello': 2, 'world': 1}" in report
    assert "Performance Metrics:" in report
    assert "- average_turn_time: 1.5" in report
    assert "- user_turn_count: 2" in report
    assert "- bot_turn_count: 2" in report