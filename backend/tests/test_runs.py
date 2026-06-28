from yfjz.runs.aggregation import aggregate_case_results
from yfjz.runs.service import RunService
from yfjz.storage.models import CaseResultRecord
from yfjz.storage.repositories import Repository


class FakeProvider:
    def __init__(self, repository: Repository, run_id_holder: dict[str, int]) -> None:
        self.repository = repository
        self.run_id_holder = run_id_holder

    async def complete(self, config, model, prompt, temperature, max_tokens):
        run_id = self.run_id_holder["run_id"]
        statuses = [row.status for row in self.repository.list_case_results(run_id)]
        assert "running" in statuses
        from yfjz.providers.base import ProviderResult

        return ProviderResult(output="2", raw_response='{"ok": true}', latency_ms=10)


def test_run_aggregation_counts_statuses_and_latency() -> None:
    rows = [
        CaseResultRecord(
            id=1,
            run_id=1,
            case_id="a",
            status="passed",
            prompt="p",
            expected="x",
            output="x",
            raw_response=None,
            score=1,
            reason="ok",
            latency_ms=100,
            cache_hit=True,
            error_message=None,
            created_at="now",
            updated_at="now",
        ),
        CaseResultRecord(
            id=2,
            run_id=1,
            case_id="b",
            status="failed",
            prompt="p",
            expected="x",
            output="y",
            raw_response=None,
            score=0,
            reason="no",
            latency_ms=300,
            cache_hit=False,
            error_message=None,
            created_at="now",
            updated_at="now",
        ),
        CaseResultRecord(
            id=3,
            run_id=1,
            case_id="c",
            status="error",
            prompt="p",
            expected="x",
            output=None,
            raw_response=None,
            score=0,
            reason="error",
            latency_ms=None,
            cache_hit=False,
            error_message="boom",
            created_at="now",
            updated_at="now",
        ),
    ]

    aggregate = aggregate_case_results(rows, total_cases=3)

    assert aggregate.completed_cases == 3
    assert aggregate.passed_cases == 1
    assert aggregate.failed_cases == 1
    assert aggregate.error_cases == 1
    assert aggregate.score == 0.5
    assert aggregate.average_latency_ms == 200
    assert aggregate.cache_hit_count == 1


def test_run_service_precreates_pending_cases_and_updates_statuses(db_path) -> None:
    import asyncio
    from yfjz.core.config import reset_settings_cache
    from yfjz.storage.database import init_db

    reset_settings_cache()
    init_db()
    repository = Repository()
    provider = repository.create_provider_config(
        {
            "name": "local",
            "base_url": "https://example.test/v1",
            "api_key": "sk-secretabcd",
            "default_model": "gpt-test",
            "timeout_seconds": 5,
            "max_retries": 0,
        }
    )
    suite = repository.create_suite(
        {
            "name": "math",
            "description": "",
            "prompt_template": "{{ question }}",
            "evaluation": {"type": "exact_match", "expected_field": "answer"},
            "cases": [{"id": "case_1", "question": "1+1", "answer": "2"}],
        }
    )
    run_id_holder: dict[str, int] = {}
    service = RunService(repository, FakeProvider(repository, run_id_holder))

    run = service.create_run(
        {
            "suite_id": suite.id,
            "provider_config_id": provider.id,
            "model": "gpt-test",
            "temperature": 0,
            "max_tokens": 8,
            "concurrency": 1,
            "use_cache": False,
        }
    )
    run_id_holder["run_id"] = run.id

    pending = repository.list_case_results(run.id)
    assert [row.status for row in pending] == ["pending"]

    asyncio.run(service.execute_run(run.id))

    completed = repository.list_case_results(run.id)
    assert [row.status for row in completed] == ["passed"]


def test_run_service_records_top_level_error_message(db_path) -> None:
    import asyncio
    from yfjz.core.config import reset_settings_cache
    from yfjz.storage.database import init_db

    reset_settings_cache()
    init_db()
    repository = Repository()
    provider = repository.create_provider_config(
        {
            "name": "local",
            "base_url": "https://example.test/v1",
            "api_key": "sk-secretabcd",
            "default_model": "gpt-test",
            "timeout_seconds": 5,
            "max_retries": 0,
        }
    )
    suite = repository.create_suite(
        {
            "name": "math",
            "description": "",
            "prompt_template": "{{ question }}",
            "evaluation": {"type": "exact_match", "expected_field": "answer"},
            "cases": [{"id": "case_1", "question": "1+1", "answer": "2"}],
        }
    )
    service = RunService(repository, FakeProvider(repository, {}))
    run = service.create_run(
        {
            "suite_id": suite.id,
            "provider_config_id": provider.id,
            "model": "gpt-test",
            "temperature": 0,
            "max_tokens": 8,
            "concurrency": 1,
            "use_cache": False,
        }
    )

    repository.delete_provider_config(provider.id)
    asyncio.run(service.execute_run(run.id))

    failed_run = repository.get_run(run.id)
    assert failed_run.status == "failed"
    assert "provider config not found" in failed_run.error_message
