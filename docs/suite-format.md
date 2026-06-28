# JSON Suite Format

第一版只支持 JSON suite。模板只支持简单字段替换：`{{ field_name }}`，不支持嵌套字段、循环或 YAML。

## Schema

```json
{
  "name": "math-basic",
  "description": "Basic math evaluation",
  "prompt_template": "Please answer: {{ question }}",
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

## Validation Rules

- `cases` 至少包含一个 case。
- 每个 case 必须包含非空 `id`。
- case `id` 必须唯一。
- `evaluation.expected_field` 必须存在于每个 case 中。
- `prompt_template` 中的每个 `{{ field_name }}` 都必须存在于每个 case 中。
- case 字段允许自定义，但第一版模板字段名只支持字母、数字和下划线。

## Evaluators

支持的 `evaluation.type`：

- `exact_match`: 比较完整输出与 expected 是否相等。
- `contains`: 判断输出是否包含 expected。
- `regex_match`: 将 expected 作为正则表达式匹配输出。

`exact_match` 和 `contains` 支持：

- `strip`: 比较前去掉首尾空白。
- `ignore_case`: 比较前忽略大小写。

`regex_match` 中无效正则不会中断整个 run，会返回未通过的评分结果或 case error。
