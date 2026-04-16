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

from trim.reasoning.evidence.global_evidence import extract_global_evidence_for_split
from trim.reasoning.evidence.local_evidence import extract_local_evidence_for_split
from trim.utils.io import load_json, save_json


DEFAULT_MANIFEST_INDEX = (
    "outputs/reasoning_agent_tools/manifests/"
    "fg_top_level+rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts/manifest_index.json"
)
DEFAULT_GLOBAL_OUTPUT_ROOT = "outputs/reasoning_evidence/global/all_tasks_core_pka_no_fr_keep_nan"
DEFAULT_LOCAL_OUTPUT_ROOT = "outputs/reasoning_evidence/local/all_tasks_core_pka_no_fr_counts"
DEFAULT_DATASET_ROOT = "data/processed/tdc_no_conflict_labels_salt_removed"
DEFAULT_CACHE_ROOT = "data/cache/tdc_mol_fingerprints"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract full global/local reasoning evidence for all tasks defined in a task-manifest index."
    )
    parser.add_argument(
        "--manifest-index",
        default=DEFAULT_MANIFEST_INDEX,
        help="Manifest index JSON listing all tasks and per-task manifest paths",
    )
    parser.add_argument(
        "--split",
        action="append",
        dest="splits",
        default=None,
        help="Split to export. Repeat for multiple splits. Defaults to train, valid, test.",
    )
    parser.add_argument(
        "--task",
        action="append",
        dest="tasks",
        default=None,
        help="Optional task filter. Repeat to export multiple tasks.",
    )
    parser.add_argument("--dataset-root", default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--cache-root", default=DEFAULT_CACHE_ROOT)
    parser.add_argument("--prompt-root", default=None)
    parser.add_argument("--global-output-root", default=DEFAULT_GLOBAL_OUTPUT_ROOT)
    parser.add_argument("--local-output-root", default=DEFAULT_LOCAL_OUTPUT_ROOT)
    parser.add_argument("--include-global-intro", action="store_true")
    parser.add_argument("--include-global-local-trend", action="store_true")
    return parser.parse_args()


def _resolve_path(path_like: str | Path) -> Path:
    path = Path(path_like).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (Path.cwd() / path).resolve()


def _selected_tasks(index_payload: dict[str, object], requested_tasks: list[str] | None) -> list[dict[str, object]]:
    tasks = list(index_payload["tasks"])
    if requested_tasks is None:
        return tasks
    requested_set = set(requested_tasks)
    selected = [row for row in tasks if str(row["task"]) in requested_set]
    missing = sorted(requested_set.difference({str(row["task"]) for row in selected}))
    if missing:
        raise ValueError(f"Tasks not found in manifest index: {missing}")
    return selected


def _save_child_manifest(output_dir: Path, payload: dict[str, object]) -> None:
    manifest_path = output_dir / "manifest.json"
    manifest_payload = {key: value for key, value in payload.items() if key != "records"}
    save_json(manifest_path, manifest_payload)


def main() -> int:
    args = parse_args()
    manifest_index_path = _resolve_path(args.manifest_index)
    index_payload = load_json(manifest_index_path)

    splits = args.splits or ["train", "valid", "test"]
    task_rows = _selected_tasks(index_payload, args.tasks)

    global_output_root = _resolve_path(args.global_output_root)
    local_output_root = _resolve_path(args.local_output_root)
    dataset_root = _resolve_path(args.dataset_root)
    cache_root = _resolve_path(args.cache_root)

    summary_rows: list[dict[str, object]] = []

    for task_row in task_rows:
        task = str(task_row["task"])
        manifest_path = Path(str(task_row["manifest_path"])).resolve()
        task_manifest = load_json(manifest_path)
        bundle_paths = dict(task_manifest["bundle_paths"])
        local_tool = dict(task_manifest["local_tool"])

        print(f"[reasoning-evidence] task={task}")
        for split in splits:
            print(f"[reasoning-evidence] task={task} split={split} global")
            global_output_dir = global_output_root / task / split
            global_payload = extract_global_evidence_for_split(
                bundle_path=bundle_paths["global_bundle_path"],
                split=split,
                dataset_root=dataset_root,
                prompt_root=args.prompt_root,
                output_dir=global_output_dir,
                include_local_trend=args.include_global_local_trend,
                include_intro=args.include_global_intro,
            )
            _save_child_manifest(global_output_dir, global_payload)

            print(f"[reasoning-evidence] task={task} split={split} local")
            local_output_dir = local_output_root / task / split
            local_payload = extract_local_evidence_for_split(
                pos_bundle_path=bundle_paths["pos_bundle_path"],
                neg_bundle_path=bundle_paths["neg_bundle_path"],
                split=split,
                dataset_root=dataset_root,
                cache_root=cache_root,
                top_k_pos=int(local_tool["top_k_pos"]),
                top_k_neg=int(local_tool["top_k_neg"]),
                top_term_k=int(local_tool["top_term_k_per_neighbor"]),
                strict_cross_scaffold_pairs=bool(local_tool["strict_cross_scaffold_pairs"]),
                prompt_root=args.prompt_root,
                output_dir=local_output_dir,
            )
            _save_child_manifest(local_output_dir, local_payload)

            summary_rows.append(
                {
                    "task": task,
                    "split": split,
                    "global_num_records": int(global_payload["num_records"]),
                    "local_num_records": int(local_payload["num_records"]),
                    "global_output_dir": str(global_output_dir.resolve()),
                    "local_output_dir": str(local_output_dir.resolve()),
                }
            )

    summary_payload = {
        "schema_version": "trim_reasoning_full_evidence_v1",
        "manifest_index_path": str(manifest_index_path),
        "splits": splits,
        "tasks": [str(row["task"]) for row in task_rows],
        "dataset_root": str(dataset_root),
        "cache_root": str(cache_root),
        "global_output_root": str(global_output_root),
        "local_output_root": str(local_output_root),
        "rows": summary_rows,
    }

    save_json(global_output_root / "summary.json", summary_payload)
    save_json(local_output_root / "summary.json", summary_payload)
    print(json.dumps(summary_payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
