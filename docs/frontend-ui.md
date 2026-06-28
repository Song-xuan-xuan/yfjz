# 前端 UI 说明

## 技术栈

- Vue 3
- TypeScript
- Vue Router
- Vite
- 原生 CSS
- fetch API client

## API Base URL

前端通过 `VITE_API_BASE_URL` 读取后端 API 地址，默认值为：

```text
http://localhost:8000/api
```

本地开发可在 `frontend/.env.local` 中覆盖：

```text
VITE_API_BASE_URL=http://localhost:8000/api
```

## 路由

- `/`：Dashboard，展示 API 配置、测试集、运行数量和推荐流程
- `/providers`：API 配置列表、新增、编辑、删除、测试连接
- `/suites`：测试集列表、JSON 编辑器、示例 suite、创建和删除
- `/suites/:id`：测试集详情，展示 prompt_template、evaluation 和 cases 表格
- `/runs`：创建评估任务，展示最近任务列表
- `/runs/:id`：运行详情，轮询进度并展示报告和样本结果

## UI 原则

- 定位为专业数据工作台，不做营销页
- 使用侧边栏导航和信息面板组织任务流
- 表单字段都有 label，按钮有 disabled/loading 状态
- 错误信息显示在相关区域附近
- 长文本使用自动换行，避免页面级横向溢出
- 图表使用轻量 CSS 条形图，避免引入大型图表库

## 后端未就绪时的兼容处理

如果后端接口尚未实现或服务未启动：

- Dashboard 会展示“部分数据加载失败”的提示
- 列表页展示局部错误和空态
- 创建表单保留输入，不会跳转
- 运行详情会展示加载失败信息

这些兼容处理不会伪造数据，只展示真实请求状态。
