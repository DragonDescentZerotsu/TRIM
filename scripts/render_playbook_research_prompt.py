#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from trim.playbook_prompt import (
    DEFAULT_FEATURE_CONFIG,
    DEFAULT_TEMPLATE_PATH,
    default_output_path,
    render_playbook_research_prompt,
)
from trim.utils.paths import resolve_project_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render a DeepResearch-style playbook prompt for a TRIM task using the current default "
            "core-pKa + no-fr RDKit/pKa feature set."
        )
    )
    parser.add_argument("--task", required=True, help="Task name, for example BBB_Martins")
    parser.add_argument(
        "--task-description",
        default=None,
        help="Optional explicit task description. If omitted, derive one from task label semantics.",
    )
    parser.add_argument(
        "--feature-config",
        default=str(DEFAULT_FEATURE_CONFIG),
        help="Feature config JSON describing the default dense feature table.",
    )
    parser.add_argument(
        "--template-path",
        default=str(DEFAULT_TEMPLATE_PATH),
        help="Prompt template path.",
    )
    parser.add_argument(
        "--output-path",
        default=None,
        help="Optional output file path. Defaults to outputs/playbook_research_prompts/<task>/deepresearch_threshold_playbook_prompt_filled.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    rendered = render_playbook_research_prompt(
        task=args.task,
        task_description=args.task_description,
        feature_config=args.feature_config,
        template_path=args.template_path,
    )

    output_path = default_output_path(args.task) if args.output_path is None else resolve_project_path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
