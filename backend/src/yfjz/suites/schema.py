import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


PLACEHOLDER_PATTERN = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*}}")


class EvaluationConfig(BaseModel):
    type: Literal["exact_match", "contains", "regex_match"]
    expected_field: str = Field(min_length=1)

    model_config = ConfigDict(extra="allow")


class SuiteDefinition(BaseModel):
    name: str = Field(min_length=1)
    description: str = ""
    prompt_template: str = Field(min_length=1)
    evaluation: EvaluationConfig
    cases: list[dict[str, Any]] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_cases(self) -> "SuiteDefinition":
        self._validate_case_ids()
        self._validate_expected_field()
        self._validate_template_fields()
        return self

    def _validate_case_ids(self) -> None:
        ids = [case.get("id") for case in self.cases]
        if any(case_id in (None, "") for case_id in ids):
            raise ValueError("each case must include a non-empty id")
        if len(ids) != len(set(ids)):
            raise ValueError("case ids must be unique")

    def _validate_expected_field(self) -> None:
        field = self.evaluation.expected_field
        for case in self.cases:
            if field not in case:
                raise ValueError(f"expected_field '{field}' missing in case {case.get('id')}")

    def _validate_template_fields(self) -> None:
        fields = PLACEHOLDER_PATTERN.findall(self.prompt_template)
        for case in self.cases:
            missing = [field for field in fields if field not in case]
            if missing:
                raise ValueError(f"prompt_template fields missing in case {case.get('id')}: {missing}")
