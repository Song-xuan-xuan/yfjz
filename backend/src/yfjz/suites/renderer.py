from typing import Any

from yfjz.core.errors import ValidationAppError
from yfjz.suites.schema import PLACEHOLDER_PATTERN


def render_prompt(template: str, case: dict[str, Any]) -> str:
    def replace(match) -> str:
        field_name = match.group(1)
        if field_name not in case:
            raise ValidationAppError(f"missing template field: {field_name}")
        return str(case[field_name])

    return PLACEHOLDER_PATTERN.sub(replace, template)
