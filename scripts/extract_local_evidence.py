#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from trim.reasoning.evidence.local_evidence import (
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
    parser.add_argument("--top-term-k", type=int, default=6, help="Number of pair terms to keep per neighbor")
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
