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

from trim.reasoning.evidence.global_evidence import (
    build_default_global_evidence_output_dir,
    extract_global_evidence_for_split,
)
from trim.utils.io import save_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract per-sample global EBM reasoning evidence from an existing TRIM model bundle."
    )
    parser.add_argument("--bundle", required=True, help="Path to a global EBM model_bundle.pkl")
    parser.add_argument("--split", default="valid", help="Dataset split to explain")
    parser.add_argument("--dataset-root", default="data/processed/tdc_no_conflict_labels_salt_removed")
    parser.add_argument("--top-k", type=int, default=10, help="Number of highest-absolute-contribution features to keep")
    parser.add_argument("--sample-index", type=int, action="append", default=None, help="Optional sample index to export")
    parser.add_argument("--max-samples", type=int, default=None, help="Optional cap on exported samples")
    parser.add_argument("--prompt-root", default=None, help="Optional prompt root used to recover task label semantics")
    parser.add_argument(
        "--include-local-trend",
        action="store_true",
        help="Include local term-curve trend estimates in the exported evidence.",
    )
    parser.add_argument(
        "--include-intro",
        action="store_true",
        help="Include a short top-feature overview sentence at the start of global_middle_draft.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Optional output directory. Defaults to outputs/reasoning_evidence/global/<experiment>/<task>/<feature_set>/<split>",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle_path = Path(args.bundle).expanduser()
    if not bundle_path.is_absolute():
        bundle_path = (Path.cwd() / bundle_path).resolve()
    else:
        bundle_path = bundle_path.resolve()

    output_dir = args.output_dir
    if output_dir is None:
        output_dir = build_default_global_evidence_output_dir(bundle_path=bundle_path, split=args.split)

    payload = extract_global_evidence_for_split(
        bundle_path=bundle_path,
        split=args.split,
        dataset_root=args.dataset_root,
        top_k=args.top_k,
        sample_indices=args.sample_index,
        max_samples=args.max_samples,
        prompt_root=args.prompt_root,
        output_dir=output_dir,
        include_local_trend=args.include_local_trend,
        include_intro=args.include_intro,
    )

    manifest_path = Path(output_dir) / "manifest.json"
    manifest_payload = {
        key: value
        for key, value in payload.items()
        if key != "records"
    }
    save_json(manifest_path, manifest_payload)
    print(f"Wrote {payload['num_records']} global evidence files to {Path(output_dir).resolve()}")
    print(f"Manifest: {manifest_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
