# yfjz frontend

Vue 3 + TypeScript + Vite 前端项目，用于展示 LLM 评估任务、评分结果和报告。

## 环境变量

默认后端 API 地址：

```text
http://localhost:8000/api
```

如需覆盖，在 `frontend/.env.local` 中配置：

```text
VITE_API_BASE_URL=http://localhost:8000/api
```

## 本地运行

```powershell
npm install
npm run dev
```

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
