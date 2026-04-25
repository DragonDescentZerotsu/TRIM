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

from trim.reasoning.agent_tools import (
    DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
    build_all_task_tool_manifests,
)
from trim.utils.io import save_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build simple task manifests for TRIM agent tools."
    )
    parser.add_argument("--task", action="append", default=None, help="Optional task name. Repeat for multiple tasks.")
    parser.add_argument("--feature-set-name", default=DEFAULT_AGENT_TOOL_FEATURE_SET_NAME)
    parser.add_argument("--dataset-root", default="data/processed/tdc_no_conflict_labels_salt_removed")
    parser.add_argument("--cache-root", default="data/cache/tdc_mol_fingerprints")
    parser.add_argument("--global-top-k", type=int, default=10)
    parser.add_argument("--local-top-term-k", type=int, default=8)
    parser.add_argument("--local-top-k-pos", type=int, default=3)
    parser.add_argument("--local-top-k-neg", type=int, default=3)
    parser.add_argument("--allow-same-scaffold", action="store_true")
    parser.add_argument("--manifest-root", default=str(DEFAULT_AGENT_TOOL_MANIFEST_ROOT))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_all_task_tool_manifests(
        tasks=args.task,
        feature_set_name=args.feature_set_name,
        dataset_root=args.dataset_root,
        cache_root=args.cache_root,
        global_top_k=args.global_top_k,
        local_top_term_k=args.local_top_term_k,
        local_top_k_pos=args.local_top_k_pos,
        local_top_k_neg=args.local_top_k_neg,
        strict_cross_scaffold_pairs=not args.allow_same_scaffold,
        manifest_root=args.manifest_root,
    )
    summary_path = Path(args.manifest_root) / args.feature_set_name / "manifest_index.json"
    save_json(summary_path, summary)
    print(summary_path.resolve())
    print(f"num_tasks={summary['num_tasks']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
