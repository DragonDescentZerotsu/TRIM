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

from trim.data.datasets import list_tasks
from trim.features.table_loader import build_feature_source_bundle
from trim.models.global_ebm import build_ebm_params
from trim.training.global_training import train_global_task
from trim.utils.paths import DEFAULT_PROCESSED_DATA_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train global EBM models for TDC binary tasks.")
    parser.add_argument(
        "--tasks",
        default=None,
        help="Comma-separated task names. Defaults to all tasks under the processed train split.",
    )
    parser.add_argument(
        "--feature-config",
        action="append",
        dest="feature_configs",
        default=None,
        help="Path to a feature config JSON. Can be repeated.",
    )
    parser.add_argument("--data-root", default=str(DEFAULT_PROCESSED_DATA_ROOT))
    parser.add_argument("--train-split", default="train")
    parser.add_argument("--valid-split", default="valid")
    parser.add_argument("--interactions", type=int, default=0)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--ebm-jobs", type=int, default=1)
    parser.add_argument("--scale-features", action="store_true")
    nan_group = parser.add_mutually_exclusive_group()
    nan_group.add_argument(
        "--keep-nan-columns",
        dest="keep_nan_columns",
        action="store_true",
        help=(
            "Keep feature columns that contain some NaN values in the train split. "
            "This is now the default behavior."
        ),
    )
    nan_group.add_argument(
        "--drop-nan-columns",
        dest="keep_nan_columns",
        action="store_false",
        help="Drop any feature column that contains a NaN value in the train split.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/models/global_ebm/default_experiment",
    )
    parser.set_defaults(keep_nan_columns=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tasks = (
        [item.strip() for item in args.tasks.split(",") if item.strip()]
        if args.tasks
        else list_tasks(args.data_root)
    )
    feature_configs = args.feature_configs or [
        "configs/features/fg_top_level_plus_rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts.json"
    ]
    feature_bundle = build_feature_source_bundle(feature_configs)
    ebm_params = build_ebm_params(
        interactions=args.interactions,
        random_state=args.random_state,
        n_jobs=args.ebm_jobs,
    )

    summaries = []
    for task in tasks:
        summaries.append(
            train_global_task(
                task=task,
                feature_bundle=feature_bundle,
                dataset_root=args.data_root,
                train_split_name=args.train_split,
                valid_split_name=args.valid_split,
                ebm_params=ebm_params,
                scale_features=args.scale_features,
                drop_any_nan_columns=not args.keep_nan_columns,
                output_dir=args.output_dir,
            )
        )
    print(json.dumps({"num_tasks": len(summaries), "tasks": tasks}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
