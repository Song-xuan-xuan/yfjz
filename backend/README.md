# yfjz backend

FastAPI 后端项目，负责自定义 LLM 评估与基准测试框架的核心能力。

## 职责

- 管理测试套件与数据集
- 调用模型 provider
- 执行评估任务
- 计算评分指标
- 缓存模型输出
- 生成评估报告

## 已实现能力

- FastAPI 应用工厂 `create_app()`，业务接口统一使用 `/api` 前缀
- SQLite 持久化 provider configs、suites、runs、case results、response cache
- OpenAI-compatible `/chat/completions` provider，支持超时与重试
- JSON suite 校验与简单 `{{ field_name }}` prompt 渲染
- `exact_match`、`contains`、`regex_match` 评分器
- 异步并发 run 执行，使用 `asyncio.Semaphore(concurrency)` 控制并发
- Typer CLI：`list-suites`、`run`、`show-run`

## 部署与启动

### 1. 安装依赖

进入后端目录：

```powershell
cd backend
```

推荐使用 `uv` 同步依赖：

```powershell
python -m uv sync
```

如果已经激活 `.venv`，且虚拟环境中没有 `uv` 模块，可以直接使用虚拟环境中的命令，不需要再执行 `python -m uv run`。

### 2. 开发启动

使用 `uv`：

```powershell
python -m uv run uvicorn yfjz.app:app --reload --port 8000
```

已激活 `.venv` 时：

```powershell
uvicorn yfjz.app:app --reload --port 8000
```

或：

```powershell
.\.venv\Scripts\uvicorn.exe yfjz.app:app --reload --port 8000
```

健康检查地址：

```text
http://127.0.0.1:8000/health
```

预期返回：

```json
{"status": "ok", "service": "yfjz-backend"}
```

### 3. 局域网/部署启动

如果前端部署在其他机器，或需要局域网访问：

```powershell
uvicorn yfjz.app:app --host 0.0.0.0 --port 8000
```

前端 API Base URL 配置为：

```text
http://<后端机器IP>:8000/api
```

后端已允许 `localhost` / `127.0.0.1` 任意端口的本地前端跨域访问。跨机器部署时，如需其他域名或 IP 作为浏览器 Origin，需要调整 `yfjz.app:create_app()` 中的 CORS 配置。

业务接口文档见 `../docs/backend-api.md`，suite 格式见 `../docs/suite-format.md`。

## 配置

环境变量：

- `YFJZ_DATABASE_PATH`: SQLite 路径，默认 `data/yfjz.sqlite3`
- `YFJZ_SECRET_KEY`: 本地 API key 可逆混淆密钥，默认 `local-development-secret`

Provider API key 不会在 API 响应中返回完整值，只返回 `api_key_masked`。

当前实现使用基于 `YFJZ_SECRET_KEY` 的简单可逆本地混淆，主要用于本地开发防止明文直接暴露；这不是生产级加密或密钥管理。请仅在本地开发环境使用，不要把 `backend/data/yfjz.sqlite3` 当作生产密钥仓库。

## CLI

```powershell
python -m uv run yfjz --help
python -m uv run yfjz list-suites
python -m uv run yfjz run --suite-id 1 --provider-config-id 1 --model gpt-4o-mini
python -m uv run yfjz show-run 1
```

`run` 命令复用后端 run service，会同步等待当前 run 执行完成并输出最终聚合结果。

已激活 `.venv` 时也可以直接运行：

```powershell
yfjz --help
```

## API 使用示例

新增 provider config：

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/provider-configs `
  -ContentType "application/json" `
  -Body '{
    "name":"axonhub",
    "base_url":"http://4.217.217.26:8090/v1",
    "api_key":"sk-...",
    "default_model":"glm-5",
    "timeout_seconds":60,
    "max_retries":2
  }'
```

查看 provider config：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/provider-configs
```

API 响应只返回 `api_key_masked`，不会返回完整 `api_key`。

## 测试

```powershell
python -m uv run pytest
```

如果本机已把 `uv` 可执行文件加入 PATH，也可以使用 `uv run pytest`。当前仓库文档使用 `python -m uv`，避免 Windows PATH 未配置时无法运行。

已激活 `.venv` 时：

```powershell
python -m pytest
```
