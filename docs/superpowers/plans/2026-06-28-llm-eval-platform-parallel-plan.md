# LLM Evaluation Platform Parallel Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a FastAPI + Vue front-end/back-end separated LLM evaluation platform for topic 2 in `0628.md`.

**Architecture:** The backend owns provider configuration, suite validation, asynchronous concurrent evaluation runs, scoring, caching, and persistence. The frontend owns the evaluation workbench UI and talks to the backend only through the HTTP API contract in this document. Backend and frontend workers must not edit each other's directories.

**Tech Stack:** Backend: Python 3.12, FastAPI, Pydantic, SQLite, httpx, Typer, pytest. Frontend: Vue 3, Vite, TypeScript, native CSS or lightweight local components, fetch/Axios, optional ECharts only if needed.

---

## Parallel Work Rules

- Backend worker owns only `backend/**`, backend-related docs under `docs/backend-*.md`, and shared API documentation updates in this plan.
- Frontend worker owns only `frontend/**`, frontend-related docs under `docs/frontend-*.md`, and may read this plan but must not change backend code.
- Shared contract changes require stopping both workers and updating this document first.
- Do not change root-level project layout during implementation.
- Do not store full API keys in frontend local storage, query strings, browser logs, or UI state beyond the create/update request payload.
- First version supports JSON suites only. Do not implement YAML loading even if `pyyaml` exists in backend dependencies.
- Use TDD for backend service logic and frontend API/client behavior where practical.

## Product Scope

The system is a local LLM benchmark platform with these first-version capabilities:

- Manage multiple OpenAI-compatible API configurations, each with a user-defined display name.
- Upload or create JSON evaluation suites.
- Start asynchronous evaluation runs.
- Execute suite cases concurrently with a configurable concurrency limit.
- Cache model raw outputs by request fingerprint.
- Score outputs using `exact_match`, `contains`, or `regex_match`.
- Persist provider configs, suites, runs, case results, and cache records in SQLite.
- Show run progress and final reports in Vue.
- Provide a CLI for suite listing, run creation, and run inspection.

## Shared API Contract

All backend routes use the `/api` prefix. Responses use JSON. Timestamps are ISO 8601 strings.

### Provider Configs

`POST /api/provider-configs`

Request:

```json
{
  "name": "OpenAI Official",
  "base_url": "https://api.openai.com/v1",
  "api_key": "sk-...",
  "default_model": "gpt-4o-mini",
  "timeout_seconds": 60,
  "max_retries": 2
}
```

Response:

```json
{
  "id": 1,
  "name": "OpenAI Official",
  "base_url": "https://api.openai.com/v1",
  "api_key_masked": "sk-****abcd",
  "default_model": "gpt-4o-mini",
  "timeout_seconds": 60,
  "max_retries": 2,
  "created_at": "2026-06-28T09:30:00Z",
  "updated_at": "2026-06-28T09:30:00Z"
}
```

Required endpoints:

- `GET /api/provider-configs`
- `POST /api/provider-configs`
- `PUT /api/provider-configs/{id}`
- `DELETE /api/provider-configs/{id}`
- `POST /api/provider-configs/{id}/test`

### Suite Format

The framework defines its own JSON suite protocol. Case fields are flexible; `prompt_template` and `evaluation.expected_field` decide how to read them.

```json
{
  "name": "math-basic",
  "description": "Basic math evaluation",
  "prompt_template": "Please answer the question and output only the final answer: {{ question }}",
  "evaluation": {
    "type": "exact_match",
    "expected_field": "answer",
    "ignore_case": true,
    "strip": true
  },
  "cases": [
    {
      "id": "case_001",
      "question": "1 + 1 = ?",
      "answer": "2"
    }
  ]
}
```

Supported `evaluation.type` values:

- `exact_match`
- `contains`
- `regex_match`

Template syntax for version 1 is simple field replacement: `{{ field_name }}`. Nested field access is out of scope.

### Suites

Required endpoints:

- `GET /api/suites`
- `POST /api/suites`
- `GET /api/suites/{id}`
- `DELETE /api/suites/{id}`

`POST /api/suites` accepts:

```json
{
  "suite": {
    "name": "math-basic",
    "description": "Basic math evaluation",
    "prompt_template": "Answer: {{ question }}",
    "evaluation": {
      "type": "exact_match",
      "expected_field": "answer"
    },
    "cases": [
      {
        "id": "case_001",
        "question": "1 + 1 = ?",
        "answer": "2"
      }
    ]
  }
}
```

Suite list response item:

```json
{
  "id": 1,
  "name": "math-basic",
  "description": "Basic math evaluation",
  "case_count": 1,
  "metric_type": "exact_match",
  "created_at": "2026-06-28T09:30:00Z"
}
```

### Runs

`POST /api/runs`

Request:

```json
{
  "suite_id": 1,
  "provider_config_id": 1,
  "model": "gpt-4o-mini",
  "temperature": 0,
  "max_tokens": 512,
  "concurrency": 3,
  "use_cache": true
}
```

Immediate response:

```json
{
  "id": 1,
  "status": "pending",
  "suite_id": 1,
  "provider_config_id": 1,
  "model": "gpt-4o-mini",
  "total_cases": 10,
  "completed_cases": 0,
  "passed_cases": 0,
  "failed_cases": 0,
  "error_cases": 0,
  "score": 0,
  "created_at": "2026-06-28T09:30:00Z"
}
```

Required endpoints:

- `GET /api/runs`
- `POST /api/runs`
- `GET /api/runs/{id}`
- `GET /api/runs/{id}/results`

Run statuses:

- `pending`
- `running`
- `completed`
- `failed`

Case result statuses:

- `pending`
- `running`
- `passed`
- `failed`
- `error`

Run detail response must include progress fields:

```json
{
  "id": 1,
  "status": "running",
  "total_cases": 10,
  "completed_cases": 7,
  "passed_cases": 5,
  "failed_cases": 1,
  "error_cases": 1,
  "score": 0.7143,
  "average_latency_ms": 812.4,
  "cache_hit_count": 3
}
```

Case result item:

```json
{
  "id": 1,
  "case_id": "case_001",
  "status": "passed",
  "prompt": "Answer: 1 + 1 = ?",
  "expected": "2",
  "output": "2",
  "score": 1,
  "reason": "exact match",
  "latency_ms": 512,
  "cache_hit": false,
  "error_message": null
}
```

## Chunk 1: Backend Checklist

Backend worker must work from `backend/`.

### Task B1: Project Structure and App Wiring

**Files:**

- Modify: `backend/pyproject.toml`
- Modify: `backend/src/yfjz/app.py`
- Modify: `backend/src/yfjz/__init__.py`
- Create: `backend/src/yfjz/api/__init__.py`
- Create: `backend/src/yfjz/core/config.py`
- Create: `backend/src/yfjz/core/errors.py`
- Create: `backend/tests/test_health.py`

- [ ] Add backend dev dependencies: `pytest`, `pytest-asyncio`, `ruff` if absent.
- [ ] Keep FastAPI factory `create_app()`.
- [ ] Register `/api` routers from separate modules.
- [ ] Keep `/health` returning `{"status": "ok", "service": "yfjz-backend"}`.
- [ ] Add a backend test for `/health`.
- [ ] Run: `cd backend; uv run pytest`.

### Task B2: SQLite Storage Models

**Files:**

- Create: `backend/src/yfjz/storage/database.py`
- Create: `backend/src/yfjz/storage/models.py`
- Create: `backend/src/yfjz/storage/repositories.py`
- Create: `backend/tests/test_storage.py`

- [ ] Implement SQLite connection setup with a local `data/yfjz.sqlite3` default.
- [ ] Create tables for provider configs, suites, runs, case results, and response cache.
- [ ] Store suite JSON as canonical JSON text.
- [ ] Store provider API keys server-side only.
- [ ] Do not expose raw API keys in repository return values.
- [ ] Run: `cd backend; uv run pytest backend/tests/test_storage.py -v`.

### Task B3: Provider Config API

**Files:**

- Create: `backend/src/yfjz/api/provider_configs.py`
- Create: `backend/src/yfjz/core/secrets.py`
- Create: `backend/tests/test_provider_configs_api.py`

- [ ] Implement create/list/update/delete provider config endpoints.
- [ ] Return `api_key_masked`, never `api_key`.
- [ ] For first version, allow local reversible storage using a `SECRET_KEY`; if encryption is not implemented in time, document local-only risk in README.
- [ ] Implement `/api/provider-configs/{id}/test` using the provider abstraction.
- [ ] Run: `cd backend; uv run pytest backend/tests/test_provider_configs_api.py -v`.

### Task B4: Suite Protocol and Validation

**Files:**

- Create: `backend/src/yfjz/suites/schema.py`
- Create: `backend/src/yfjz/suites/renderer.py`
- Create: `backend/src/yfjz/api/suites.py`
- Create: `backend/tests/test_suites.py`

- [ ] Define Pydantic models for the JSON suite protocol in this document.
- [ ] Validate unique case IDs.
- [ ] Validate `evaluation.expected_field` exists in every case.
- [ ] Validate template placeholders exist in every case.
- [ ] Implement simple `{{ field_name }}` rendering.
- [ ] Reject YAML and non-JSON suite payloads.
- [ ] Run: `cd backend; uv run pytest backend/tests/test_suites.py -v`.

### Task B5: Evaluators

**Files:**

- Create: `backend/src/yfjz/evaluators/base.py`
- Create: `backend/src/yfjz/evaluators/exact_match.py`
- Create: `backend/src/yfjz/evaluators/contains.py`
- Create: `backend/src/yfjz/evaluators/regex_match.py`
- Create: `backend/src/yfjz/evaluators/registry.py`
- Create: `backend/tests/test_evaluators.py`

- [ ] Implement common evaluator result shape: `score`, `passed`, `reason`.
- [ ] Implement `exact_match` with `strip` and `ignore_case` options.
- [ ] Implement `contains` with `strip` and `ignore_case` options.
- [ ] Implement `regex_match` where expected value is the regex pattern.
- [ ] Add invalid regex handling that returns an error result, not a crash.
- [ ] Run: `cd backend; uv run pytest backend/tests/test_evaluators.py -v`.

### Task B6: OpenAI-Compatible Provider and Cache

**Files:**

- Create: `backend/src/yfjz/providers/base.py`
- Create: `backend/src/yfjz/providers/openai_compatible.py`
- Create: `backend/src/yfjz/tools/cache.py`
- Create: `backend/tests/test_cache.py`
- Create: `backend/tests/test_openai_provider.py`

- [ ] Implement provider request with model, messages, temperature, max_tokens, timeout, retries.
- [ ] Use OpenAI-compatible `/chat/completions` semantics through `httpx` or the OpenAI SDK.
- [ ] Extract output from `choices[0].message.content`.
- [ ] Preserve raw provider response JSON where possible.
- [ ] Generate cache key from provider config ID, model, rendered prompt, temperature, and max tokens.
- [ ] Cache raw model output only; always rerun evaluator.
- [ ] Run: `cd backend; uv run pytest backend/tests/test_cache.py backend/tests/test_openai_provider.py -v`.

### Task B7: Async Concurrent Run Executor

**Files:**

- Create: `backend/src/yfjz/runs/executor.py`
- Create: `backend/src/yfjz/runs/service.py`
- Create: `backend/src/yfjz/runs/aggregation.py`
- Create: `backend/src/yfjz/api/runs.py`
- Create: `backend/tests/test_runs.py`

- [ ] Implement `POST /api/runs` to create a run and return immediately.
- [ ] Execute cases asynchronously in the background.
- [ ] Use `asyncio.Semaphore(concurrency)` to limit concurrent provider calls.
- [ ] Update each case result independently.
- [ ] Do not fail the whole run when one case errors.
- [ ] Aggregate score, pass/fail/error counts, latency, and cache hits.
- [ ] Implement `GET /api/runs/{id}` and `GET /api/runs/{id}/results`.
- [ ] Run: `cd backend; uv run pytest backend/tests/test_runs.py -v`.

### Task B8: CLI

**Files:**

- Create: `backend/src/yfjz/cli.py`
- Modify: `backend/pyproject.toml`
- Create: `backend/tests/test_cli.py`

- [ ] Add CLI commands: `list-suites`, `run`, `show-run`.
- [ ] CLI may call backend service functions directly.
- [ ] Do not duplicate evaluation logic in CLI.
- [ ] Update `[project.scripts]` with an executable command such as `yfjz`.
- [ ] Run: `cd backend; uv run pytest backend/tests/test_cli.py -v`.

### Task B9: Backend Documentation and Verification

**Files:**

- Create: `docs/backend-api.md`
- Create: `docs/suite-format.md`
- Modify: `backend/README.md`

- [ ] Document all API endpoints from the shared contract.
- [ ] Document JSON suite examples and validation rules.
- [ ] Document environment variables and local SQLite storage.
- [ ] Run: `cd backend; uv run pytest`.
- [ ] Run: `cd backend; uv run yfjz --help` or the final CLI command.

## Chunk 2: Frontend Checklist

Frontend worker must work from `frontend/`.

### Task F1: Frontend Structure and API Client

**Files:**

- Modify: `frontend/package.json`
- Modify: `frontend/src/main.ts`
- Modify: `frontend/src/App.vue`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/types.ts`
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/style.css`

- [ ] Add Vue Router.
- [ ] Add Axios or use a typed `fetch` wrapper. Prefer one approach consistently.
- [ ] Set API base URL from `VITE_API_BASE_URL`, defaulting to `http://localhost:8000/api`.
- [ ] Define TypeScript types matching the shared API contract.
- [ ] Keep UI text in Simplified Chinese.
- [ ] Run: `cd frontend; npm run build`.

### Task F2: Layout and Navigation

**Files:**

- Create: `frontend/src/components/AppLayout.vue`
- Create: `frontend/src/components/StatusBadge.vue`
- Create: `frontend/src/views/DashboardView.vue`
- Modify: `frontend/src/App.vue`

- [ ] Build a workbench layout, not a marketing landing page.
- [ ] Navigation items: Dashboard, API 配置, 测试集, 评估任务.
- [ ] Use accessible buttons, labels, focus states, and at least 44px touch targets.
- [ ] Avoid emoji as UI icons.
- [ ] Show backend health or connection state if available.
- [ ] Run: `cd frontend; npm run build`.

### Task F3: Provider Config Management

**Files:**

- Create: `frontend/src/views/ProviderConfigsView.vue`
- Create: `frontend/src/components/ProviderConfigForm.vue`
- Create: `frontend/src/api/providerConfigs.ts`

- [ ] List provider configs with name, base URL, default model, masked key, and update time.
- [ ] Add provider config form with name, base URL, API key, default model, timeout, retries.
- [ ] Allow editing metadata and replacing API key.
- [ ] Add delete action with confirmation.
- [ ] Add test connection action.
- [ ] Never display or persist raw API key after submission.
- [ ] Run: `cd frontend; npm run build`.

### Task F4: Suite Management

**Files:**

- Create: `frontend/src/views/SuitesView.vue`
- Create: `frontend/src/views/SuiteDetailView.vue`
- Create: `frontend/src/components/SuiteEditor.vue`
- Create: `frontend/src/api/suites.ts`

- [ ] List suites with name, description, case count, metric type, created time.
- [ ] Provide JSON editor textarea for suite creation.
- [ ] Include a sample JSON suite button or inline placeholder.
- [ ] Validate JSON syntax before submitting.
- [ ] Show backend validation errors near the editor.
- [ ] Show suite detail with prompt template, evaluation config, and case table.
- [ ] Run: `cd frontend; npm run build`.

### Task F5: Run Creation

**Files:**

- Create: `frontend/src/views/CreateRunView.vue`
- Create: `frontend/src/api/runs.ts`

- [ ] Provide form fields for suite, provider config, model, temperature, max tokens, concurrency, and cache toggle.
- [ ] Default concurrency to `3`.
- [ ] Limit selectable concurrency to `1`, `3`, `5`, `10`.
- [ ] After create, navigate to `/runs/:id`.
- [ ] Disable submit button while request is in flight.
- [ ] Show clear backend error messages.
- [ ] Run: `cd frontend; npm run build`.

### Task F6: Run Progress and Report

**Files:**

- Create: `frontend/src/views/RunDetailView.vue`
- Create: `frontend/src/components/ProgressSummary.vue`
- Create: `frontend/src/components/CaseResultsTable.vue`
- Create: `frontend/src/components/ReportCharts.vue`
- Create: `frontend/src/api/runs.ts`

- [ ] Poll `GET /api/runs/{id}` every 1-2 seconds while status is `pending` or `running`.
- [ ] Stop polling when status is `completed` or `failed`.
- [ ] Show progress, score, pass/fail/error counts, average latency, and cache hits.
- [ ] Show case results table with prompt, expected, output, score, cache hit, status, and error.
- [ ] Use simple CSS charts or add ECharts only if it does not slow implementation.
- [ ] Ensure long model outputs wrap without horizontal page overflow.
- [ ] Run: `cd frontend; npm run build`.

### Task F7: Frontend Documentation and Verification

**Files:**

- Create: `docs/frontend-ui.md`
- Modify: `frontend/README.md`

- [ ] Document frontend routes and required backend API base URL.
- [ ] Document local dev command.
- [ ] Run: `cd frontend; npm run build`.
- [ ] If backend is available, manually verify API config, suite creation, run creation, and progress page.

## Integration Checklist

Run after both backend and frontend are individually complete.

- [ ] Start backend: `cd backend; uv run uvicorn yfjz.app:app --reload --port 8000`.
- [ ] Start frontend: `cd frontend; npm run dev`.
- [ ] Open the frontend dev URL.
- [ ] Create a provider config.
- [ ] Create a suite from the sample JSON.
- [ ] Start a run with concurrency `3` and cache enabled.
- [ ] Confirm progress updates without page refresh.
- [ ] Confirm final report shows pass/fail/error counts and case details.
- [ ] Repeat the same run and confirm cache hits increase.
- [ ] Run backend tests: `cd backend; uv run pytest`.
- [ ] Run frontend build: `cd frontend; npm run build`.

## Out of Scope for Version 1

- YAML suite support.
- User login and permissions.
- Distributed workers.
- Celery, Redis, or external queue infrastructure.
- WebSocket streaming.
- Prompt template loops or nested object access.
- BLEU, ROUGE, embedding similarity, or LLM-as-judge scoring.
- Public cloud deployment.

