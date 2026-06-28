import httpx
import pytest

from yfjz.providers.openai_compatible import OpenAICompatibleProvider
from yfjz.storage.models import ProviderConfigSecret


@pytest.mark.asyncio
async def test_openai_provider_posts_chat_completion_and_extracts_output() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "model answer"}}]},
        )

    provider = OpenAICompatibleProvider(transport=httpx.MockTransport(handler))
    config = ProviderConfigSecret(
        id=1,
        name="local",
        base_url="https://example.test/v1",
        api_key="sk-test",
        default_model="default-model",
        timeout_seconds=3,
        max_retries=0,
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
    )

    result = await provider.complete(
        config=config,
        model="gpt-test",
        prompt="Say hi",
        temperature=0.1,
        max_tokens=32,
    )

    assert result.output == "model answer"
    assert requests[0].url.path == "/v1/chat/completions"
    assert requests[0].headers["authorization"] == "Bearer sk-test"
    assert requests[0].read()
