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

from trim.reasoning.agent_tools import (
    DEFAULT_AGENT_TOOL_CACHE_ROOT,
    DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
    DEFAULT_AGENT_TOOL_PREWARM_SUMMARY_ROOT,
    SUPPORTED_AGENT_TOOL_NAMES,
    prewarm_agent_tool_cache,
)
from trim.reasoning.task_user_prompts import DEFAULT_TASK_MANIFEST_INDEX
from trim.utils.paths import DEFAULT_PROCESSED_DATA_ROOT, DEFAULT_SIMILARITY_CACHE_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prewarm agent tool payload cache for all selected tasks and SMILES."
    )
    parser.add_argument(
        "--task",
        action="append",
        default=None,
        help="Optional task name. Repeat for multiple tasks. Defaults to all tasks in the manifest index.",
    )
    parser.add_argument(
        "--split",
        action="append",
        default=None,
        help="Dataset split(s) to scan for SMILES. Repeat for multiple splits. Defaults to train+valid+test.",
    )
    parser.add_argument(
        "--tool",
        action="append",
        default=None,
        choices=list(SUPPORTED_AGENT_TOOL_NAMES),
        help="Tool(s) to prewarm. Repeat to select a subset. Defaults to both tools.",
    )
    parser.add_argument(
        "--manifest-index",
        default=str(DEFAULT_TASK_MANIFEST_INDEX),
        help="Manifest index JSON used to discover task names when --task is omitted.",
    )
    parser.add_argument("--feature-set-name", default=DEFAULT_AGENT_TOOL_FEATURE_SET_NAME)
    parser.add_argument("--manifest-root", default=str(DEFAULT_AGENT_TOOL_MANIFEST_ROOT))
    parser.add_argument("--dataset-root", default=str(DEFAULT_PROCESSED_DATA_ROOT))
    parser.add_argument(
        "--cache-root",
        default=str(DEFAULT_SIMILARITY_CACHE_ROOT),
        help="Similarity cache root used by compare_similar_mols.",
    )
    parser.add_argument(
        "--tool-cache-root",
        default=str(DEFAULT_AGENT_TOOL_CACHE_ROOT),
        help="Output root for saved tool payload JSON cache files.",
    )
    parser.add_argument(
        "--summary-path",
        default=str(DEFAULT_AGENT_TOOL_PREWARM_SUMMARY_ROOT / DEFAULT_AGENT_TOOL_FEATURE_SET_NAME / "manifest.json"),
        help="Where to save the run summary JSON.",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=1,
        help="Number of worker processes to use per task when prewarming SMILES.",
    )
    parser.add_argument(
        "--max-smiles-per-task",
        type=int,
        default=None,
        help="Optional debug cap for the number of unique SMILES to prewarm per task.",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Recompute payloads even when the current cache file already exists.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = prewarm_agent_tool_cache(
        tasks=args.task,
        splits=args.split,
        manifest_index_path=args.manifest_index,
        feature_set_name=args.feature_set_name,
        manifest_root=args.manifest_root,
        dataset_root=args.dataset_root,
        cache_root=args.cache_root,
        tool_cache_root=args.tool_cache_root,
        tool_names=args.tool,
        max_concurrency=args.max_concurrency,
        force_refresh=args.force_refresh,
        max_smiles_per_task=args.max_smiles_per_task,
        summary_path=args.summary_path,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
