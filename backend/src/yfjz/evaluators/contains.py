from typing import Any

from yfjz.evaluators.base import EvaluationResult, normalize


class ContainsEvaluator:
    def evaluate(self, expected: str, output: str, options: dict[str, Any]) -> EvaluationResult:
        passed = normalize(expected, options) in normalize(output, options)
        return EvaluationResult(
            score=1.0 if passed else 0.0,
            passed=passed,
            reason="contains expected value" if passed else "output did not contain expected value",
        )
