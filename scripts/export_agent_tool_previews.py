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

from trim.data.datasets import load_tdc_split
from trim.reasoning.agent_tools import (
    DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
    TaskReasoningAgentTools,
    load_task_tool_manifest,
)
from trim.utils.io import save_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export preview JSON files for get_mol_properties_and_fg and compare_similar_mols."
    )
    parser.add_argument("--task", action="append", default=None, help="Optional task name. Repeat for multiple tasks.")
    parser.add_argument("--split", default="valid")
    parser.add_argument("--sample-index", type=int, default=0)
    parser.add_argument("--feature-set-name", default=DEFAULT_AGENT_TOOL_FEATURE_SET_NAME)
    parser.add_argument("--manifest-root", default=str(DEFAULT_AGENT_TOOL_MANIFEST_ROOT))
    parser.add_argument("--dataset-root", default="data/processed/tdc_no_conflict_labels_salt_removed")
    parser.add_argument("--cache-root", default="data/cache/tdc_mol_fingerprints")
    parser.add_argument("--output-root", default="outputs/reasoning_agent_tools/previews")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_root = Path(args.manifest_root)
    feature_dir = manifest_root / args.feature_set_name
    if args.task:
        tasks = list(args.task)
    else:
        tasks = sorted(path.stem for path in feature_dir.glob("*.json") if path.stem != "manifest_index")

    output_root = Path(args.output_root) / args.feature_set_name / args.split / f"sample_{args.sample_index:05d}"
    manifest_index = {
        "feature_set_name": args.feature_set_name,
        "split": args.split,
        "sample_index": int(args.sample_index),
        "tasks": {},
    }

    for task in tasks:
        load_task_tool_manifest(
            task=task,
            feature_set_name=args.feature_set_name,
            manifest_root=manifest_root,
        )
        split_payload = load_tdc_split(task, args.split, data_root=args.dataset_root)
        smiles = split_payload.smiles[args.sample_index]
        tools = TaskReasoningAgentTools.from_task(
            task=task,
            feature_set_name=args.feature_set_name,
            manifest_root=manifest_root,
            dataset_root=args.dataset_root,
            cache_root=args.cache_root,
        )

        global_payload = tools.get_mol_properties_and_fg(smiles)
        local_payload = tools.compare_similar_mols(smiles)

        task_dir = output_root / task
        global_path = task_dir / "get_mol_properties_and_fg.json"
        local_path = task_dir / "compare_similar_mols.json"
        save_json(global_path, global_payload)
        save_json(local_path, local_payload)
        manifest_index["tasks"][task] = {
            "smiles": smiles,
            "global_preview": str(global_path.resolve()),
            "local_preview": str(local_path.resolve()),
        }

    manifest_path = output_root / "manifest.json"
    save_json(manifest_path, manifest_index)
    print(manifest_path.resolve())
    print(f"num_tasks={len(tasks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
