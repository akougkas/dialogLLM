from dialogllm.llm.monitoring import monitor_performance

def test_monitor_performance():
    """Test that the monitoring decorator works"""
    @monitor_performance
    def test_func():
        return "test"
    
    result = test_func()
    assert result == "test"
