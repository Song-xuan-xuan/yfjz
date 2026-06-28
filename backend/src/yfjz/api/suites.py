from dataclasses import asdict

from fastapi import APIRouter
from pydantic import BaseModel

from yfjz.suites.schema import SuiteDefinition
from yfjz.storage.repositories import Repository


router = APIRouter(prefix="/suites", tags=["suites"])


class SuiteCreateRequest(BaseModel):
    suite: SuiteDefinition


def _suite_list_item(record) -> dict:
    return {
        "id": record.id,
        "name": record.name,
        "description": record.description,
        "case_count": len(record.cases),
        "metric_type": record.evaluation["type"],
        "created_at": record.created_at,
    }


@router.get("")
def list_suites() -> list[dict]:
    return [_suite_list_item(suite) for suite in Repository().list_suites()]


@router.post("")
def create_suite(payload: SuiteCreateRequest) -> dict:
    suite = payload.suite.model_dump()
    return asdict(Repository().create_suite(suite))


@router.get("/{suite_id}")
def get_suite(suite_id: int) -> dict:
    return asdict(Repository().get_suite(suite_id))


@router.delete("/{suite_id}")
def delete_suite(suite_id: int) -> dict[str, bool]:
    Repository().delete_suite(suite_id)
    return {"deleted": True}
