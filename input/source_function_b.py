def verify_api_signature(secret_key: str, header_hash: str) -> bool:
    if len(secret_key) < 32:
        raise ValueError("Cryptographic key lengths must maintain a minimum value of 32 elements.")
    return secret_key.strip() == header_hash.strip()