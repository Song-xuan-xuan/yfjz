from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderConfigPublic:
    id: int
    name: str
    base_url: str
    api_key_masked: str
    default_model: str
    timeout_seconds: int
    max_retries: int
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ProviderConfigSecret:
    id: int
    name: str
    base_url: str
    api_key: str
    default_model: str
    timeout_seconds: int
    max_retries: int
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class SuiteRecord:
    id: int
    name: str
    description: str
    prompt_template: str
    evaluation: dict
    cases: list[dict]
    suite_json: dict
    created_at: str


@dataclass(frozen=True)
class RunRecord:
    id: int
    status: str
    suite_id: int
    provider_config_id: int
    model: str
    temperature: float
    max_tokens: int
    concurrency: int
    use_cache: bool
    total_cases: int
    completed_cases: int
    passed_cases: int
    failed_cases: int
    error_cases: int
    score: float
    average_latency_ms: float | None
    cache_hit_count: int
    error_message: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class CaseResultRecord:
    id: int
    run_id: int
    case_id: str
    status: str
    prompt: str
    expected: str
    output: str | None
    raw_response: str | None
    score: float
    reason: str
    latency_ms: float | None
    cache_hit: bool
    error_message: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class CacheRecord:
    cache_key: str
    output: str
    raw_response: str | None
    created_at: str
