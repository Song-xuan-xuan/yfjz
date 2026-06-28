from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class EvaluationResult:
    score: float
    passed: bool
    reason: str


class Evaluator(Protocol):
    def evaluate(self, expected: str, output: str, options: dict[str, Any]) -> EvaluationResult:
        ...


def normalize(value: str, options: dict[str, Any]) -> str:
    normalized = value.strip() if options.get("strip", False) else value
    return normalized.lower() if options.get("ignore_case", False) else normalized
