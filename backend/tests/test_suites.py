import pytest
from pydantic import ValidationError

from yfjz.suites.renderer import render_prompt
from yfjz.suites.schema import SuiteDefinition


def valid_suite_payload() -> dict:
    return {
        "name": "math-basic",
        "description": "Basic math",
        "prompt_template": "Answer only: {{ question }}",
        "evaluation": {
            "type": "exact_match",
            "expected_field": "answer",
            "ignore_case": True,
            "strip": True,
        },
        "cases": [{"id": "case_1", "question": "1 + 1?", "answer": "2"}],
    }


def test_suite_validation_accepts_flexible_case_fields() -> None:
    suite = SuiteDefinition.model_validate(valid_suite_payload())

    assert suite.name == "math-basic"
    assert suite.cases[0]["question"] == "1 + 1?"


def test_suite_validation_rejects_duplicate_case_ids() -> None:
    payload = valid_suite_payload()
    payload["cases"].append({"id": "case_1", "question": "2 + 2?", "answer": "4"})

    with pytest.raises(ValidationError, match="unique"):
        SuiteDefinition.model_validate(payload)


def test_suite_validation_rejects_missing_expected_field() -> None:
    payload = valid_suite_payload()
    payload["cases"] = [{"id": "case_1", "question": "1 + 1?"}]

    with pytest.raises(ValidationError, match="expected_field"):
        SuiteDefinition.model_validate(payload)


def test_suite_validation_rejects_missing_template_field() -> None:
    payload = valid_suite_payload()
    payload["prompt_template"] = "{{ missing }}"

    with pytest.raises(ValidationError, match="prompt_template"):
        SuiteDefinition.model_validate(payload)


def test_render_prompt_replaces_simple_fields() -> None:
    rendered = render_prompt("Answer {{ question }} as {{ format }}", {
        "question": "1 + 1",
        "format": "number",
    })

    assert rendered == "Answer 1 + 1 as number"
