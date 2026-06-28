from dataclasses import asdict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from yfjz.providers.openai_compatible import OpenAICompatibleProvider
from yfjz.storage.repositories import Repository


router = APIRouter(prefix="/provider-configs", tags=["provider-configs"])


class ProviderConfigIn(BaseModel):
    name: str = Field(min_length=1)
    base_url: str = Field(min_length=1)
    api_key: str = Field(min_length=1)
    default_model: str = Field(min_length=1)
    timeout_seconds: int = Field(default=60, ge=1)
    max_retries: int = Field(default=2, ge=0)


class ProviderConfigUpdate(ProviderConfigIn):
    api_key: str | None = None


@router.get("")
def list_provider_configs() -> list[dict]:
    return [asdict(item) for item in Repository().list_provider_configs()]


@router.post("")
def create_provider_config(payload: ProviderConfigIn) -> dict:
    created = Repository().create_provider_config(payload.model_dump())
    return asdict(created)


@router.put("/{config_id}")
def update_provider_config(config_id: int, payload: ProviderConfigUpdate) -> dict:
    updated = Repository().update_provider_config(config_id, payload.model_dump())
    return asdict(updated)


@router.delete("/{config_id}")
def delete_provider_config(config_id: int) -> dict[str, bool]:
    Repository().delete_provider_config(config_id)
    return {"deleted": True}


@router.post("/{config_id}/test")
async def test_provider_config(config_id: int) -> dict:
    repository = Repository()
    config = repository.get_provider_config_secret(config_id)
    try:
        result = await OpenAICompatibleProvider().complete(
            config=config,
            model=config.default_model,
            prompt="ping",
            temperature=0,
            max_tokens=8,
        )
    except Exception as exc:
        return {"ok": False, "message": str(exc)}
    return {"ok": True, "message": "provider responded", "latency_ms": result.latency_ms}
