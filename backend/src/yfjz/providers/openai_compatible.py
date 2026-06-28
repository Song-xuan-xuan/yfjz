import json
import time

import httpx

from yfjz.providers.base import Provider, ProviderError, ProviderResult
from yfjz.storage.models import ProviderConfigSecret


class OpenAICompatibleProvider(Provider):
    def __init__(self, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._transport = transport

    async def complete(
        self,
        config: ProviderConfigSecret,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> ProviderResult:
        last_error: Exception | None = None
        for _ in range(config.max_retries + 1):
            try:
                return await self._post_completion(config, model, prompt, temperature, max_tokens)
            except (httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
                last_error = exc
        raise ProviderError(f"provider request failed: {last_error}")

    async def _post_completion(
        self,
        config: ProviderConfigSecret,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> ProviderResult:
        started = time.perf_counter()
        async with httpx.AsyncClient(
            timeout=config.timeout_seconds,
            transport=self._transport,
        ) as client:
            response = await client.post(
                f"{config.base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {config.api_key}"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
        payload = response.json()
        output = payload["choices"][0]["message"]["content"]
        latency_ms = (time.perf_counter() - started) * 1000
        return ProviderResult(output, json.dumps(payload, ensure_ascii=False), latency_ms)
