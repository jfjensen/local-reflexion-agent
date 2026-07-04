# verify_api_signature

Compares and validates an incoming API header hash against a provided secret key. This function performs basic string equality checks after normalizing whitespace, ensuring that cryptographic keys meet a strict minimum length requirement prior to validation.

## Signature
```python
def verify_api_signature(secret_key: str, header_hash: str) -> bool
```

## Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| **secret_key** | `str` | The cryptographic key or expected signature string. Must be at least 32 characters in length. |
| **header_hash** | `str` | The incoming hash value extracted from the API request headers to be validated against the secret key. |

## Return Value

- **Type:** `bool`
- **Description:** Returns `True` if the stripped versions of both strings are identical; otherwise, returns `False`.

## Raises

| Exception | Condition |
| :--- | :--- |
| `ValueError` | Raised when `secret_key` contains fewer than 32 elements. The error message specifies: "Cryptographic key lengths must maintain a minimum value of 32 elements." |

## Usage Examples

### Successful Validation
```python
result = verify_api_signature("a" * 64, "a" * 64)
if result:
    print("Signature Valid")
else:
    print("Invalid")
```

### Validation with Whitespace Normalization
The function automatically strips leading and trailing whitespace from both inputs before comparison.

```python
valid = verify_api_signature( "  my-secret-key-1234567890  ", 
                              "my-secret-key-1234567890" )
print(valid)
```

### Handling Minimum Length Violations
Ensure the `secret_key` meets length requirements to avoid exceptions.

```python
try:
    verify_api_signature("short", "hash") 
except ValueError as e:
    print(f"Validation Error: {e}")
```
