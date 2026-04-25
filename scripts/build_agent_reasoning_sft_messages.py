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

from trim.reasoning.agent_sft import (
    DEFAULT_AGENT_REASONING_SFT_OUTPUT_ROOT,
    DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
    DEFAULT_NEIGHBOR_LEVEL_REWRITE_OUTPUT_ROOT,
    DEFAULT_REWRITE_FILTER_ROOT,
    DEFAULT_REWRITE_MODEL,
    DEFAULT_REWRITE_OUTPUT_ROOT,
    DEFAULT_REWRITE_PROVIDER,
    SFT_MODE_FULL,
    SFT_MODE_LOCAL_NEIGHBOR_ONLY,
    SFT_MODES,
    DEFAULT_TOOL_CACHE_ROOT,
    build_agent_reasoning_sft_datasets,
)
from trim.reasoning.task_user_prompts import DEFAULT_TASK_MANIFEST_INDEX, DEFAULT_TASK_USER_PROMPT_ROOT
from trim.utils.paths import DEFAULT_PROCESSED_DATA_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build per-task agent reasoning SFT datasets in OpenAI messages format."
    )
    parser.add_argument("--split", default="train")
    parser.add_argument(
        "--sft-mode",
        choices=SFT_MODES,
        default=SFT_MODE_FULL,
        help=(
            "Transcript assembly mode. 'full' keeps the current global+local+hybrid format; "
            "'global_only' and 'local_only' build ablation datasets from samples where that teacher is correct; "
            "'local_neighbor_only' builds local-only transcripts from six per-neighbor rewrites plus a summary rewrite."
        ),
    )
    parser.add_argument("--task", action="append", default=None, help="Optional task name. Repeat for multiple tasks.")
    parser.add_argument(
        "--manifest-index",
        default=str(DEFAULT_TASK_MANIFEST_INDEX),
        help="Manifest index JSON used to discover task names when --task is omitted.",
    )
    parser.add_argument(
        "--rewrite-output-root",
        default=str(DEFAULT_REWRITE_OUTPUT_ROOT),
        help="Root directory containing saved global/local/hybrid rewrite outputs.",
    )
    parser.add_argument(
        "--rewrite-filter-root",
        default=str(DEFAULT_REWRITE_FILTER_ROOT),
        help="Root directory containing kept_records.json files with global/local correctness flags.",
    )
    parser.add_argument("--provider", default=DEFAULT_REWRITE_PROVIDER)
    parser.add_argument("--model", default=DEFAULT_REWRITE_MODEL)
    parser.add_argument("--dataset-root", default=str(DEFAULT_PROCESSED_DATA_ROOT))
    parser.add_argument("--output-root", default=str(DEFAULT_AGENT_REASONING_SFT_OUTPUT_ROOT))
    parser.add_argument("--prompt-root", default=str(DEFAULT_TASK_USER_PROMPT_ROOT))
    parser.add_argument("--feature-set-name", default=DEFAULT_AGENT_TOOL_FEATURE_SET_NAME)
    parser.add_argument("--manifest-root", default=str(DEFAULT_AGENT_TOOL_MANIFEST_ROOT))
    parser.add_argument("--cache-root", default=str(DEFAULT_TOOL_CACHE_ROOT))
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=1,
        help="Number of worker processes to use per task when assembling samples.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Rebuild task JSONL files from scratch instead of resuming from existing outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rewrite_output_root = args.rewrite_output_root
    if (
        args.sft_mode == SFT_MODE_LOCAL_NEIGHBOR_ONLY
        and str(args.rewrite_output_root) == str(DEFAULT_REWRITE_OUTPUT_ROOT)
    ):
        rewrite_output_root = str(DEFAULT_NEIGHBOR_LEVEL_REWRITE_OUTPUT_ROOT)
    summary = build_agent_reasoning_sft_datasets(
        tasks=args.task,
        split=args.split,
        sft_mode=args.sft_mode,
        manifest_index_path=args.manifest_index,
        rewrite_output_root=rewrite_output_root,
        rewrite_filter_root=args.rewrite_filter_root,
        provider=args.provider,
        model=args.model,
        dataset_root=args.dataset_root,
        output_root=args.output_root,
        prompt_root=args.prompt_root,
        feature_set_name=args.feature_set_name,
        manifest_root=args.manifest_root,
        cache_root=args.cache_root,
        max_concurrency=args.max_concurrency,
        skip_existing=not args.overwrite,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
