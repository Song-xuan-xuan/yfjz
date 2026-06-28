import asyncio
import json
from dataclasses import asdict

import typer

from yfjz.runs.service import RunService
from yfjz.storage.database import init_db
from yfjz.storage.repositories import Repository


app = typer.Typer(help="yfjz backend CLI")


@app.command("list-suites")
def list_suites() -> None:
    init_db()
    rows = [asdict(suite) for suite in Repository().list_suites()]
    typer.echo(json.dumps(rows, ensure_ascii=False, indent=2))


@app.command("run")
def run_suite(
    suite_id: int = typer.Option(..., "--suite-id"),
    provider_config_id: int = typer.Option(..., "--provider-config-id"),
    model: str = "",
    temperature: float = 0,
    max_tokens: int = 512,
    concurrency: int = 3,
    use_cache: bool = True,
) -> None:
    init_db()
    service = RunService()
    run = service.create_run(
        {
            "suite_id": suite_id,
            "provider_config_id": provider_config_id,
            "model": model or None,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "concurrency": concurrency,
            "use_cache": use_cache,
        }
    )
    asyncio.run(service.execute_run(run.id))
    typer.echo(json.dumps(asdict(service.refresh_progress(run.id)), ensure_ascii=False))


@app.command("show-run")
def show_run(run_id: int) -> None:
    init_db()
    run = RunService().refresh_progress(run_id)
    results = [asdict(row) for row in Repository().list_case_results(run_id)]
    typer.echo(json.dumps({"run": asdict(run), "results": results}, ensure_ascii=False, indent=2))


def main() -> None:
    app()
