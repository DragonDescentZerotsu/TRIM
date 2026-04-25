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

from trim.reasoning.rewrite.pipeline import validate_saved_rewrite_output
from trim.utils.paths import serialize_project_path


DEFAULT_ROOT = (
    "outputs/reasoning_rewrite_outputs_neighbor_level/"
    "openrouter/openai__gpt-5.4-mini/local_summary/train"
)
DEFAULT_CANDIDATE_ROOT = "outputs/reasoning_rewrite_candidates/from_filters/train"

REQUIRED_QUALITY_CHECKS: tuple[str, ...] = (
    "uses_all_six_neighbors",
    "uses_similarity_and_evidence_strength",
    "handles_conflicting_neighbors",
    "uses_neighbor_level_predictions_as_votes",
    "does_not_add_new_descriptor_evidence",
    "preserves_neighbor_predictions",
    "preserves_neighbor_strengths",
    "final_prediction_matches_required_label",
    "no_meta_references",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check local-summary rewrite example outputs.")
    parser.add_argument("--root", default=DEFAULT_ROOT)
    parser.add_argument("--candidate-root", default=DEFAULT_CANDIDATE_ROOT)
    parser.add_argument(
        "--example",
        action="append",
        required=True,
        help="Task/sample pair in the form TASK:SAMPLE_INDEX",
    )
    parser.add_argument(
        "--output-path",
        default=None,
        help="Where to write the JSON report. Defaults to <root>/five_task_summary_quality_check.json",
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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _candidate_path(candidate_root: Path, task: str, sample_index: int) -> Path:
    return candidate_root / task / f"sample_{sample_index:05d}.json"


def _expected_label(candidate_payload: dict[str, Any]) -> int:
    return int(candidate_payload["local_rewrite_input"]["local_prediction"])


def _neighbor_result_path(summary_root: Path, task: str, sample_index: int, neighbor_index: int) -> Path:
    return (
        summary_root.parent.parent
        / "local_neighbor"
        / summary_root.name
        / task
        / f"sample_{sample_index:05d}"
        / f"neighbor_{neighbor_index:02d}"
        / "result.json"
    )


def _neighbor_prediction_counts(summary_root: Path, task: str, sample_index: int) -> tuple[dict[str, int], list[str]]:
    counts = {"A": 0, "B": 0}
    errors: list[str] = []
    for neighbor_index in range(1, 7):
        path = _neighbor_result_path(summary_root, task, sample_index, neighbor_index)
        if not path.exists():
            errors.append(f"missing_neighbor_result:{serialize_project_path(path)}")
            continue
        try:
            payload = _load_json(path)
            parsed = payload.get("parsed_output", payload)
            prediction = parsed.get("neighbor_prediction") if isinstance(parsed, dict) else None
            option = prediction.get("option") if isinstance(prediction, dict) else None
            if option not in counts:
                errors.append(f"invalid_neighbor_prediction:{serialize_project_path(path)}:{option!r}")
                continue
            counts[str(option)] += 1
        except Exception as exc:  # noqa: BLE001 - report checker should continue scanning.
            errors.append(f"read_neighbor_result_failed:{serialize_project_path(path)}:{exc}")
    return counts, errors


def _count_phrase_present(reasoning: str, *, option: str, count: int) -> bool:
    option_label = re.escape(option)
    option_pattern = rf"option\s*\({option_label}\)"
    count_pattern = rf"{int(count)}"
    patterns = (
        # option (A) has 0 neighbors / receives 0 votes
        rf"{option_pattern}[^.{{}};\n]{{0,100}}\b{count_pattern}\s+(?:neighbors?|votes?)\b",
        # 0 neighbors / votes for option (A)
        rf"\b{count_pattern}\s+(?:neighbors?|votes?)\b[^.{{}};\n]{{0,100}}{option_pattern}",
        # 0 for option (A)
        rf"\b{count_pattern}\s+for\s+{option_pattern}",
        # option (A)=0 / A=0
        rf"{option_pattern}\s*=\s*{count_pattern}\b",
        rf"\b{option_label}\s*=\s*{count_pattern}\b",
    )
    return any(re.search(pattern, reasoning, flags=re.IGNORECASE) for pattern in patterns)


def main() -> int:
    args = parse_args()
    root = Path(args.root)
    candidate_root = Path(args.candidate_root)
    examples = _parse_examples(args.example)

    rows: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for task, sample_index in examples.items():
        result_path = root / task / f"sample_{sample_index:05d}" / "result.json"
        candidate_path = _candidate_path(candidate_root, task, sample_index)
        if not result_path.exists():
            issue = {"type": "missing_result", "path": serialize_project_path(result_path)}
            rows.append(issue)
            issues.append(issue)
            continue
        if not candidate_path.exists():
            issue = {"type": "missing_candidate", "path": serialize_project_path(candidate_path)}
            rows.append(issue)
            issues.append(issue)
            continue

        payload = _load_json(result_path)
        candidate_payload = _load_json(candidate_path)
        parsed = dict(payload["parsed_output"])
        reasoning = str(parsed.get("reasoning", ""))
        prediction = parsed.get("local_prediction", {})
        if not isinstance(prediction, dict):
            prediction = {}
        quality_check = parsed.get("quality_check", {})
        if not isinstance(quality_check, dict):
            quality_check = {}

        pipeline_valid = True
        pipeline_error = None
        try:
            validate_saved_rewrite_output(mode="local_summary", payload=payload)
        except Exception as exc:  # noqa: BLE001 - report checker should keep scanning all examples.
            pipeline_valid = False
            pipeline_error = str(exc)

        expected_label = _expected_label(candidate_payload)
        neighbor_counts, neighbor_count_errors = _neighbor_prediction_counts(root, task, sample_index)
        missing_count_phrases = [
            f"option ({option}) = {count}"
            for option, count in sorted(neighbor_counts.items())
            if not _count_phrase_present(reasoning, option=option, count=count)
        ]
        missing_neighbors = [
            index for index in range(1, 7) if not re.search(rf"\bNeighbors?\s*{index}\b", reasoning)
        ]
        missing_quality_checks = [
            name for name in REQUIRED_QUALITY_CHECKS if name not in quality_check
        ]
        failed_quality_checks = [
            name for name, value in quality_check.items() if value is not True
        ]
        row = {
            "task": task,
            "sample_index": sample_index,
            "path": serialize_project_path(result_path),
            "candidate_path": serialize_project_path(candidate_path),
            "label_ok": int(prediction.get("label", -1)) == expected_label,
            "expected_label": expected_label,
            "observed_prediction": prediction,
            "mentions_all_neighbors": not missing_neighbors,
            "missing_neighbors": missing_neighbors,
            "neighbor_prediction_counts": neighbor_counts,
            "neighbor_count_errors": neighbor_count_errors,
            "states_exact_vote_count": not neighbor_count_errors and not missing_count_phrases,
            "missing_count_phrases": missing_count_phrases,
            "quality_all_true": bool(quality_check) and not missing_quality_checks and not failed_quality_checks,
            "missing_quality_checks": missing_quality_checks,
            "failed_quality_checks": failed_quality_checks,
            "meta_reference_free": bool(payload.get("post_checks", {}).get("meta_reference_free")),
            "pipeline_valid": pipeline_valid,
            "pipeline_error": pipeline_error,
            "attempt_count": payload.get("attempt_count"),
            "reasoning_chars": len(reasoning),
            "reasoning_tail": reasoning[-500:],
        }
        rows.append(row)
        if (
            not row["label_ok"]
            or not row["mentions_all_neighbors"]
            or not row["states_exact_vote_count"]
            or not row["quality_all_true"]
            or not row["meta_reference_free"]
            or not pipeline_valid
        ):
            issues.append(row)

    summary = {
        "checked_rows": len([row for row in rows if "type" not in row]),
        "expected_rows": len(examples),
        "issue_count": len(issues),
        "tasks": examples,
        "issues": issues,
    }
    report = {"summary": summary, "rows": rows}
    output_path = Path(args.output_path) if args.output_path else root / "five_task_summary_quality_check.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"quality_check_path={serialize_project_path(output_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
