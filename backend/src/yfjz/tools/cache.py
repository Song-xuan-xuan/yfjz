import hashlib
import json


def build_cache_key(
    provider_config_id: int,
    model: str,
    rendered_prompt: str,
    temperature: float,
    max_tokens: int,
) -> str:
    payload = {
        "provider_config_id": provider_config_id,
        "model": model,
        "rendered_prompt": rendered_prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
