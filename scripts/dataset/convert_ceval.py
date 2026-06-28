from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DATASET_NAME = "ceval/ceval-exam"
DEFAULT_PROMPT_TEMPLATE = (
    "请选择正确答案，只输出 A、B、C 或 D。\n"
    "题目：{{ question }}\n"
    "A. {{ A }}\n"
    "B. {{ B }}\n"
    "C. {{ C }}\n"
    "D. {{ D }}"
)
CHOICE_LABELS = ("A", "B", "C", "D")


@dataclass(frozen=True)
class ConvertOptions:
    subject: str
    split: str
    limit: int
    seed: int
    output: Path
    suite_name: str | None


def import_datasets() -> tuple[Any, Any]:
    try:
        from datasets import get_dataset_config_names, load_dataset
    except ImportError:
        print(
            "缺少依赖 datasets。请先运行：python -m pip install datasets",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return get_dataset_config_names, load_dataset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download and convert C-Eval into yfjz JSON suite format.",
    )
    parser.add_argument("--list-subjects", action="store_true", help="列出 C-Eval 学科")
    parser.add_argument("--subject", help="C-Eval 学科配置名，例如 accountant")
    parser.add_argument("--split", default="val", help="数据集 split，默认 val")
    parser.add_argument("--limit", type=int, default=20, help="转换样本数量，默认 20")
    parser.add_argument("--seed", type=int, default=42, help="随机抽样种子，默认 42")
    parser.add_argument("--output", type=Path, help="输出 JSON suite 路径")
    parser.add_argument("--suite-name", help="可选，自定义 suite 名称")
    return parser


def list_subjects() -> None:
    get_dataset_config_names, _ = import_datasets()
    subjects = get_dataset_config_names(DATASET_NAME)
    for subject in subjects:
        print(subject)


def parse_options(args: argparse.Namespace) -> ConvertOptions:
    if not args.subject:
        raise SystemExit("缺少 --subject。可先运行 --list-subjects 查看可用学科。")
    if args.limit <= 0:
        raise SystemExit("--limit 必须大于 0。")
    output = args.output or Path("data") / "suites" / f"ceval_{args.subject}_{args.limit}.json"
    return ConvertOptions(
        subject=args.subject,
        split=args.split,
        limit=args.limit,
        seed=args.seed,
        output=output,
        suite_name=args.suite_name,
    )


def load_rows(options: ConvertOptions) -> list[dict[str, Any]]:
    _, load_dataset = import_datasets()
    dataset = load_dataset(DATASET_NAME, options.subject, split=options.split)
    rows = [dict(row) for row in dataset]
    if not rows:
        raise SystemExit(f"数据集为空：{options.subject}/{options.split}")

    rng = random.Random(options.seed)
    if len(rows) > options.limit:
        rows = rng.sample(rows, options.limit)
    return rows


def normalize_answer(value: Any) -> str:
    if isinstance(value, int):
        if value < 0 or value >= len(CHOICE_LABELS):
            raise ValueError(f"answer 索引超出范围：{value}")
        return CHOICE_LABELS[value]
    answer = str(value).strip().upper()
    if answer not in CHOICE_LABELS:
        raise ValueError(f"answer 必须是 A/B/C/D 或 0-3，实际为：{value!r}")
    return answer


def build_case(row: dict[str, Any], options: ConvertOptions, index: int) -> dict[str, str]:
    missing = [field for field in ("question", "A", "B", "C", "D", "answer") if field not in row]
    if missing:
        raise ValueError(f"样本缺少字段 {missing}：{row}")
    return {
        "id": f"{options.subject}_{options.split}_{index + 1:04d}",
        "question": str(row["question"]).strip(),
        "A": str(row["A"]).strip(),
        "B": str(row["B"]).strip(),
        "C": str(row["C"]).strip(),
        "D": str(row["D"]).strip(),
        "answer": normalize_answer(row["answer"]),
    }


def build_suite(rows: list[dict[str, Any]], options: ConvertOptions) -> dict[str, Any]:
    cases = [build_case(row, options, index) for index, row in enumerate(rows)]
    suite_name = options.suite_name or f"ceval-{options.subject}-{len(cases)}"
    return {
        "name": suite_name,
        "description": (
            f"C-Eval 中文多选题转换样例："
            f"{options.subject} / {options.split} / {len(cases)} cases"
        ),
        "prompt_template": DEFAULT_PROMPT_TEMPLATE,
        "evaluation": {
            "type": "exact_match",
            "expected_field": "answer",
            "ignore_case": True,
            "strip": True,
        },
        "cases": cases,
    }


def write_suite(suite: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(suite, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def convert(options: ConvertOptions) -> None:
    rows = load_rows(options)
    suite = build_suite(rows, options)
    write_suite(suite, options.output)
    print(f"已生成：{options.output}")
    print(f"样本数：{len(suite['cases'])}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.list_subjects:
        list_subjects()
        return
    options = parse_options(args)
    convert(options)


if __name__ == "__main__":
    main()
