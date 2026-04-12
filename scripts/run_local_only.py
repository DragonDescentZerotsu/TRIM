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

from trim.evaluation.pair_eval import evaluate_local_system, save_local_evaluation
from trim.features.table_loader import build_feature_source_bundle
from trim.models.retrieval import CachedSimilarityRetriever
from trim.utils.paths import DEFAULT_PROCESSED_DATA_ROOT, DEFAULT_SIMILARITY_CACHE_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run molecule-level local-only evaluation.")
    parser.add_argument("--task", required=True)
    parser.add_argument("--split", default="test")
    parser.add_argument("--pos-bundle-path", required=True)
    parser.add_argument("--neg-bundle-path", required=True)
    parser.add_argument(
        "--feature-config",
        action="append",
        dest="feature_configs",
        default=None,
    )
    parser.add_argument("--data-root", default=str(DEFAULT_PROCESSED_DATA_ROOT))
    parser.add_argument("--cache-root", default=str(DEFAULT_SIMILARITY_CACHE_ROOT))
    parser.add_argument("--top-k-pos", type=int, default=3)
    parser.add_argument("--top-k-neg", type=int, default=3)
    parser.add_argument("--allow-same-scaffold", action="store_true")
    parser.add_argument("--output-dir", default="outputs/metrics/local_only")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    feature_configs = args.feature_configs or ["configs/features/rdkit_descriptors_and_pka_easy_to_NLP_Lv1.json"]
    print(
        f"[local-eval] task={args.task} split={args.split} "
        f"top_k_pos={args.top_k_pos} top_k_neg={args.top_k_neg} "
        f"strict_cross_scaffold_pairs={not args.allow_same_scaffold}"
    )
    feature_bundle = build_feature_source_bundle(feature_configs)
    retriever = CachedSimilarityRetriever(cache_root=args.cache_root, data_root=args.data_root)
    predictions_df, metrics_payload = evaluate_local_system(
        task=args.task,
        split=args.split,
        feature_source=feature_bundle["feature_source"],
        retriever=retriever,
        pos_bundle_path=args.pos_bundle_path,
        neg_bundle_path=args.neg_bundle_path,
        top_k_pos=args.top_k_pos,
        top_k_neg=args.top_k_neg,
        strict_cross_scaffold_pairs=not args.allow_same_scaffold,
    )
    payload = save_local_evaluation(
        predictions_df=predictions_df,
        metrics_payload=metrics_payload,
        output_dir=args.output_dir,
        task=args.task,
        split=args.split,
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
