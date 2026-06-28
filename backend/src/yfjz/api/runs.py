from dataclasses import asdict

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field

from yfjz.runs.service import RunService
from yfjz.storage.repositories import Repository


router = APIRouter(prefix="/runs", tags=["runs"])


class RunCreateRequest(BaseModel):
    suite_id: int
    provider_config_id: int
    model: str | None = None
    temperature: float = 0
    max_tokens: int = Field(default=512, ge=1)
    concurrency: int = Field(default=3, ge=1, le=10)
    use_cache: bool = True


async def _execute_run(run_id: int) -> None:
    await RunService().execute_run(run_id)


@router.get("")
def list_runs() -> list[dict]:
    return [asdict(run) for run in Repository().list_runs()]


@router.post("")
def create_run(payload: RunCreateRequest, background_tasks: BackgroundTasks) -> dict:
    run = RunService().create_run(payload.model_dump())
    background_tasks.add_task(_execute_run, run.id)
    return asdict(run)


@router.get("/{run_id}")
def get_run(run_id: int) -> dict:
    return asdict(RunService().refresh_progress(run_id))


@router.get("/{run_id}/results")
def get_run_results(run_id: int) -> list[dict]:
    Repository().get_run(run_id)
    return [asdict(result) for result in Repository().list_case_results(run_id)]
