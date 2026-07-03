# verify_api_signature

Validates the identity of an incoming API client by comparing a shared cryptographic secret key against a hash value provided in HTTP request headers.

## Signature

```python
def verify_api_signature(secret_key: str, header_hash: str) -> bool
```

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `secret_key` | `str` | Yes | The server-side shared secret string used to authenticate the client. This key is expected to be at least **32 characters** long; shorter keys are rejected immediately as they do not meet security standards for entropy or collision resistance in this implementation context. Whitespace included here counts toward the length check but will be stripped during final comparison against the header hash. |
| `header_hash` | `str` | Yes | The cryptographic value extracted from incoming request headers (e.g., `X-API-Signature`). This represents the expected signature or token that must match your stored secret exactly to grant access. Whitespace is automatically trimmed before equality validation occurs, allowing for flexible header formatting without compromising security logic. |

## Returns

**Type:** `bool`

*   **Description**: Signals the result of the identity verification process.
    *   `True`: Authentication successful. The normalized (stripped) contents of `secret_key` match exactly with the normalized `header_hash`. The request is authorized to proceed to downstream logic.
    *   `False`: Authentication failed. Even after removing leading or trailing whitespace from both inputs, a mismatch was detected between the provided key and header hash. Access should be denied at this point in the call stack.

## Raises

**`ValueError`**

A `ValueError` is raised if the input parameters violate safety constraints prior to the signature comparison step. This prevents weak keys from being used, which could lead to security vulnerabilities such as brute-force attacks or reduced entropy in key derivation processes.

| Condition | Message Description |
| :--- | :--- |
| Length < 32 characters | Raised immediately if `len(secret_key) < 32`. The error message specifies that cryptographic keys must maintain a minimum value of **32 elements**. Leading and trailing whitespace are counted toward this length check before any stripping operations occur. |

## Usage Example

This function is typically integrated into middleware layers (such as WSGI or ASGI application frameworks) to intercept incoming requests early in the lifecycle. The example below demonstrates how to validate a request signature within an authentication handler:

```python
from verify_api_signature import verify_api_signature

def handle_request(request):
    # Retrieve expected secret from secure environment configuration
    configured_secret = os.getenv("API_SECRET_KEY") 
    
    # Extract hash provided by client in headers (e.g., X-Signature)
    header_hash = request.headers.get('X-API-Hash', '')

    try:
        is_authenticated = verify_api_signature(configured_secret, header_hash)
        
        if is_authenticated:
            return process_business_logic(request) # Safe to proceed
        
        else:
            raise PermissionError("Invalid signature hash.")

    except ValueError as e:
        log_error(f"Key security violation: {e}") # Do not expose key details in logs
        return {"error": "Security check failed"}, 403
    
    except Exception:
        # Handle unexpected parsing errors gracefully
        return {"error": "Internal verification error"}, 500

# Direct testing logic (Avoid hardcoding secrets)
secret = "abcdefghijklmnopqrstuvwxyz123456"  
header_hash_from_request = "\n\t" + secret.strip()

if verify_api_signature(secret, header_hash_from_request):
    print("Signature Valid") 
else:
    print("Signature Invalid")
```