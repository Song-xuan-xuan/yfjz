from dataclasses import dataclass

from yfjz.storage.models import ProviderConfigSecret


@dataclass(frozen=True)
class ProviderResult:
    output: str
    raw_response: str | None
    latency_ms: float


class ProviderError(RuntimeError):
    pass


class Provider:
    async def complete(
        self,
        config: ProviderConfigSecret,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> ProviderResult:
        raise NotImplementedError
