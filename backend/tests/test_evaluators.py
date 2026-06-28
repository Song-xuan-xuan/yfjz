from yfjz.evaluators.registry import evaluate


def test_exact_match_honors_strip_and_ignore_case() -> None:
    result = evaluate(
        "exact_match",
        expected="Answer",
        output=" answer ",
        options={"strip": True, "ignore_case": True},
    )

    assert result.score == 1
    assert result.passed is True


def test_contains_honors_strip_and_ignore_case() -> None:
    result = evaluate(
        "contains",
        expected="needle",
        output=" A NEEDLE is here ",
        options={"strip": True, "ignore_case": True},
    )

    assert result.score == 1
    assert result.passed is True


def test_regex_match_returns_error_result_for_invalid_regex() -> None:
    result = evaluate("regex_match", expected="[", output="anything", options={})

    assert result.score == 0
    assert result.passed is False
    assert "invalid regex" in result.reason
