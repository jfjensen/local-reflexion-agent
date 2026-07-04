# calculate_compound_interest

Calculates the future value of an investment based on compound interest principles using a standard mathematical formula: $A = P(1 + r/n)^{nt}$. This function computes the total accumulated amount, including principal and accrued interest.

## Function Signature

```python
def calculate_compound_interest(principal: float, rate: float, time: int, n: int = 12) -> float:
```

## Parameters

| Parameter | Type | Default | Description | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| **principal** | `float` | - | The initial investment amount (P). Must be a non-negative number. | ≥ 0 |
| **rate** | `float` | - | Annual interest rate in decimal format (e.g., $5\% = 0.05$, not `5`). Must be a non-negative number. | ≥ 0 |
| **time** | `int` | - | The duration of the investment period expressed in years. Must be a whole, non-negative integer. | ≥ 0 (Integer) |
| **n** | `int` | 12 | Number of times interest is compounded per year. Defaults to monthly compounding if not specified. Should typically be an integer greater than zero. | > 0 |

## Return Value

- **Type:** `float`
- **Description:** The total accumulated amount after the specified time period, including both the original principal and compounded interest.

## Raises

| Exception | Description | Trigger Condition |
| :--- | :--- | :--- |
| `ValueError` | Indicates that financial parameters provided are invalid. | Any of `principal`, `rate`, or `time` is negative ($< 0$). |

## Examples

```python
# Calculate interest compounded monthly using the default value (n=12) 
balance = calculate_compound_interest(principal=5000, rate=0.03, time=5) 
print(f"Total Balance: ${balance:.2f}") 

# Calculate annual compounding by explicitly setting n to 1
annually_balance = calculate_compound_interest(
    principal=10000, 
    rate=0.04, 
    time=10, 
    n=1  
)

print(f"Total Balance (Annual): ${annually_balance:.2f}") 

# Calculate quarterly compounding by explicitly setting n to 4
quarterly_balance = calculate_compound_interest(
    principal=5000, 
    rate=0.03, 
    time=10, 
    n=4  
)

print(f"Total Balance (Quarterly): ${quarterly_balance:.2f}")
```
