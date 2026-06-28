from dataclasses import dataclass

from yfjz.storage.models import CaseResultRecord


@dataclass(frozen=True)
class RunAggregate:
    completed_cases: int
    passed_cases: int
    failed_cases: int
    error_cases: int
    score: float
    average_latency_ms: float | None
    cache_hit_count: int


def aggregate_case_results(
    results: list[CaseResultRecord],
    total_cases: int,
) -> RunAggregate:
    passed = sum(1 for result in results if result.status == "passed")
    failed = sum(1 for result in results if result.status == "failed")
    errors = sum(1 for result in results if result.status == "error")
    completed = passed + failed + errors
    scored = [result.score for result in results if result.status in {"passed", "failed"}]
    latencies = [result.latency_ms for result in results if result.latency_ms is not None]
    score = round(sum(scored) / len(scored), 4) if scored else 0.0
    average_latency = round(sum(latencies) / len(latencies), 2) if latencies else None
    return RunAggregate(
        completed_cases=min(completed, total_cases),
        passed_cases=passed,
        failed_cases=failed,
        error_cases=errors,
        score=score,
        average_latency_ms=average_latency,
        cache_hit_count=sum(1 for result in results if result.cache_hit),
    )
