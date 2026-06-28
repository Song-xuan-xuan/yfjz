from typing import Any

from yfjz.evaluators.base import EvaluationResult
from yfjz.evaluators.contains import ContainsEvaluator
from yfjz.evaluators.exact_match import ExactMatchEvaluator
from yfjz.evaluators.regex_match import RegexMatchEvaluator


EVALUATORS = {
    "exact_match": ExactMatchEvaluator(),
    "contains": ContainsEvaluator(),
    "regex_match": RegexMatchEvaluator(),
}


def evaluate(
    evaluator_type: str,
    expected: str,
    output: str,
    options: dict[str, Any],
) -> EvaluationResult:
    evaluator = EVALUATORS[evaluator_type]
    return evaluator.evaluate(expected, output, options)
