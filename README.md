# yfjz

`yfjz` 是一个使用 Python 编写、通过 `uv` 管理虚拟环境和依赖的项目。

## 环境要求

- Python 3.12+
- Git
- uv

当前仓库已经配置为使用 Python 3.12，并通过 `uv.lock` 锁定依赖解析结果。

## 快速开始

在项目根目录执行：

```powershell
python -m uv sync
```

如果你的终端已经能直接识别 `uv` 命令，也可以使用：

```powershell
uv sync
```

同步完成后，本地虚拟环境位于 `.venv/`。在 Windows PowerShell 中可按需激活：

```powershell
.\.venv\Scripts\Activate.ps1
```

## 常用命令

运行项目入口：

```powershell
python -m uv run yfjz
```

添加运行时依赖：

```powershell
python -m uv add <package>
```

添加开发依赖：

```powershell
python -m uv add --dev <package>
```

## 项目结构

```text
.
├── src/
│   └── yfjz/
│       └── __init__.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## GitHub 仓库

远程仓库地址：

```text
https://github.com/Song-xuan-xuan/yfjz.git
```

后续提交代码时，可使用：

```powershell
git add .
git commit -m "🎉 init: 初始化 Python 项目"
git push -u origin main
```
