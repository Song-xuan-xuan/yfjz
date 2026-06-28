# Backend API

后端 FastAPI 应用保留 `create_app()`，健康检查不带前缀，业务接口统一使用 `/api` 前缀。

## System

`GET /health`

响应：

```json
{"status": "ok", "service": "yfjz-backend"}
```

## Provider Configs

Provider config 用于保存 OpenAI-compatible API 连接信息。响应永远只返回 `api_key_masked`，不返回完整 `api_key`。

- `GET /api/provider-configs`
- `POST /api/provider-configs`
- `PUT /api/provider-configs/{id}`
- `DELETE /api/provider-configs/{id}`
- `POST /api/provider-configs/{id}/test`

创建请求：

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

响应：

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

## Suites

仅支持 JSON suite，不支持 YAML。

- `GET /api/suites`
- `POST /api/suites`
- `GET /api/suites/{id}`
- `DELETE /api/suites/{id}`

创建请求：

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
      {"id": "case_001", "question": "1 + 1 = ?", "answer": "2"}
    ]
  }
}
```

列表项响应包含 `id`、`name`、`description`、`case_count`、`metric_type`、`created_at`。

## Runs

- `GET /api/runs`
- `POST /api/runs`
- `GET /api/runs/{id}`
- `GET /api/runs/{id}/results`

创建请求：

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

`POST /api/runs` 创建 run 后返回 run 记录，并在后台执行 case。状态取值：

- run: `pending`, `running`, `completed`, `failed`
- case: `pending`, `running`, `passed`, `failed`, `error`

`GET /api/runs/{id}` 返回聚合字段：`total_cases`、`completed_cases`、`passed_cases`、`failed_cases`、`error_cases`、`score`、`average_latency_ms`、`cache_hit_count`、`error_message`。
如果 run 顶层执行失败，`status` 为 `failed`，`error_message` 包含后端可展示的失败原因。

`GET /api/runs/{id}/results` 返回每个 case 的 prompt、expected、output、score、reason、latency、cache_hit 与 error_message。
run 创建后会预创建每个 case 的 `pending` 结果；执行中 case 会更新为 `running`，完成后更新为 `passed`、`failed` 或 `error`。
