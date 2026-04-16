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

from trim.reasoning.rewrite import render_rewrite_prompt
from trim.reasoning.rewrite.rendering import resolve_reasoning_text
from trim.utils.io import load_json
from trim.utils.paths import resolve_project_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render filled prompts for rewrite candidate samples.")
    parser.add_argument("--candidate-json", required=True, help="Path to one rewrite candidate JSON file")
    parser.add_argument(
        "--mode",
        required=True,
        choices=["global", "local", "hybrid"],
        help="Which rewrite prompt to render",
    )
    parser.add_argument(
        "--template-root",
        default="prompt_templates/reasoning_sft",
        help="Directory containing rewrite prompt templates",
    )
    parser.add_argument(
        "--global-reasoning",
        default=None,
        help="Raw global reasoning text or a path to a .txt/.md/.json file containing it",
    )
    parser.add_argument(
        "--local-reasoning",
        default=None,
        help="Raw local reasoning text or a path to a .txt/.md/.json file containing it",
    )
    parser.add_argument(
        "--output-path",
        default=None,
        help="Optional explicit output path for the filled prompt markdown",
    )
    return parser.parse_args()


def _default_output_path(candidate_path: Path, mode: str) -> Path:
    payload = load_json(candidate_path)
    task = str(payload["task"])
    sample_id = str(payload["sample_id"])
    return resolve_project_path("outputs/rewrite_prompts") / task / f"{sample_id}__{mode}_prompt.md"


def main() -> int:
    args = parse_args()
    candidate_path = resolve_project_path(args.candidate_json)
    candidate_payload = load_json(candidate_path)

    prompt_text = render_rewrite_prompt(
        candidate_payload=candidate_payload,
        mode=args.mode,
        template_root=args.template_root,
        global_reasoning=resolve_reasoning_text(args.global_reasoning),
        local_reasoning=resolve_reasoning_text(args.local_reasoning),
    )

    output_path = (
        resolve_project_path(args.output_path)
        if args.output_path is not None
        else _default_output_path(candidate_path, args.mode)
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prompt_text, encoding="utf-8")

    print(
        json.dumps(
            {
                "candidate_json": str(candidate_path),
                "mode": args.mode,
                "output_path": str(output_path.resolve()),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
