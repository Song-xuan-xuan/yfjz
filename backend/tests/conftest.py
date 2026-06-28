from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def db_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "test.sqlite3"
    monkeypatch.setenv("YFJZ_DATABASE_PATH", str(path))
    monkeypatch.setenv("YFJZ_SECRET_KEY", "test-secret")
    return path


@pytest.fixture()
def client(db_path: Path) -> Iterator[TestClient]:
    from yfjz.core.config import reset_settings_cache

    reset_settings_cache()
    from yfjz.app import create_app

    with TestClient(create_app()) as test_client:
        yield test_client
