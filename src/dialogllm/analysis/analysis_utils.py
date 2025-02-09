# src/dialogllm/analysis/analysis_utils.py

from collections import Counter
import re

def analyze_conversation(conversation_history):
    """
    Analyzes a conversation history and extracts relevant metrics.

    Args:
        conversation_history: A list of messages representing the conversation.
            Each message should be a string.

    Returns:
        A dictionary of analysis metrics.
    """
    if not conversation_history:
        return {
            "total_messages": 0,
            "word_count": 0,
            "sentiment_distribution": {},
        }

    total_messages = len(conversation_history)
    word_count = sum(len(message.split()) for message in conversation_history)
    # Remove punctuation and convert to lowercase
    words = []
    for message in conversation_history:
        message = re.sub(r'[^\w\s]', '', message).lower()
        words.extend(message.split())

    word_frequency = Counter(words)

    # Placeholder for sentiment analysis (can be added later with NLP libraries)
    sentiment_distribution = {}

    return {
        "total_messages": total_messages,
        "word_count": word_count,
        "word_frequency": word_frequency,
        "sentiment_distribution": sentiment_distribution,
    }