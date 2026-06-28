# yfjz frontend

Vue 3 + TypeScript + Vite 前端项目，用于展示 LLM 评估任务、评分结果和报告。

## 环境要求

- Node.js 22+
- npm 11+
- 后端服务已启动，默认地址为 `http://localhost:8000`

## 环境变量

默认后端 API 地址：

```text
http://localhost:8000/api
```

如需覆盖，在 `frontend/.env.local` 中配置：

```text
VITE_API_BASE_URL=http://localhost:8000/api
```

## 本地启动

```powershell
npm install
npm run dev
```

启动后访问 Vite 输出的本地地址，通常为：

```text
http://localhost:5173/
```

## 构建与部署

生产构建：

```powershell
npm ci
npm run build
```

构建产物位于：

```text
dist/
```

部署时将 `dist/` 作为静态站点目录发布。部署环境需要配置：

- `VITE_API_BASE_URL`：真实后端 API 地址，例如 `https://example.com/api`
- history 路由回退：未知路径统一返回 `index.html`

本地预览生产构建：

```powershell
npm run preview
```

## 使用说明

1. 打开 Dashboard，查看后端健康状态、测试集数量、API 配置数量和最近运行记录。
2. 进入“API 配置”，新增模型服务配置并测试连接。提交后页面只展示 masked API key。
3. 进入“测试集”，粘贴或使用示例 JSON 创建测试集；格式错误会在提交前提示。
4. 打开测试集详情页，检查 `prompt_template`、`evaluation` 和 cases 表格。
5. 进入“评估任务”，选择测试集、API 配置、模型、temperature、max_tokens、并发数和缓存开关。
6. 创建任务后进入运行详情页，等待轮询刷新完成，查看通过数、失败数、评分、平均耗时、缓存命中和 case 结果。

## 验证

```powershell
npm test -- src/api/client.test.ts
npm run build
```

## 职责

- 创建评估任务
- 查看任务状态
- 展示评分报告
- 管理测试套件入口

## 页面路由

- `/`：Dashboard
- `/providers`：API 配置
- `/suites`：测试集管理
- `/suites/:id`：测试集详情
- `/runs`：创建评估任务和最近任务
- `/runs/:id`：运行进度和报告
