# src/dialogllm/analysis/report_generation.py

def generate_report(analysis_metrics, performance_metrics):
    """
    Generates a report from conversation analysis and performance metrics.

    Args:
        analysis_metrics: A dictionary of analysis metrics.
        performance_metrics: A dictionary of performance metrics.

    Returns:
        A string representing the report.
    """
    report = "Conversation Analysis Report\n\n"
    report += "Analysis Metrics:\n"
    for key, value in analysis_metrics.items():
        report += f"- {key}: {value}\n"

    report += "\nPerformance Metrics:\n"
    for key, value in performance_metrics.items():
        report += f"- {key}: {value}\n"

    return report