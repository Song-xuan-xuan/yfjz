import json

from yfjz.core.config import get_settings
from yfjz.core.secrets import decrypt_secret, mask_api_key
from yfjz.storage.models import (
    CaseResultRecord,
    ProviderConfigPublic,
    ProviderConfigSecret,
    RunRecord,
    SuiteRecord,
)


def provider_public(row) -> ProviderConfigPublic:
    api_key = decrypt_secret(row["api_key_encrypted"], get_settings().secret_key)
    return ProviderConfigPublic(
        id=row["id"],
        name=row["name"],
        base_url=row["base_url"],
        api_key_masked=mask_api_key(api_key),
        default_model=row["default_model"],
        timeout_seconds=row["timeout_seconds"],
        max_retries=row["max_retries"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def provider_secret(row) -> ProviderConfigSecret:
    api_key = decrypt_secret(row["api_key_encrypted"], get_settings().secret_key)
    return ProviderConfigSecret(
        id=row["id"],
        name=row["name"],
        base_url=row["base_url"],
        api_key=api_key,
        default_model=row["default_model"],
        timeout_seconds=row["timeout_seconds"],
        max_retries=row["max_retries"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def suite_record(row) -> SuiteRecord:
    return SuiteRecord(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        prompt_template=row["prompt_template"],
        evaluation=json.loads(row["evaluation_json"]),
        cases=json.loads(row["cases_json"]),
        suite_json=json.loads(row["suite_json"]),
        created_at=row["created_at"],
    )


def run_record(row) -> RunRecord:
    return RunRecord(
        id=row["id"],
        status=row["status"],
        suite_id=row["suite_id"],
        provider_config_id=row["provider_config_id"],
        model=row["model"],
        temperature=row["temperature"],
        max_tokens=row["max_tokens"],
        concurrency=row["concurrency"],
        use_cache=bool(row["use_cache"]),
        total_cases=row["total_cases"],
        completed_cases=row["completed_cases"],
        passed_cases=row["passed_cases"],
        failed_cases=row["failed_cases"],
        error_cases=row["error_cases"],
        score=row["score"],
        average_latency_ms=row["average_latency_ms"],
        cache_hit_count=row["cache_hit_count"],
        error_message=row["error_message"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def case_result(row) -> CaseResultRecord:
    return CaseResultRecord(
        id=row["id"],
        run_id=row["run_id"],
        case_id=row["case_id"],
        status=row["status"],
        prompt=row["prompt"],
        expected=row["expected"],
        output=row["output"],
        raw_response=row["raw_response"],
        score=row["score"],
        reason=row["reason"],
        latency_ms=row["latency_ms"],
        cache_hit=bool(row["cache_hit"]),
        error_message=row["error_message"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
