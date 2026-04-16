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

from trim.playbook_prompt import (
    DEFAULT_FEATURE_CONFIG,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_TASK_MANIFEST_INDEX,
    DEFAULT_TEMPLATE_PATH,
    load_task_names_from_manifest_index,
    render_playbook_research_prompts_for_tasks,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render playbook-research prompts for all tasks in a manifest index."
    )
    parser.add_argument(
        "--manifest-index",
        default=str(DEFAULT_TASK_MANIFEST_INDEX),
        help="Manifest index JSON used to discover task names.",
    )
    parser.add_argument(
        "--feature-config",
        default=str(DEFAULT_FEATURE_CONFIG),
        help="Feature config JSON describing the dense molecular-property table.",
    )
    parser.add_argument(
        "--template-path",
        default=str(DEFAULT_TEMPLATE_PATH),
        help="Prompt template path.",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Directory where per-task rendered prompts will be written.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tasks = load_task_names_from_manifest_index(args.manifest_index)
    summary = render_playbook_research_prompts_for_tasks(
        tasks=tasks,
        output_root=args.output_root,
        feature_config=args.feature_config,
        template_path=args.template_path,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
