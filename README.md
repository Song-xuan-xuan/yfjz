# yfjz

`yfjz` 是一个自定义 LLM 评估与基准测试平台，选题来自 `0628.md` 的问题二。

项目采用前后端分离结构：

- `backend/`：FastAPI 后端，使用 `uv` 管理 Python 环境
- `frontend/`：Vue + Vite 前端，使用 npm 管理依赖
- `docs/`：设计文档与开发记录
- `instruct.md`：给后续 LLM 或开发者阅读的项目说明与开发规范

## 环境要求

- Python 3.12+
- Git
- uv
- Node.js 22+
- npm 11+

## 后端启动

在 `backend/` 目录执行：

```powershell
cd backend
python -m uv sync
python -m uv run uvicorn yfjz.app:app --reload
```

## 前端启动

在 `frontend/` 目录执行：

```powershell
npm install
npm run dev
```

## 项目结构

```text
.
├── backend/
│   ├── src/
│   │   └── yfjz/
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── docs/
├── 0628.md
├── instruct.md
└── README.md
```

详细开发规范见 [instruct.md](./instruct.md)。

## GitHub 仓库

远程仓库地址：

```text
https://github.com/Song-xuan-xuan/yfjz.git
```

后续提交代码时，可使用：

```powershell
git add .
git commit -m "✨ feat: 初始化评估平台结构"
git push
```
