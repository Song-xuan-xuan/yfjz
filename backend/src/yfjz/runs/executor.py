import asyncio
from dataclasses import asdict
from typing import Any

from yfjz.evaluators.registry import evaluate
from yfjz.providers.base import Provider
from yfjz.suites.renderer import render_prompt
from yfjz.storage.repositories import Repository
from yfjz.tools.cache import build_cache_key


class RunExecutor:
    def __init__(self, repository: Repository, provider: Provider) -> None:
        self.repository = repository
        self.provider = provider

    async def execute(self, run_id: int) -> None:
        run = self.repository.get_run(run_id)
        suite = self.repository.get_suite(run.suite_id)
        config = self.repository.get_provider_config_secret(run.provider_config_id)
        self.repository.update_run(run_id, status="running")
        semaphore = asyncio.Semaphore(run.concurrency)
        tasks = [self._guarded_case(run_id, suite, config, case, semaphore) for case in suite.cases]
        await asyncio.gather(*tasks)

    async def _guarded_case(self, run_id: int, suite, config, case: dict[str, Any], semaphore) -> None:
        async with semaphore:
            try:
                await self._execute_case(run_id, suite, config, case)
            except Exception as exc:
                self._save_error(run_id, suite, case, str(exc))

    async def _execute_case(self, run_id: int, suite, config, case: dict[str, Any]) -> None:
        run = self.repository.get_run(run_id)
        prompt = render_prompt(suite.prompt_template, case)
        expected = str(case[suite.evaluation["expected_field"]])
        case_id = str(case["id"])
        self.repository.update_case_result(run_id, case_id, status="running")
        output, raw, latency, cache_hit = await self._get_output(run, config, prompt)
        result = evaluate(suite.evaluation["type"], expected, output, suite.evaluation)
        self.repository.update_case_result(
            run_id,
            case_id,
            status="passed" if result.passed else "failed",
            output=output,
            raw_response=raw,
            score=result.score,
            reason=result.reason,
            latency_ms=latency,
            cache_hit=cache_hit,
        )

    async def _get_output(self, run, config, prompt: str) -> tuple[str, str | None, float | None, bool]:
        cache_key = build_cache_key(run.provider_config_id, run.model, prompt, run.temperature, run.max_tokens)
        cached = self.repository.get_cache(cache_key) if run.use_cache else None
        if cached is not None:
            return cached.output, cached.raw_response, None, True
        result = await self.provider.complete(config, run.model, prompt, run.temperature, run.max_tokens)
        self.repository.set_cache(cache_key, {**asdict(run), "rendered_prompt": prompt, **asdict(result)})
        return result.output, result.raw_response, result.latency_ms, False

    def _save_error(self, run_id: int, suite, case: dict[str, Any], message: str) -> None:
        prompt = render_prompt(suite.prompt_template, case)
        expected = str(case.get(suite.evaluation["expected_field"], ""))
        self.repository.update_case_result(
            run_id,
            str(case.get("id", "")),
            status="error",
            prompt=prompt,
            expected=expected,
            score=0,
            reason="case error",
            error_message=message,
        )
