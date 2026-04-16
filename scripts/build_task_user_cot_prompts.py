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

from trim.reasoning.task_user_prompts import (
    DEFAULT_LEGACY_PROMPT_ROOTS,
    DEFAULT_TASK_MANIFEST_INDEX,
    DEFAULT_TASK_USER_PROMPT_ROOT,
    export_task_user_prompts_for_tasks,
    load_task_names_from_manifest_index,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build per-task CoT user-message templates for the current TRIM tasks."
    )
    parser.add_argument(
        "--manifest-index",
        default=str(DEFAULT_TASK_MANIFEST_INDEX),
        help="Manifest index JSON used to discover task names.",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_TASK_USER_PROMPT_ROOT),
        help="Directory where per-task prompt JSON files will be written.",
    )
    parser.add_argument(
        "--legacy-prompt-root",
        action="append",
        dest="legacy_prompt_roots",
        help=(
            "Legacy TDC prompt jsonl directory. Can be passed multiple times. "
            "Defaults to train/valid/test prompt roots from the old project."
        ),
    )
    parser.add_argument(
        "--max-records-per-root",
        type=int,
        default=32,
        help="Maximum number of records to inspect from each legacy prompt jsonl.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tasks = load_task_names_from_manifest_index(args.manifest_index)
    legacy_prompt_roots = args.legacy_prompt_roots
    if legacy_prompt_roots is None:
        legacy_prompt_roots = [str(path) for path in DEFAULT_LEGACY_PROMPT_ROOTS]

    summary = export_task_user_prompts_for_tasks(
        tasks=tasks,
        output_root=args.output_root,
        legacy_prompt_roots=legacy_prompt_roots,
        max_records_per_root=args.max_records_per_root,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
