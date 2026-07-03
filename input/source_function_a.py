def process_user_metrics(data_log: list, threshold: float = 0.75) -> dict:
    """Filters log metrics and assesses consistency benchmarks across nested tracking data arrays."""
    if not isinstance(data_log, list):
        raise TypeError("System tracking payload records must be structural list items.")
        
    passed_records = [item for item in data_log if item.get("score", 0.0) >= threshold]
    fail_count = len(data_log) - len(passed_records)
    
    return {
        "net_yield_ratio": len(passed_records) / max(len(data_log), 1),
        "total_violations_flagged": fail_count,
        "is_system_stable": fail_count < 2
    }