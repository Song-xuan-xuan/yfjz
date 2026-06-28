# Dataset Scripts

本目录存放项目开发和演示用的数据集辅助脚本，和 `backend/`、`frontend/` 解耦。

当前目标是把公开中文评测数据集转换为本项目支持的 JSON suite 格式，便于在前端上传并运行评估任务。

## 目录约定

```text
scripts/dataset/
├── README.md
└── convert_ceval.py
```

推荐输出目录：

```text
data/suites/
```

`data/suites/` 用于保存转换后的 JSON suite 文件。转换脚本会在输出时自动创建目录。

## 数据集选择

第一版推荐使用 C-Eval：

- 数据集地址：`ceval/ceval-exam`
- 类型：中文多学科多选题
- 字段：`question`、`A`、`B`、`C`、`D`、`answer`
- 适配评分器：`exact_match`

选择 C-Eval 的原因是字段天然接近本项目的 suite 协议，可以稳定转换为选择题评估集。

## 安装依赖

脚本依赖 Hugging Face `datasets`：

```powershell
python -m pip install datasets
```

不建议把该依赖加入 `backend/pyproject.toml`，因为它只是离线辅助脚本依赖，不属于后端运行时依赖。

## 列出可用学科

```powershell
python scripts/dataset/convert_ceval.py --list-subjects
```

如果 Hugging Face 网络不可用，该命令会失败。可稍后重试，或手动指定已知学科名。

## 转换样例

```powershell
python scripts/dataset/convert_ceval.py `
  --subject accountant `
  --split val `
  --limit 20 `
  --output data/suites/ceval_accountant_20.json
```

常用参数：

- `--subject`：C-Eval 学科配置名，例如 `accountant`
- `--split`：数据集 split，优先用带答案的 `val` 或 `dev`
- `--limit`：最多转换多少条样本
- `--seed`：随机抽样种子
- `--output`：输出 JSON suite 路径
- `--suite-name`：可选，自定义 suite 名称

## 输出格式

脚本输出符合本项目的 JSON suite 协议：

```json
{
  "name": "ceval-accountant-20",
  "description": "C-Eval 中文多选题转换样例：accountant / val / 20 cases",
  "prompt_template": "请选择正确答案，只输出 A、B、C 或 D。\n题目：{{ question }}\nA. {{ A }}\nB. {{ B }}\nC. {{ C }}\nD. {{ D }}",
  "evaluation": {
    "type": "exact_match",
    "expected_field": "answer",
    "ignore_case": true,
    "strip": true
  },
  "cases": [
    {
      "id": "accountant_val_0001",
      "question": "题目文本",
      "A": "选项 A",
      "B": "选项 B",
      "C": "选项 C",
      "D": "选项 D",
      "answer": "B"
    }
  ]
}
```

生成后可在前端“测试集”页面上传该 JSON 文件。

