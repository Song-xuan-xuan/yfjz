from datetime import UTC, datetime
from typing import Any

from yfjz.core.config import get_settings
from yfjz.core.errors import NotFoundError
from yfjz.core.secrets import encrypt_secret
from yfjz.storage.database import connect
from yfjz.storage.row_mappers import (
    case_result,
    provider_public,
    provider_secret,
    run_record,
    suite_record,
)
from yfjz.storage.models import (
    CacheRecord,
    CaseResultRecord,
    ProviderConfigPublic,
    ProviderConfigSecret,
    RunRecord,
    SuiteRecord,
)


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    import json

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class Repository:
    def create_provider_config(self, data: dict[str, Any]) -> ProviderConfigPublic:
        now = utc_now()
        encrypted = encrypt_secret(data["api_key"], get_settings().secret_key)
        with connect() as db:
            cursor = db.execute(
                """
                INSERT INTO provider_configs
                (name, base_url, api_key_encrypted, default_model, timeout_seconds,
                 max_retries, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["name"],
                    data["base_url"],
                    encrypted,
                    data["default_model"],
                    data["timeout_seconds"],
                    data["max_retries"],
                    now,
                    now,
                ),
            )
            created_id = cursor.lastrowid
        return self.get_provider_config(created_id)

    def list_provider_configs(self) -> list[ProviderConfigPublic]:
        with connect() as db:
            rows = db.execute("SELECT * FROM provider_configs ORDER BY id").fetchall()
        return [provider_public(row) for row in rows]

    def get_provider_config(self, config_id: int) -> ProviderConfigPublic:
        with connect() as db:
            row = db.execute(
                "SELECT * FROM provider_configs WHERE id = ?",
                (config_id,),
            ).fetchone()
        if row is None:
            raise NotFoundError("provider config not found")
        return provider_public(row)

    def get_provider_config_secret(self, config_id: int) -> ProviderConfigSecret:
        with connect() as db:
            row = db.execute(
                "SELECT * FROM provider_configs WHERE id = ?",
                (config_id,),
            ).fetchone()
        if row is None:
            raise NotFoundError("provider config not found")
        return provider_secret(row)

    def update_provider_config(self, config_id: int, data: dict[str, Any]) -> ProviderConfigPublic:
        current = self.get_provider_config_secret(config_id)
        api_key = data.get("api_key") or current.api_key
        encrypted = encrypt_secret(api_key, get_settings().secret_key)
        now = utc_now()
        with connect() as db:
            db.execute(
                """
                UPDATE provider_configs
                SET name = ?, base_url = ?, api_key_encrypted = ?, default_model = ?,
                    timeout_seconds = ?, max_retries = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    data["name"],
                    data["base_url"],
                    encrypted,
                    data["default_model"],
                    data["timeout_seconds"],
                    data["max_retries"],
                    now,
                    config_id,
                ),
            )
        return self.get_provider_config(config_id)

    def delete_provider_config(self, config_id: int) -> None:
        self.get_provider_config(config_id)
        with connect() as db:
            db.execute("DELETE FROM provider_configs WHERE id = ?", (config_id,))

    def create_suite(self, suite: dict[str, Any]) -> SuiteRecord:
        now = utc_now()
        with connect() as db:
            cursor = db.execute(
                """
                INSERT INTO suites
                (name, description, prompt_template, evaluation_json, cases_json,
                 suite_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    suite["name"],
                    suite.get("description", ""),
                    suite["prompt_template"],
                    canonical_json(suite["evaluation"]),
                    canonical_json(suite["cases"]),
                    canonical_json(suite),
                    now,
                ),
            )
            suite_id = cursor.lastrowid
        return self.get_suite(suite_id)

    def list_suites(self) -> list[SuiteRecord]:
        with connect() as db:
            rows = db.execute("SELECT * FROM suites ORDER BY id").fetchall()
        return [suite_record(row) for row in rows]

    def get_suite(self, suite_id: int) -> SuiteRecord:
        with connect() as db:
            row = db.execute("SELECT * FROM suites WHERE id = ?", (suite_id,)).fetchone()
        if row is None:
            raise NotFoundError("suite not found")
        return suite_record(row)

    def delete_suite(self, suite_id: int) -> None:
        self.get_suite(suite_id)
        with connect() as db:
            db.execute("DELETE FROM suites WHERE id = ?", (suite_id,))

    def create_run(self, data: dict[str, Any], total_cases: int) -> RunRecord:
        now = utc_now()
        with connect() as db:
            cursor = db.execute(
                """
                INSERT INTO runs
                (status, suite_id, provider_config_id, model, temperature, max_tokens,
                 concurrency, use_cache, total_cases, created_at, updated_at)
                VALUES ('pending', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["suite_id"],
                    data["provider_config_id"],
                    data["model"],
                    data["temperature"],
                    data["max_tokens"],
                    data["concurrency"],
                    int(data["use_cache"]),
                    total_cases,
                    now,
                    now,
                ),
            )
            run_id = cursor.lastrowid
        return self.get_run(run_id)

    def get_run(self, run_id: int) -> RunRecord:
        with connect() as db:
            row = db.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        if row is None:
            raise NotFoundError("run not found")
        return run_record(row)

    def list_runs(self) -> list[RunRecord]:
        with connect() as db:
            rows = db.execute("SELECT * FROM runs ORDER BY id DESC").fetchall()
        return [run_record(row) for row in rows]

    def update_run(self, run_id: int, **fields: Any) -> RunRecord:
        if not fields:
            return self.get_run(run_id)
        fields["updated_at"] = utc_now()
        assignments = ", ".join(f"{key} = ?" for key in fields)
        values = list(fields.values()) + [run_id]
        with connect() as db:
            db.execute(f"UPDATE runs SET {assignments} WHERE id = ?", values)
        return self.get_run(run_id)

    def update_case_result(
        self,
        run_id: int,
        case_id: str,
        **fields: Any,
    ) -> CaseResultRecord:
        if not fields:
            return self.get_case_result_by_case(run_id, case_id)
        fields["updated_at"] = utc_now()
        assignments = ", ".join(f"{key} = ?" for key in fields)
        values = list(fields.values()) + [run_id, case_id]
        with connect() as db:
            db.execute(
                f"UPDATE case_results SET {assignments} WHERE run_id = ? AND case_id = ?",
                values,
            )
        return self.get_case_result_by_case(run_id, case_id)

    def create_case_result(self, data: dict[str, Any]) -> CaseResultRecord:
        now = utc_now()
        with connect() as db:
            cursor = db.execute(
                """
                INSERT INTO case_results
                (run_id, case_id, status, prompt, expected, output, raw_response,
                 score, reason, latency_ms, cache_hit, error_message, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["run_id"],
                    data["case_id"],
                    data["status"],
                    data["prompt"],
                    data["expected"],
                    data.get("output"),
                    data.get("raw_response"),
                    data.get("score", 0),
                    data.get("reason", ""),
                    data.get("latency_ms"),
                    int(data.get("cache_hit", False)),
                    data.get("error_message"),
                    now,
                    now,
                ),
            )
            result_id = cursor.lastrowid
        return self.get_case_result(result_id)

    def get_case_result_by_case(self, run_id: int, case_id: str) -> CaseResultRecord:
        with connect() as db:
            row = db.execute(
                "SELECT * FROM case_results WHERE run_id = ? AND case_id = ?",
                (run_id, case_id),
            ).fetchone()
        if row is None:
            raise NotFoundError("case result not found")
        return case_result(row)

    def get_case_result(self, result_id: int) -> CaseResultRecord:
        with connect() as db:
            row = db.execute("SELECT * FROM case_results WHERE id = ?", (result_id,)).fetchone()
        if row is None:
            raise NotFoundError("case result not found")
        return case_result(row)

    def list_case_results(self, run_id: int) -> list[CaseResultRecord]:
        with connect() as db:
            rows = db.execute(
                "SELECT * FROM case_results WHERE run_id = ? ORDER BY id",
                (run_id,),
            ).fetchall()
        return [case_result(row) for row in rows]

    def get_cache(self, cache_key: str) -> CacheRecord | None:
        with connect() as db:
            row = db.execute(
                "SELECT * FROM response_cache WHERE cache_key = ?",
                (cache_key,),
            ).fetchone()
        if row is None:
            return None
        return CacheRecord(row["cache_key"], row["output"], row["raw_response"], row["created_at"])

    def set_cache(self, cache_key: str, data: dict[str, Any]) -> None:
        with connect() as db:
            db.execute(
                """
                INSERT OR REPLACE INTO response_cache
                (cache_key, provider_config_id, model, rendered_prompt, temperature,
                 max_tokens, output, raw_response, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cache_key,
                    data["provider_config_id"],
                    data["model"],
                    data["rendered_prompt"],
                    data["temperature"],
                    data["max_tokens"],
                    data["output"],
                    data.get("raw_response"),
                    utc_now(),
                ),
            )
