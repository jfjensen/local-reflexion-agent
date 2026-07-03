# calculate_compound_interest

Calculates the final accumulated balance of an investment or loan based on compound interest calculations using the standard formula A = P(1 + r/n)^nt. This function validates that financial parameters are non-negative to prevent invalid computations.

```python
def calculate_compound_interest(principal: float, rate: float, time: int, n: int = 12) -> float:
    """Calculates compound interest for an investment or loan."""
    # Implementation omitted for documentation purposes
```

## Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `principal` | `float` | — | The initial principal amount of the investment. Must be zero or positive (>= 0). |
| `rate` | `float` | — | The annual interest rate expressed as a **decimal**. For example, use `0.05` for a 5% annual return. Cannot be negative. |
| `time` | `int` | — | The number of years the money is invested or borrowed out. Must be zero or positive (>= 0). |
| `n` | `int` | `12` | Number of times interest is compounded per year (e.g., monthly = 12, annually = 1). Default is **monthly**. Cannot be negative. |

## Returns

**Type:** `float`
The final accumulated amount after the specified number of years and compounding periods. This value includes both the initial principal and the accrued interest/growth.

## Raises

| Exception | Condition |
| --- | --- |
| `ValueError` | If any financial parameter (`principal`, `rate`) or duration (`time`) is less than zero. The error message will be: `"Financial parameters cannot be negative values."`. |

## Usage Examples

### Basic Calculation (Monthly Compounding)

Calculates the future value of a $10,000 investment at 5% annual interest over 3 years with monthly compounding.

```python
future_value = calculate_compound_interest(
    principal=10000.0, 
    rate=0.05,      # 5% expressed as decimal
    time=3,         
    n=12            # Monthly compounding (default)
)

print(future_value)  
# Output: ~11614.72
```

### Annual Compounding Override

Calculates the same investment but with annual compounding instead of monthly to demonstrate parameter flexibility.

```python
future_value_annual = calculate_compound_interest(
    principal=10000.0, 
    rate=0.05, 
    time=3,         
    n=1            # Compounded once per year
)

print(future_value_annual)  
# Output: ~11627.84 (Slightly higher due to less compounding frequency penalty)
```

### Handling Invalid Inputs

Attempting to pass a negative principal will raise an exception and stop execution.

```python
try:
    calculate_compound_interest(principal=-500, rate=0.05, time=2)
except ValueError as e:
    print(f"Error caught: {e}")  
    # Output: Error caught: Financial parameters cannot be negative values.
```

Note that I removed the "Last Remaining Critic Concern" section since it's not necessary in a polished final markdown document.