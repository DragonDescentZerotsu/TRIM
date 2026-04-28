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
from trim.reasoning.evidence.local_evidence import (
    DEFAULT_RANDOM_TOP_TERM_MAX,
    DEFAULT_RANDOM_TOP_TERM_MIN,
    DEFAULT_TOP_TERM_K_PER_NEIGHBOR,
    LOCAL_TERM_SELECTION_MODES,
    extract_local_evidence_for_split,
)
from trim.utils.io import load_json, save_json
from trim.utils.paths import resolve_project_path, serialize_project_path


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
    parser.add_argument(
        "--evidence-mode",
        choices=("global", "local", "both"),
        default="both",
        help="Which evidence family to export. Defaults to both for backward compatibility.",
    )
    parser.add_argument("--include-global-intro", action="store_true")
    parser.add_argument("--include-global-local-trend", action="store_true")
    parser.add_argument(
        "--local-term-selection-mode",
        choices=LOCAL_TERM_SELECTION_MODES,
        default="ranked_top_k",
        help=(
            "How to select pair terms for local per-neighbor middle drafts. ranked_top_k preserves the legacy "
            "top-k ranked behavior; random_k_ranked samples a per-neighbor term count; top_k_shuffled selects "
            "top-k then shuffles display order."
        ),
    )
    parser.add_argument(
        "--local-top-term-k",
        type=int,
        default=None,
        help=(
            "Override manifest local_tool.top_term_k_per_neighbor. Use 6 with top_k_shuffled for the shuffled-top6 "
            "evidence variant."
        ),
    )
    parser.add_argument("--local-random-top-term-min", type=int, default=DEFAULT_RANDOM_TOP_TERM_MIN)
    parser.add_argument("--local-random-top-term-max", type=int, default=DEFAULT_RANDOM_TOP_TERM_MAX)
    parser.add_argument("--local-random-seed", type=int, default=0)
    return parser.parse_args()


def _resolve_path(path_like: str | Path) -> Path:
    return resolve_project_path(path_like)


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


def _local_variant_requested(args: argparse.Namespace) -> bool:
    return (
        args.local_term_selection_mode != "ranked_top_k"
        or args.local_top_term_k is not None
        or int(args.local_random_top_term_min) != DEFAULT_RANDOM_TOP_TERM_MIN
        or int(args.local_random_top_term_max) != DEFAULT_RANDOM_TOP_TERM_MAX
        or int(args.local_random_seed) != 0
    )


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
    run_global = args.evidence_mode in {"global", "both"}
    run_local = args.evidence_mode in {"local", "both"}
    if run_local and _local_variant_requested(args) and args.local_output_root == DEFAULT_LOCAL_OUTPUT_ROOT:
        raise ValueError(
            "Local evidence variant parameters were requested, but --local-output-root still points to the legacy "
            f"default cache ({DEFAULT_LOCAL_OUTPUT_ROOT}). Choose a variant-specific output root."
        )

    for task_row in task_rows:
        task = str(task_row["task"])
        manifest_path = _resolve_path(task_row["manifest_path"])
        task_manifest = load_json(manifest_path)
        bundle_paths = {
            str(name): str(_resolve_path(path_like))
            for name, path_like in dict(task_manifest["bundle_paths"]).items()
        }
        local_tool = dict(task_manifest["local_tool"])

        print(f"[reasoning-evidence] task={task}")
        for split in splits:
            global_output_dir = global_output_root / task / split
            local_output_dir = local_output_root / task / split
            global_payload = None
            local_payload = None

            if run_global:
                print(f"[reasoning-evidence] task={task} split={split} global")
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

            if run_local:
                print(f"[reasoning-evidence] task={task} split={split} local")
                local_top_term_k = (
                    int(args.local_top_term_k)
                    if args.local_top_term_k is not None
                    else int(local_tool.get("top_term_k_per_neighbor", DEFAULT_TOP_TERM_K_PER_NEIGHBOR))
                )
                local_payload = extract_local_evidence_for_split(
                    pos_bundle_path=bundle_paths["pos_bundle_path"],
                    neg_bundle_path=bundle_paths["neg_bundle_path"],
                    split=split,
                    dataset_root=dataset_root,
                    cache_root=cache_root,
                    top_k_pos=int(local_tool["top_k_pos"]),
                    top_k_neg=int(local_tool["top_k_neg"]),
                    top_term_k=local_top_term_k,
                    term_selection_mode=args.local_term_selection_mode,
                    random_top_term_min=args.local_random_top_term_min,
                    random_top_term_max=args.local_random_top_term_max,
                    random_seed=args.local_random_seed,
                    strict_cross_scaffold_pairs=bool(local_tool["strict_cross_scaffold_pairs"]),
                    prompt_root=args.prompt_root,
                    output_dir=local_output_dir,
                )
                _save_child_manifest(local_output_dir, local_payload)

            summary_rows.append(
                {
                    "task": task,
                    "split": split,
                    "global_num_records": int(global_payload["num_records"]) if global_payload is not None else None,
                    "local_num_records": int(local_payload["num_records"]) if local_payload is not None else None,
                    "global_output_dir": serialize_project_path(global_output_dir) if run_global else None,
                    "local_output_dir": serialize_project_path(local_output_dir) if run_local else None,
                }
            )

    summary_payload = {
        "schema_version": "trim_reasoning_full_evidence_v1",
        "manifest_index_path": serialize_project_path(manifest_index_path),
        "splits": splits,
        "tasks": [str(row["task"]) for row in task_rows],
        "evidence_mode": args.evidence_mode,
        "dataset_root": serialize_project_path(dataset_root),
        "cache_root": serialize_project_path(cache_root),
        "global_output_root": serialize_project_path(global_output_root),
        "local_output_root": serialize_project_path(local_output_root),
        "local_term_selection": {
            "mode": str(args.local_term_selection_mode),
            "top_term_k_override": int(args.local_top_term_k) if args.local_top_term_k is not None else None,
            "random_top_term_min": int(args.local_random_top_term_min),
            "random_top_term_max": int(args.local_random_top_term_max),
            "random_seed": int(args.local_random_seed),
        },
        "rows": summary_rows,
    }

    if run_global:
        save_json(global_output_root / "summary.json", summary_payload)
    if run_local:
        save_json(local_output_root / "summary.json", summary_payload)
    print(json.dumps(summary_payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
