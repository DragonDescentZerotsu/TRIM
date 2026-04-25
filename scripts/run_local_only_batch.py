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
from trim.utils.paths import serialize_project_path

try:
    from tqdm.auto import tqdm
except ImportError:
    def tqdm(iterable=None, **kwargs):
        return iterable


DEFAULT_FEATURE_CONFIG = "configs/features/fg_top_level.json"
DEFAULT_FEATURE_SET_NAME = "fg_top_level"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train pairwise models and evaluate local-only performance for one or more splits."
    )
    parser.add_argument("--tasks", default=None, help="Comma-separated task names. Defaults to all tasks.")
    parser.add_argument("--splits", default="valid,test", help="Comma-separated splits to evaluate.")
    parser.add_argument("--feature-config", default=DEFAULT_FEATURE_CONFIG)
    parser.add_argument("--feature-set-name", default=DEFAULT_FEATURE_SET_NAME)
    parser.add_argument("--python-executable", default=sys.executable)
    parser.add_argument("--max-parallel-tasks", type=int, default=4)
    parser.add_argument("--pair-n-jobs", type=int, default=16)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--allow-same-scaffold", action="store_true", default=True)
    parser.add_argument("--strict-cross-scaffold", action="store_true")
    parser.add_argument("--skip-training", action="store_true")
    parser.add_argument(
        "--pair-output-root",
        default="outputs/models/pair_ebm/fg_only_topk4_same_scaffold_njobs16",
    )
    parser.add_argument(
        "--local-output-root",
        default="outputs/metrics/local_only/fg_only_topk4_same_scaffold_njobs16",
    )
    parser.add_argument("--log-root", default="outputs/logs/local_only_batch_fg_only")
    parser.add_argument(
        "--summary-output",
        default="outputs/metrics/local_only_batch_summary_all16_fg_only.json",
    )
    return parser.parse_args()


def resolve_tasks(args: argparse.Namespace) -> list[str]:
    if args.tasks:
        return [item.strip() for item in args.tasks.split(",") if item.strip()]
    return list_tasks()


def resolve_splits(args: argparse.Namespace) -> list[str]:
    splits = [item.strip() for item in args.splits.split(",") if item.strip()]
    if not splits:
        raise ValueError("No splits selected.")
    return splits


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


def run_task_pipeline(task: str, splits: list[str], args: argparse.Namespace) -> list[dict[str, object]]:
    allow_same_scaffold_flag = build_allow_same_scaffold_flag(args.strict_cross_scaffold)
    pair_task_root = Path(args.pair_output_root) / task / args.feature_set_name
    log_root = Path(args.log_root) / task

    if not args.skip_training:
        pos_command = [
            args.python_executable,
            "-u",
            "scripts/train_pair_pos.py",
            "--tasks",
            task,
            "--feature-config",
            args.feature_config,
            "--top-k",
            str(args.top_k),
            "--n-jobs",
            str(args.pair_n_jobs),
            "--output-dir",
            args.pair_output_root,
            *allow_same_scaffold_flag,
        ]
        run_and_log(pos_command, log_root / "train_pair_pos.log")

        neg_command = [
            args.python_executable,
            "-u",
            "scripts/train_pair_neg.py",
            "--tasks",
            task,
            "--feature-config",
            args.feature_config,
            "--top-k",
            str(args.top_k),
            "--n-jobs",
            str(args.pair_n_jobs),
            "--output-dir",
            args.pair_output_root,
            *allow_same_scaffold_flag,
        ]
        run_and_log(neg_command, log_root / "train_pair_neg.log")

    pos_bundle_path = pair_task_root / "pos_model_bundle.pkl"
    neg_bundle_path = pair_task_root / "neg_model_bundle.pkl"
    if not pos_bundle_path.exists() or not neg_bundle_path.exists():
        raise FileNotFoundError(f"Missing pair bundles under {pair_task_root}")

    results: list[dict[str, object]] = []
    for split in splits:
        local_task_root = Path(args.local_output_root) / split / task
        local_command = [
            args.python_executable,
            "-u",
            "scripts/run_local_only.py",
            "--task",
            task,
            "--split",
            split,
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
        run_and_log(local_command, log_root / f"run_local_only_{split}.log")
        metrics_path = local_task_root / f"{task}__{split}_molecule_level_metrics.json"
        metrics_payload = load_json(metrics_path)
        results.append(
            {
                "task": task,
                "split": split,
                "metrics_path": serialize_project_path(metrics_path),
                "metrics": metrics_payload["metrics"]["local_only"],
                "logs": {
                    "train_pair_pos": serialize_project_path(log_root / "train_pair_pos.log"),
                    "train_pair_neg": serialize_project_path(log_root / "train_pair_neg.log"),
                    f"run_local_only_{split}": serialize_project_path(log_root / f"run_local_only_{split}.log"),
                },
            }
        )
    return results


def build_summary_rows(results: list[dict[str, object]]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for result in results:
        metrics = result["metrics"]
        rows.append(
            {
                "task": result["task"],
                "split": result["split"],
                "local_macro_f1": metrics["macro_f1"],
                "local_roc_auc": metrics["roc_auc"],
                "local_balanced_accuracy": metrics["balanced_accuracy"],
                "local_accuracy": metrics["accuracy"],
                "local_brier_score": metrics["brier_score"],
                "local_log_loss": metrics["log_loss"],
                "metrics_path": result["metrics_path"],
            }
        )
    return pd.DataFrame(rows).sort_values(by=["split", "local_macro_f1"], ascending=[True, False]).reset_index(drop=True)


def main() -> int:
    args = parse_args()
    if args.strict_cross_scaffold:
        args.allow_same_scaffold = False
    tasks = resolve_tasks(args)
    splits = resolve_splits(args)
    if not tasks:
        raise ValueError("No tasks selected for batch run.")

    print(
        f"[local-batch] num_tasks={len(tasks)} splits={','.join(splits)} "
        f"max_parallel_tasks={args.max_parallel_tasks} pair_n_jobs={args.pair_n_jobs} "
        f"top_k={args.top_k} strict_cross_scaffold_pairs={args.strict_cross_scaffold}"
    )

    results: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=args.max_parallel_tasks) as executor:
        future_to_task = {
            executor.submit(run_task_pipeline, task, splits, args): task
            for task in tasks
        }
        for future in tqdm(as_completed(future_to_task), total=len(future_to_task), desc="Completed tasks"):
            task = future_to_task[future]
            task_results = future.result()
            results.extend(task_results)
            metric_text = " ".join(
                f"{result['split']}_macro_f1={result['metrics']['macro_f1']:.4f}"
                for result in task_results
            )
            print(f"[local-batch] finished task={task} {metric_text}")

    summary_df = build_summary_rows(results)
    summary_json_path = Path(args.summary_output)
    summary_json_path.parent.mkdir(parents=True, exist_ok=True)
    summary_csv_path = summary_json_path.with_suffix(".csv")
    summary_df.to_csv(summary_csv_path, index=False)

    split_means = (
        summary_df.groupby("split", as_index=False)["local_macro_f1"]
        .mean()
        .sort_values(by="split")
        .to_dict(orient="records")
    )
    payload = {
        "config": {
            "tasks": tasks,
            "splits": splits,
            "feature_config": args.feature_config,
            "feature_set_name": args.feature_set_name,
            "pair_n_jobs": args.pair_n_jobs,
            "top_k": args.top_k,
            "strict_cross_scaffold_pairs": args.strict_cross_scaffold,
            "max_parallel_tasks": args.max_parallel_tasks,
            "python_executable": args.python_executable,
            "skip_training": args.skip_training,
        },
        "summary_csv": serialize_project_path(summary_csv_path),
        "split_macro_f1_means": split_means,
        "results": results,
    }
    save_json(summary_json_path, payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
