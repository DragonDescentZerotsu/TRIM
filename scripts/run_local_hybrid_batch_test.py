#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from trim.data.datasets import list_tasks
from trim.utils.io import load_json, save_json

try:
    from tqdm.auto import tqdm
except ImportError:
    def tqdm(iterable=None, **kwargs):
        return iterable


DEFAULT_FEATURE_CONFIG = "configs/features/fg_top_level_plus_rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts.json"
DEFAULT_FEATURE_SET_NAME = "fg_top_level+rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run local-only and hybrid split evaluation in parallel using existing pairwise bundles."
    )
    parser.add_argument("--tasks", default=None, help="Comma-separated task names. Defaults to all tasks.")
    parser.add_argument("--split", default="test")
    parser.add_argument("--feature-config", default=DEFAULT_FEATURE_CONFIG)
    parser.add_argument("--feature-set-name", default=DEFAULT_FEATURE_SET_NAME)
    parser.add_argument("--python-executable", default=sys.executable)
    parser.add_argument("--max-parallel-tasks", type=int, default=16)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--allow-same-scaffold", action="store_true", default=True)
    parser.add_argument("--strict-cross-scaffold", action="store_true")
    parser.add_argument(
        "--pair-root-default",
        default="outputs/models/pair_ebm/all_tasks_topk4_same_scaffold_njobs16_fg_plus_rdkit_core_pka_no_fr_counts",
    )
    parser.add_argument(
        "--pair-root-override",
        action="append",
        default=["BBB_Martins=outputs/models/pair_ebm/all_tasks_topk4_same_scaffold_njobs16_fg_plus_rdkit_core_pka_no_fr_counts"],
        help="task=pair_root overrides; may be specified multiple times.",
    )
    parser.add_argument("--local-output-root", default="outputs/metrics/local_only/test_all16_fg_plus_rdkit_core_pka_no_fr_counts")
    parser.add_argument("--hybrid-output-root", default="outputs/metrics/hybrid/test_all16_fg_plus_rdkit_core_pka_no_fr_counts")
    parser.add_argument("--log-root", default="outputs/logs/local_hybrid_batch_test_core_pka_no_fr_counts")
    parser.add_argument("--global-model-root", default="outputs/models/global_ebm/all_tasks_njobs16_parallel_core_pka_no_fr_keep_nan")
    parser.add_argument("--summary-output", default="outputs/metrics/local_hybrid_batch_test_summary_all16_fg_plus_rdkit_core_pka_no_fr_counts.json")
    return parser.parse_args()


def parse_pair_root_overrides(raw_items: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for item in raw_items:
        if "=" not in item:
            raise ValueError(f"Expected override in task=path form, got: {item}")
        task, path = item.split("=", 1)
        mapping[task.strip()] = path.strip()
    return mapping


def resolve_tasks(args: argparse.Namespace) -> list[str]:
    if args.tasks:
        return [item.strip() for item in args.tasks.split(",") if item.strip()]
    return list_tasks()


def run_and_log(command: list[str], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as handle:
        handle.write("COMMAND:\n")
        handle.write(" ".join(command))
        handle.write("\n\n")
        handle.flush()
        process = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=False,
            text=True,
        )
    if process.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {process.returncode}: {' '.join(command)}")


def build_allow_same_scaffold_flag(strict_cross_scaffold: bool) -> list[str]:
    if strict_cross_scaffold:
        return []
    return ["--allow-same-scaffold"]


def evaluate_task(task: str, args: argparse.Namespace, pair_root_overrides: dict[str, str]) -> dict[str, object]:
    allow_same_scaffold_flag = build_allow_same_scaffold_flag(args.strict_cross_scaffold)
    pair_root = Path(pair_root_overrides.get(task, args.pair_root_default))
    pair_task_root = pair_root / task / args.feature_set_name
    local_task_root = Path(args.local_output_root) / task
    hybrid_task_root = Path(args.hybrid_output_root) / task
    log_root = Path(args.log_root) / task

    pos_bundle_path = pair_task_root / "pos_model_bundle.pkl"
    neg_bundle_path = pair_task_root / "neg_model_bundle.pkl"
    global_bundle_path = Path(args.global_model_root) / task / args.feature_set_name / "model_bundle.pkl"

    local_command = [
        args.python_executable,
        "-u",
        "scripts/run_local_only.py",
        "--task",
        task,
        "--split",
        args.split,
        "--pos-bundle-path",
        str(pos_bundle_path),
        "--neg-bundle-path",
        str(neg_bundle_path),
        "--feature-config",
        args.feature_config,
        "--top-k-pos",
        str(args.top_k),
        "--top-k-neg",
        str(args.top_k),
        "--output-dir",
        str(local_task_root),
        *allow_same_scaffold_flag,
    ]
    run_and_log(local_command, log_root / "run_local_only_test.log")

    hybrid_command = [
        args.python_executable,
        "-u",
        "scripts/run_hybrid.py",
        "--task",
        task,
        "--split",
        args.split,
        "--pos-bundle-path",
        str(pos_bundle_path),
        "--neg-bundle-path",
        str(neg_bundle_path),
        "--global-bundle-path",
        str(global_bundle_path),
        "--feature-config",
        args.feature_config,
        "--top-k-pos",
        str(args.top_k),
        "--top-k-neg",
        str(args.top_k),
        "--output-dir",
        str(hybrid_task_root),
        *allow_same_scaffold_flag,
    ]
    run_and_log(hybrid_command, log_root / "run_hybrid_test.log")

    hybrid_metrics_path = hybrid_task_root / f"{task}__{args.split}_molecule_level_metrics.json"
    metrics_payload = load_json(hybrid_metrics_path)
    return {
        "task": task,
        "metrics_path": str(hybrid_metrics_path.resolve()),
        "metrics": metrics_payload["metrics"],
        "logs": {
            "run_local_only_test": str((log_root / "run_local_only_test.log").resolve()),
            "run_hybrid_test": str((log_root / "run_hybrid_test.log").resolve()),
        },
    }


def build_summary_rows(results: list[dict[str, object]]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for result in results:
        metrics = result["metrics"]
        local_metrics = metrics["local_only"]
        global_metrics = metrics["global_only"]
        hybrid_metrics = metrics["hybrid"]
        rows.append(
            {
                "task": result["task"],
                "local_macro_f1": local_metrics["macro_f1"],
                "local_roc_auc": local_metrics["roc_auc"],
                "local_balanced_accuracy": local_metrics["balanced_accuracy"],
                "global_macro_f1": global_metrics["macro_f1"],
                "global_roc_auc": global_metrics["roc_auc"],
                "global_balanced_accuracy": global_metrics["balanced_accuracy"],
                "hybrid_macro_f1": hybrid_metrics["macro_f1"],
                "hybrid_roc_auc": hybrid_metrics["roc_auc"],
                "hybrid_balanced_accuracy": hybrid_metrics["balanced_accuracy"],
                "lambda": metrics["lambda"],
                "metrics_path": result["metrics_path"],
            }
        )
    return pd.DataFrame(rows).sort_values(by="hybrid_macro_f1", ascending=False).reset_index(drop=True)


def main() -> int:
    args = parse_args()
    if args.strict_cross_scaffold:
        args.allow_same_scaffold = False
    tasks = resolve_tasks(args)
    pair_root_overrides = parse_pair_root_overrides(args.pair_root_override)

    print(
        f"[batch-eval] split={args.split} num_tasks={len(tasks)} max_parallel_tasks={args.max_parallel_tasks} "
        f"top_k={args.top_k} strict_cross_scaffold_pairs={args.strict_cross_scaffold}"
    )

    results: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=args.max_parallel_tasks) as executor:
        future_to_task = {
            executor.submit(evaluate_task, task, args, pair_root_overrides): task
            for task in tasks
        }
        for future in tqdm(as_completed(future_to_task), total=len(future_to_task), desc="Completed tasks"):
            task = future_to_task[future]
            result = future.result()
            results.append(result)
            metrics = result["metrics"]
            print(
                f"[batch-test] finished task={task} "
                f"local_macro_f1={metrics['local_only']['macro_f1']:.4f} "
                f"hybrid_macro_f1={metrics['hybrid']['macro_f1']:.4f} "
                f"lambda={metrics['lambda']:.2f}"
            )

    summary_df = build_summary_rows(results)
    summary_json_path = Path(args.summary_output)
    summary_json_path.parent.mkdir(parents=True, exist_ok=True)
    summary_csv_path = summary_json_path.with_suffix(".csv")
    summary_df.to_csv(summary_csv_path, index=False)

    payload = {
        "config": {
            "tasks": tasks,
            "split": args.split,
            "feature_config": args.feature_config,
            "feature_set_name": args.feature_set_name,
            "top_k": args.top_k,
            "strict_cross_scaffold_pairs": args.strict_cross_scaffold,
            "max_parallel_tasks": args.max_parallel_tasks,
            "python_executable": args.python_executable,
            "pair_root_default": args.pair_root_default,
            "pair_root_overrides": pair_root_overrides,
        },
        "summary_csv": str(summary_csv_path.resolve()),
        "results": results,
    }
    save_json(summary_json_path, payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
