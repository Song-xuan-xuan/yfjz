from typing import Any

from yfjz.providers.base import Provider
from yfjz.providers.openai_compatible import OpenAICompatibleProvider
from yfjz.runs.aggregation import aggregate_case_results
from yfjz.runs.executor import RunExecutor
from yfjz.suites.renderer import render_prompt
from yfjz.storage.models import RunRecord
from yfjz.storage.repositories import Repository


class RunService:
    def __init__(
        self,
        repository: Repository | None = None,
        provider: Provider | None = None,
    ) -> None:
        self.repository = repository or Repository()
        self.provider = provider or OpenAICompatibleProvider()

    def create_run(self, data: dict[str, Any]) -> RunRecord:
        suite = self.repository.get_suite(data["suite_id"])
        self.repository.get_provider_config(data["provider_config_id"])
        model = data.get("model") or self.repository.get_provider_config(data["provider_config_id"]).default_model
        run_data = {**data, "model": model}
        run = self.repository.create_run(run_data, total_cases=len(suite.cases))
        self._create_pending_case_results(run.id, suite)
        return run

    async def execute_run(self, run_id: int) -> None:
        try:
            executor = RunExecutor(self.repository, self.provider)
            await executor.execute(run_id)
            self._refresh_aggregate(run_id, final_status="completed")
        except Exception as exc:
            self._refresh_aggregate(run_id, final_status="failed", error_message=str(exc))

    def _create_pending_case_results(self, run_id: int, suite) -> None:
        expected_field = suite.evaluation["expected_field"]
        for case in suite.cases:
            self.repository.create_case_result(
                {
                    "run_id": run_id,
                    "case_id": str(case["id"]),
                    "status": "pending",
                    "prompt": render_prompt(suite.prompt_template, case),
                    "expected": str(case[expected_field]),
                    "score": 0,
                    "reason": "",
                }
            )

    def _refresh_aggregate(
        self,
        run_id: int,
        final_status: str | None = None,
        error_message: str | None = None,
    ) -> RunRecord:
        run = self.repository.get_run(run_id)
        results = self.repository.list_case_results(run_id)
        aggregate = aggregate_case_results(results, run.total_cases)
        fields = aggregate.__dict__
        if final_status is not None:
            fields["status"] = final_status
        if error_message is not None:
            fields["error_message"] = error_message
        return self.repository.update_run(run_id, **fields)

    def refresh_progress(self, run_id: int) -> RunRecord:
        return self._refresh_aggregate(run_id)
