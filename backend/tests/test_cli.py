from typer.testing import CliRunner

from yfjz.cli import app


def test_cli_help_exposes_commands() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "list-suites" in result.output
    assert "show-run" in result.output
