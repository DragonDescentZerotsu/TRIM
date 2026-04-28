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

from trim.reasoning.evidence.local_evidence import (
    DEFAULT_RANDOM_TOP_TERM_MAX,
    DEFAULT_RANDOM_TOP_TERM_MIN,
    LOCAL_TERM_SELECTION_MODES,
    build_default_local_evidence_output_dir,
    extract_local_evidence_for_split,
)
from trim.utils.io import save_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract per-neighbor local pair-EBM reasoning evidence from existing TRIM pair bundles."
    )
    parser.add_argument("--pos-bundle", required=True, help="Path to pos_model_bundle.pkl")
    parser.add_argument("--neg-bundle", required=True, help="Path to neg_model_bundle.pkl")
    parser.add_argument("--split", default="valid", help="Dataset split to explain")
    parser.add_argument("--dataset-root", default="data/processed/tdc_no_conflict_labels_salt_removed")
    parser.add_argument("--cache-root", default="data/cache/tdc_mol_fingerprints")
    parser.add_argument("--top-k-pos", type=int, default=3, help="Number of positive neighbors to keep per sample")
    parser.add_argument("--top-k-neg", type=int, default=3, help="Number of negative neighbors to keep per sample")
    parser.add_argument("--top-term-k", type=int, default=8, help="Number of pair terms to keep per neighbor")
    parser.add_argument(
        "--term-selection-mode",
        choices=LOCAL_TERM_SELECTION_MODES,
        default="ranked_top_k",
        help=(
            "How to select pair terms for each neighbor middle draft. ranked_top_k preserves the legacy behavior; "
            "random_k_ranked samples a per-neighbor term count; top_k_shuffled selects top-k then shuffles display order."
        ),
    )
    parser.add_argument("--random-top-term-min", type=int, default=DEFAULT_RANDOM_TOP_TERM_MIN)
    parser.add_argument("--random-top-term-max", type=int, default=DEFAULT_RANDOM_TOP_TERM_MAX)
    parser.add_argument("--random-seed", type=int, default=0)
    parser.add_argument("--sample-index", type=int, action="append", default=None, help="Optional sample index to export")
    parser.add_argument("--max-samples", type=int, default=None, help="Optional cap on exported samples")
    parser.add_argument("--prompt-root", default=None, help="Optional prompt root used to recover task label semantics")
    parser.add_argument("--allow-same-scaffold", action="store_true", help="Allow same-scaffold neighbors")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Optional output directory. Defaults to outputs/reasoning_evidence/local/<experiment>/<task>/<feature_set>/<split>",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pos_bundle_path = Path(args.pos_bundle).expanduser()
    neg_bundle_path = Path(args.neg_bundle).expanduser()
    if not pos_bundle_path.is_absolute():
        pos_bundle_path = (Path.cwd() / pos_bundle_path).resolve()
    else:
        pos_bundle_path = pos_bundle_path.resolve()
    if not neg_bundle_path.is_absolute():
        neg_bundle_path = (Path.cwd() / neg_bundle_path).resolve()
    else:
        neg_bundle_path = neg_bundle_path.resolve()

    output_dir = args.output_dir
    if output_dir is None:
        if args.term_selection_mode != "ranked_top_k":
            raise ValueError(
                "Non-default term selection requires an explicit --output-dir so variant evidence does not overwrite "
                "the legacy local evidence cache."
            )
        output_dir = build_default_local_evidence_output_dir(pos_bundle_path=pos_bundle_path, split=args.split)

    payload = extract_local_evidence_for_split(
        pos_bundle_path=pos_bundle_path,
        neg_bundle_path=neg_bundle_path,
        split=args.split,
        dataset_root=args.dataset_root,
        cache_root=args.cache_root,
        top_k_pos=args.top_k_pos,
        top_k_neg=args.top_k_neg,
        top_term_k=args.top_term_k,
        term_selection_mode=args.term_selection_mode,
        random_top_term_min=args.random_top_term_min,
        random_top_term_max=args.random_top_term_max,
        random_seed=args.random_seed,
        strict_cross_scaffold_pairs=not args.allow_same_scaffold,
        sample_indices=args.sample_index,
        max_samples=args.max_samples,
        prompt_root=args.prompt_root,
        output_dir=output_dir,
    )

    manifest_path = Path(output_dir) / "manifest.json"
    manifest_payload = {
        key: value
        for key, value in payload.items()
        if key != "records"
    }
    save_json(manifest_path, manifest_payload)
    print(f"Wrote {payload['num_records']} local evidence files to {Path(output_dir).resolve()}")
    print(f"Manifest: {manifest_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
