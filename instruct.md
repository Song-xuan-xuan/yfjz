# yfjz 项目开发说明

本文档面向后续接手本仓库的 LLM 或开发者，用于快速理解项目目标、目录结构和开发规范。

## 1. 选题与目标

本项目选择 `0628.md` 中的问题二：自定义 LLM 评估与基准测试框架。

原题核心要求：

1. 提供 CLI，支持运行指定测试套件，例如 `evaluate --suite math --model gpt-4`
2. `evaluator` 模块支持自定义评估指标，例如准确率、BLEU、ROUGE、正则评分
3. `tools` 模块提供数据集加载、模型 API 调用重试、结果缓存等工具函数
4. 至少对接一种大模型 API，并比对模型原始输出与预期答案
5. 提供项目设计文档，说明模块划分、评估流程、指标扩展接口

当前项目扩展为前后端分离形态：

- 后端：FastAPI + uv + Python 3.12
- 前端：Vue 3 + TypeScript + Vite
- 可选保留 CLI：CLI 与 Web API 复用同一套评估服务层

## 2. 项目定位

目标不是做聊天机器人，而是做“评估平台”。

典型流程：

```text
用户选择测试套件
  ↓
选择模型 provider 和评分指标
  ↓
后端加载数据集并调用模型
  ↓
评分器比对模型输出与期望答案
  ↓
缓存原始输出和评分结果
  ↓
前端展示任务状态与报告
```

## 3. 推荐目录结构

```text
.
├── backend/
│   ├── src/
│   │   └── yfjz/
│   │       ├── api/             # FastAPI 路由
│   │       ├── application/     # 评估任务编排
│   │       ├── datasets/        # 测试集加载
│   │       ├── evaluators/      # 评分器
│   │       ├── providers/       # 模型服务商适配
│   │       ├── reports/         # 报告生成
│   │       ├── storage/         # SQLite/cache
│   │       ├── tools/           # 重试、缓存、文件工具
│   │       ├── cli.py           # evaluate 命令行入口
│   │       └── app.py           # FastAPI app
│   ├── tests/
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/
│   ├── src/
│   │   ├── api/                 # 后端 API 客户端
│   │   ├── components/          # 可复用组件
│   │   ├── pages/               # 页面
│   │   ├── stores/              # 状态管理
│   │   └── App.vue
│   └── package.json
├── docs/
├── 0628.md
├── instruct.md
└── README.md
```

## 4. 后端边界

后端只负责评估业务和数据接口，不直接关心页面布局。

建议模块：

- `api`：HTTP 接口层，只做请求校验、响应转换和错误映射
- `application`：任务编排层，串联数据集、provider、evaluator、report
- `datasets`：读取 JSONL/YAML/CSV 测试集，转换成统一样本结构
- `providers`：封装 OpenAI、Anthropic、本地 vLLM 等模型调用
- `evaluators`：实现评分接口，例如 exact match、regex、accuracy
- `tools`：重试、缓存、文件读写、时间统计等基础工具
- `storage`：SQLite 持久化任务、样本输出、评分结果和缓存
- `reports`：生成 Markdown/HTML/JSON 报告

后端不要在路由函数里堆业务逻辑。路由调用 application service，service 再调用领域模块。

## 5. 前端边界

前端是评估工作台，不是营销落地页。

核心页面建议：

- 测试套件列表：查看已有 suite、样本数量、指标类型
- 创建评估任务：选择 suite、provider、model、evaluator
- 任务详情：查看运行状态、失败原因、样本级输出
- 报告页：展示准确率、错误样本、模型原始输出和导出入口

UI 风格建议：

- 面向数据分析和后台操作，保持密度适中、信息清晰
- 优先使用表格、状态标签、筛选器、分段控件和图表
- 不要做营销 hero 页，不要用大面积装饰渐变
- 保证移动端不横向溢出，正文最小 16px
- 所有交互控件需要可见 focus 状态和明确 loading/error 状态

## 6. API 草案

推荐先实现这些接口：

```text
GET    /health
GET    /api/suites
POST   /api/suites
GET    /api/evaluators
GET    /api/providers
POST   /api/runs
GET    /api/runs
GET    /api/runs/{run_id}
GET    /api/runs/{run_id}/report
```

任务运行初期可以同步执行；后续再扩展后台任务队列。

## 7. 数据格式建议

测试集样本优先使用 JSONL：

```json
{"id":"math-001","input":"1+1=?","expected":"2","evaluator":"exact_match"}
{"id":"math-002","input":"3*4=?","expected":"12","evaluator":"exact_match"}
```

测试套件配置可使用 YAML：

```yaml
name: math
dataset: datasets/math.jsonl
prompt_template: |
  请回答下面的问题，只输出最终答案：
  {{ input }}
evaluators:
  - exact_match
```

## 8. 开发规范

通用规范：

- 不硬编码 API Key，使用 `.env` 或环境变量
- 不把 `.venv/`、`node_modules/`、缓存和构建产物提交进 Git
- 先保证核心流程可跑通，再做扩展模块
- 对外部 API 调用必须有超时、重试和错误记录
- 所有模型原始输出都要保存，方便复查评分结果

Python 规范：

- 后端使用 `uv` 管理依赖
- 新功能优先写测试，再实现
- 函数保持单一职责，避免把评估流程写成一个大函数
- FastAPI 路由只做接口层逻辑，业务逻辑放入 service/module
- 数据结构优先使用 Pydantic model 或 dataclass

Vue 规范：

- 使用 Vue 3 Composition API
- 组件只负责视图和交互，不直接拼业务流程
- API 请求集中放在 `frontend/src/api/`
- 页面状态集中管理，避免深层组件互相传复杂对象
- 表格、表单和图表要考虑 loading、empty、error 三种状态

Git 规范：

- 提交信息使用 `<emoji> <type>(scope): summary`
- 示例：`✨ feat(backend): 添加评估任务接口`
- 每次提交只包含一个清晰主题
- 提交前运行相关验证命令

## 9. 建议实现顺序

1. 后端定义核心数据结构：Suite、Sample、ProviderResponse、EvaluationResult
2. 实现 JSONL 数据集加载和 exact match 评分器
3. 实现 fake provider，用于无真实 API Key 的本地测试
4. 实现 FastAPI 接口：查看 suite、创建 run、查看 run 结果
5. 实现 CLI，并复用后端 application service
6. 前端接入 API，完成 suite 列表、创建任务和结果页
7. 接入真实 OpenAI provider
8. 增加缓存、报告导出和设计文档

## 10. 验收标准

最小可交付版本应满足：

- 可以通过 CLI 或 Web 创建一次评估任务
- 可以读取至少一个本地测试集
- 可以使用 fake provider 或真实 provider 生成模型输出
- 可以用至少一个 evaluator 评分
- 可以保存并查看评估结果
- 有设计文档说明模块划分、评估流程和扩展接口
