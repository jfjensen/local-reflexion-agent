# process_user_metrics

Filters and analyzes log metrics to assess consistency benchmarks across nested tracking data arrays, returning statistical summaries regarding system stability and yield efficiency.

## Summary

This function validates input payloads against a scoring threshold, filtering records based on their `score` attribute. It calculates the net yield ratio of compliant records versus total records, flags violations, and determines overall system stability if violation counts remain below a specific limit.

---

## Parameters

### `data_log: list`

A structural payload record containing tracking data items. Each item in the list must be a dictionary-like object that supports `.get()` access to retrieve metrics (specifically expecting a `"score"` key).

| Type | Required? | Description |
| :-- | -- | :-- |
| `list` | Yes | A collection of metric records, where each record is expected to contain at least the string key `"score"`. Missing keys default to `0.0`. |

### `threshold: float = 0.75`

The minimum score value required for a log item to be considered "passed". Records with scores below this value are counted as violations.

| Type | Default | Description |
| :-- | -- | :-- |
| `float` | `0.75` | The cut-off point for filtering valid metrics. Defaults to 0.75 (three quarters). |

---

## Returns

A dictionary containing the analysis results of the provided log data:

```python
{
    "net_yield_ratio": float,      # Proportion of records meeting the threshold. Range [0.0, 1.0].
    "total_violations_flagged": int, # Count of records failing to meet the score requirement.
    "is_system_stable": bool        # True if violations are fewer than 2; False otherwise.
}
```

### Return Object Details

*   **`net_yield_ratio`** (float): The calculated ratio of passed records against total input length. Includes protection for empty lists to prevent division by zero errors. Calculated as `len(passed_records) / max(len(data_log), 1)`.
*   **`total_violations_flagged`** (int): An integer representing the count of items in `data_log` where `score < threshold`. If a record lacks a `"score"` key, it is treated as having a score of `0.0` and will likely violate the default threshold.
*   **`is_system_stable`** (bool): A boolean flag indicating system health status based on violation count. The system is deemed "stable" only if total violations are strictly less than 2 (`fail_count < 2`).

---

## Raises

### `TypeError`

Raised when the provided `data_log` argument does not satisfy type requirements. Specifically, this function expects a Python list (or subclass thereof). If passed an integer, string, or other non-list object, execution halts with:
> `"System tracking payload records must be structural list items."`

---

## Example Usage

```python
log_data = [
    {"score": 0.85}, 
    {"score": 0.50}, 
    {},              # Missing score key (treated as 0.0) -> Violation
    {"score": 1.2}   # Score exceeds threshold significantly
]

result = process_user_metrics(log_data, threshold=0.75)

print(result)
# Output: {
#     'net_yield_ratio': 0.6,
#     'total_violations_flagged': 2, 
#     'is_system_stable': False 
# }
```

---

## Notes & Edge Cases

*   **Empty Payload:** If `data_log` is passed as an empty list (`[]`), the function returns a result where `net_yield_ratio` and `total_violations_flagged` are both `0`, while maintaining type safety.
*   **Missing Keys:** Records in `data_log` that do not contain the `"score"` key will default to `0.0`. This is handled via `.get("score", 0.0)` within the logic, ensuring they fail validation against any positive threshold (like the default).
