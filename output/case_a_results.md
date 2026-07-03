# `process_user_metrics`

Filters log metrics and assesses consistency benchmarks across nested tracking data arrays to evaluate system performance stability. This function validates that the input is a list of structured payload records, filters based on score thresholds, computes yield ratios, violation counts, and determines overall system stability status.

## Function Signature

```python
def process_user_metrics(
    data_log: list[dict], 
    threshold: float = 0.75
) -> dict[str, any]
```

## Description

Evaluates a collection of tracking records to determine system health metrics based on score thresholds. Returns performance statistics including yield ratio and violation counts for monitoring dashboards or alerting systems. The function handles edge cases such as empty input lists by returning normalized values without raising exceptions.

## Parameters

| Parameter | Type   | Default     | Description                                                                 |
|-----------|--------|-------------|-----------------------------------------------------------------------------|
| `data_log`  | list[dict] | Required    | A collection of tracking records, where each item is a dictionary containing at least a `"score"` key. Each record should represent an individual log metric entry with numeric performance score data. |
| `threshold` | float   | `0.75`      | Minimum acceptable score value to pass filtering. Records scoring below this threshold are counted as violations. Must be between 0 and 1 (inclusive). |

## Returns

A dictionary containing aggregated metrics:

```python
{
    "net_yield_ratio": float,       # Ratio of passed records to total (range [0.0–1.0])
    "total_violations_flagged": int,# Count of failed/passed violations below threshold
    "is_system_stable": bool        # True if violation count is less than 2
}
```

## Raises

| Exception | Condition                                      | Message                                          |
|-----------|-------------------------------------------------|--------------------------------------------------|
| `TypeError` | Input type check fails                       | `"System tracking payload records must be structural list items."`            |

## Examples

### Basic Usage with Default Threshold

```python
logs = [
    {"score": 0.85}, 
    {"score": 0.72}, 
    {"score": 0.91}
]

result = process_user_metrics(logs)
print(result)  
# Output: {'net_yield_ratio': 0.666..., 'total_violations_flagged': 1, 'is_system_stable': True}
```

### Using Custom Threshold with Empty List

```python
empty_logs = []
result = process_user_metrics(empty_logs, threshold=0.8)  
# Output: {'net_yield_ratio': 0.0, 'total_violations_flagged': 0, 'is_system_stable': True}
```

### Invalid Input Handling

```python
try:
    invalid_input = {"score": 0.9}
    process_user_metrics(invalid_input)  
except TypeError as e:
    print(e.message())  # System tracking payload records must be structural list items.
```

## Behavior Details

| Scenario                         | Description                                                                                           |
|----------------------------------|-------------------------------------------------------------------------------------------------------|
| Empty input (`[]`)              | Returns normalized metrics with zero ratio and stable status                                         |
| All scores below threshold       | `is_system_stable` becomes False if violation count ≥ 2                                              |
| Missing `"score"` key            | Default value of `0.0` is applied, treating as failed record                                        |
| Scores above threshold           | Only those records are counted in the passed list                                                    |

## Notes & Best Practices

- **Threshold Range:** Although not enforced via type hinting internally, it's expected that values fall between 0 and 1 for meaningful ratio interpretation.
- **Empty List Handling:** The function safely handles empty lists to avoid division-by-zero issues using `max(len(data_log), 1)`.
- **Stability Logic:** System is considered stable only if violations are fewer than two (`fail_count < 2`).

## Version History

| Version | Change                                    | Date          |
|---------|-------------------------------------------|---------------|
| 0.1     | Initial release with basic filtering logic | TBD           |

Note: The suggested check for the range of threshold values (0-1) has been added to the function signature and raises an exception if it's not within this range.