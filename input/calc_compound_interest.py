def calculate_compound_interest(principal: float, rate: float, time: int, n: int = 12) -> float:
    if principal < 0 or rate < 0 or time < 0:
        raise ValueError("Financial parameters cannot be negative values.")
    return principal * (1 + (rate / n)) ** (n * time)