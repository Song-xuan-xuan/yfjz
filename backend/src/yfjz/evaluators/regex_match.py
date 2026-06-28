import re
from typing import Any

from yfjz.evaluators.base import EvaluationResult


class RegexMatchEvaluator:
    def evaluate(self, expected: str, output: str, options: dict[str, Any]) -> EvaluationResult:
        try:
            passed = re.search(expected, output) is not None
        except re.error as exc:
            return EvaluationResult(0.0, False, f"invalid regex: {exc}")
        return EvaluationResult(
            score=1.0 if passed else 0.0,
            passed=passed,
            reason="regex matched" if passed else "regex did not match output",
        )
