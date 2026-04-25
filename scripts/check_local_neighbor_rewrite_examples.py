#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from trim.utils.paths import serialize_project_path


DEFAULT_ROOT = (
    "outputs/reasoning_rewrite_outputs_neighbor_level/"
    "openrouter/openai__gpt-5.4-mini/local_neighbor/train"
)


META_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        # Keep this checker aligned with run_local_neighbor_rewrite_examples:
        # generic meta-language regexes live in validate_saved_rewrite_output.
        r"\bStep [0-9]+",
        )
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check local-neighbor rewrite example outputs.")
    parser.add_argument("--root", default=DEFAULT_ROOT)
    parser.add_argument(
        "--example",
        action="append",
        required=True,
        help="Task/sample pair in the form TASK:SAMPLE_INDEX",
    )
    parser.add_argument(
        "--output-path",
        default=None,
        help="Where to write the JSON report. Defaults to <root>/five_task_quality_check.json",
    )
    return parser.parse_args()


def _parse_examples(values: list[str]) -> dict[str, int]:
    examples: dict[str, int] = {}
    for value in values:
        if ":" not in value:
            raise ValueError(f"Expected TASK:SAMPLE_INDEX, got {value!r}")
        task, sample_index_text = value.rsplit(":", 1)
        examples[task] = int(sample_index_text)
    return examples


def _expected_label(source: dict[str, Any]) -> int:
    text = str(source["pair_prediction_semantics"])
    if "option (B)" in text:
        return 1
    if "option (A)" in text:
        return 0
    raise ValueError(f"Could not parse pair prediction semantics: {text!r}")


def main() -> int:
    args = parse_args()
    root = Path(args.root)
    examples = _parse_examples(args.example)

    rows: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for task, sample_index in examples.items():
        for neighbor_index in range(1, 7):
            result_path = root / task / f"sample_{sample_index:05d}" / f"neighbor_{neighbor_index:02d}" / "result.json"
            if not result_path.exists():
                issue = {"type": "missing_result", "path": serialize_project_path(result_path)}
                issues.append(issue)
                rows.append(issue)
                continue

            payload = json.loads(result_path.read_text(encoding="utf-8"))
            parsed = dict(payload["parsed_output"])
            source = dict(payload["source_neighbor"])
            reasoning = str(parsed.get("reasoning", ""))
            prediction = parsed.get("neighbor_prediction", {})
            if not isinstance(prediction, dict):
                prediction = {}
            label_ok = int(prediction.get("label", -1)) == _expected_label(source)
            strength_ok = parsed.get("evidence_strength") == source["teacher_aligned_evidence_strength"]
            quality_check = parsed.get("quality_check", {})
            quality_all_true = isinstance(quality_check, dict) and bool(quality_check) and all(
                value is True for value in quality_check.values()
            )
            extra_meta_patterns = sorted({pattern.pattern for pattern in META_PATTERNS if pattern.search(reasoning)})

            row = {
                "task": task,
                "sample_index": sample_index,
                "neighbor_index": neighbor_index,
                "path": serialize_project_path(result_path),
                "label_ok": label_ok,
                "strength_ok": strength_ok,
                "meta_reference_free": bool(payload.get("post_checks", {}).get("meta_reference_free")),
                "quality_all_true": quality_all_true,
                "extra_meta_patterns": extra_meta_patterns,
                "attempt_count": payload.get("attempt_count"),
                "reasoning_chars": len(reasoning),
                "prediction": prediction,
                "strength": parsed.get("evidence_strength"),
                "source_prediction": source.get("pair_prediction_semantics"),
                "source_strength": source.get("teacher_aligned_evidence_strength"),
                "reasoning_tail": reasoning[-360:],
            }
            rows.append(row)
            if (
                not label_ok
                or not strength_ok
                or not row["meta_reference_free"]
                or not quality_all_true
                or extra_meta_patterns
            ):
                issues.append(row)

    summary = {
        "checked_rows": len([row for row in rows if row.get("type") != "missing_result"]),
        "expected_rows": len(examples) * 6,
        "issue_count": len(issues),
        "tasks": examples,
        "issues": issues,
    }
    report = {
        "summary": summary,
        "rows": rows,
    }
    output_path = Path(args.output_path) if args.output_path else root / "five_task_quality_check.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"quality_check_path={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
