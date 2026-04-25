#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from trim.reasoning.rewrite import filter_rewrite_samples
from trim.utils.io import save_json
from trim.utils.paths import resolve_project_path, serialize_project_path


DEFAULT_GLOBAL_ROOT = "outputs/reasoning_evidence/global/all_tasks_core_pka_no_fr_keep_nan"
DEFAULT_LOCAL_ROOT = "outputs/reasoning_evidence/local/all_tasks_core_pka_no_fr_counts"
DEFAULT_OUTPUT_ROOT = "outputs/reasoning_rewrite_filters"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Filter out both-wrong samples before rewrite and save kept/dropped manifests."
    )
    parser.add_argument("--global-root", default=DEFAULT_GLOBAL_ROOT)
    parser.add_argument("--local-root", default=DEFAULT_LOCAL_ROOT)
    parser.add_argument(
        "--split",
        action="append",
        dest="splits",
        default=None,
        help="Split to filter. Repeat for multiple splits. Defaults to train only.",
    )
    parser.add_argument(
        "--task",
        action="append",
        dest="tasks",
        default=None,
        help="Optional task filter. Repeat to include multiple tasks.",
    )
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args()


def _task_names(global_root: Path, local_root: Path, requested_tasks: list[str] | None) -> list[str]:
    available = sorted(path.name for path in global_root.iterdir() if path.is_dir())
    available = [task for task in available if (local_root / task).is_dir()]
    if requested_tasks is None:
        return available
    requested = set(requested_tasks)
    selected = [task for task in available if task in requested]
    missing = sorted(requested.difference(selected))
    if missing:
        raise ValueError(f"Tasks not found under both roots: {missing}")
    return selected


def main() -> int:
    args = parse_args()
    splits = args.splits or ["train"]
    global_root = resolve_project_path(args.global_root)
    local_root = resolve_project_path(args.local_root)
    output_root = resolve_project_path(args.output_root)
    tasks = _task_names(global_root, local_root, args.tasks)

    summary_rows: list[dict[str, object]] = []
    for task in tasks:
        for split in splits:
            global_dir = global_root / task / split
            local_dir = local_root / task / split
            output_dir = output_root / split / task
            manifest = filter_rewrite_samples(
                global_dir=global_dir,
                local_dir=local_dir,
                output_dir=output_dir,
            )
            summary_rows.append(
                {
                    "task": task,
                    "split": split,
                    "total_record_count": int(manifest["total_record_count"]),
                    "kept_record_count": int(manifest["kept_record_count"]),
                    "dropped_record_count": int(manifest["dropped_record_count"]),
                    "teacher_case_counts": dict(manifest["teacher_case_counts"]),
                    "output_dir": serialize_project_path(output_dir),
                }
            )

    summary = {
        "schema_version": "trim_reasoning_rewrite_filter_summary_v1",
        "global_root": serialize_project_path(global_root),
        "local_root": serialize_project_path(local_root),
        "splits": splits,
        "tasks": tasks,
        "rows": summary_rows,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    save_json(output_root / "summary.json", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
