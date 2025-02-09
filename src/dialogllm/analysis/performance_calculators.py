# src/dialogllm/analysis/performance_calculators.py

import time

def calculate_performance_metrics(conversation_history):
    """
    Calculates performance metrics from conversation history.

    Args:
        conversation_history: A list of dictionaries, where each dictionary
            represents a turn in the conversation and contains 'user' and 'bot' keys.

    Returns:
        A dictionary of performance metrics.
    """
    if not conversation_history:
        return {
            "average_turn_time": 0,
            "user_turn_count": 0,
            "bot_turn_count": 0,
        }

    total_turn_time = 0
    user_turn_count = 0
    bot_turn_count = 0

    for turn in conversation_history:
        if 'user' in turn and 'bot' in turn:
            user_turn_count += 1
            bot_turn_count += 1
            # Assuming turn is a dictionary with 'timestamp' for user and bot messages
            if 'user_timestamp' in turn and 'bot_timestamp' in turn:
                turn_time = turn['bot_timestamp'] - turn['user_timestamp']
                total_turn_time += turn_time.total_seconds()
        elif 'user' in turn:
            user_turn_count += 1
        elif 'bot' in turn:
            bot_turn_count += 1

    average_turn_time = total_turn_time / user_turn_count if user_turn_count > 0 else 0

    return {
        "average_turn_time": average_turn_time,
        "user_turn_count": user_turn_count,
        "bot_turn_count": bot_turn_count,
    }