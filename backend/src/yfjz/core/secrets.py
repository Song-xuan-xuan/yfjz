import base64
from itertools import cycle


def _xor_bytes(value: bytes, secret: str) -> bytes:
    key = secret.encode("utf-8") or b"local"
    return bytes(byte ^ key_byte for byte, key_byte in zip(value, cycle(key)))


def encrypt_secret(value: str, secret: str) -> str:
    encrypted = _xor_bytes(value.encode("utf-8"), secret)
    return base64.urlsafe_b64encode(encrypted).decode("ascii")


def decrypt_secret(value: str, secret: str) -> str:
    decoded = base64.urlsafe_b64decode(value.encode("ascii"))
    return _xor_bytes(decoded, secret).decode("utf-8")


def mask_api_key(api_key: str) -> str:
    if not api_key:
        return ""
    if api_key.startswith("sk-") and len(api_key) >= 7:
        return f"sk-****{api_key[-4:]}"
    if len(api_key) <= 4:
        return "****"
    return f"****{api_key[-4:]}"
