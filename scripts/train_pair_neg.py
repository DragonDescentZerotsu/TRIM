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
from trim.models.retrieval import CachedSimilarityRetriever
from trim.training.pair_training import PairTrainingConfig, train_pair_task
from trim.utils.paths import DEFAULT_PROCESSED_DATA_ROOT, DEFAULT_SIMILARITY_CACHE_ROOT

try:
    from tqdm.auto import tqdm
except ImportError:
    def tqdm(iterable=None, **kwargs):
        return iterable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the negative-neighbor pairwise EBM.")
    parser.add_argument("--tasks", default=None)
    parser.add_argument(
        "--feature-config",
        action="append",
        dest="feature_configs",
        default=None,
    )
    parser.add_argument("--data-root", default=str(DEFAULT_PROCESSED_DATA_ROOT))
    parser.add_argument("--cache-root", default=str(DEFAULT_SIMILARITY_CACHE_ROOT))
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--allow-same-scaffold", action="store_true")
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--n-jobs", type=int, default=1)
    parser.add_argument("--max-bins", type=int, default=256)
    parser.add_argument("--output-dir", default="outputs/models/pair_ebm")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tasks = (
        [item.strip() for item in args.tasks.split(",") if item.strip()]
        if args.tasks
        else list_tasks(args.data_root)
    )
    feature_configs = args.feature_configs or ["configs/features/rdkit_descriptors_and_pka_easy_to_NLP_Lv1.json"]
    feature_bundle = build_feature_source_bundle(feature_configs)
    retriever = CachedSimilarityRetriever(cache_root=args.cache_root, data_root=args.data_root)
    config = PairTrainingConfig(
        neighbor_label=0,
        top_k=args.top_k,
        strict_cross_scaffold_pairs=not args.allow_same_scaffold,
        random_state=args.random_state,
        n_jobs=args.n_jobs,
        max_bins=args.max_bins,
    )
    print(
        f"[pair-train] model=neg num_tasks={len(tasks)} "
        f"feature_set={feature_bundle['feature_set_name']} top_k={args.top_k} "
        f"strict_cross_scaffold_pairs={not args.allow_same_scaffold} n_jobs={args.n_jobs}"
    )
    results = []
    for task in tqdm(tasks, desc="Train neg tasks"):
        results.append(
            train_pair_task(
            task=task,
            feature_bundle=feature_bundle,
            retriever=retriever,
            config=config,
            output_dir=args.output_dir,
        )
        )
    print(json.dumps({"num_tasks": len(results), "tasks": tasks}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
