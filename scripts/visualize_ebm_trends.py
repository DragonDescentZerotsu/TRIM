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

from trim.evaluation.ebm_visualization import (
    export_combined_ebm_pdf,
    export_global_curves,
    export_pair_heatmaps,
)
from trim.utils.io import load_pickle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Visualize global and pairwise EBM contribution trends.")
    parser.add_argument("--global-bundle-path", default=None)
    parser.add_argument("--pair-bundle-path", action="append", dest="pair_bundle_paths", default=None)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--global-top-k", type=int, default=12)
    parser.add_argument("--pair-top-k", type=int, default=9)
    parser.add_argument("--selected-feature", action="append", dest="selected_features", default=None)
    parser.add_argument("--feature-prefix", action="append", dest="feature_prefixes", default=None)
    parser.add_argument("--global-plots-per-figure", type=int, default=12)
    parser.add_argument("--pair-plots-per-figure", type=int, default=9)
    parser.add_argument("--combined-pdf-path", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload: dict[str, object] = {}
    global_bundle = load_pickle(args.global_bundle_path) if args.global_bundle_path else None
    pair_bundles = [load_pickle(path) for path in args.pair_bundle_paths] if args.pair_bundle_paths else []

    if args.global_bundle_path:
        payload["global"] = export_global_curves(
            bundle=global_bundle,
            output_dir=output_dir / "global",
            top_k=args.global_top_k,
            selected_feature_names=args.selected_features,
            selected_feature_prefixes=args.feature_prefixes,
            plots_per_figure=args.global_plots_per_figure,
        )

    if args.pair_bundle_paths:
        payload["pairwise"] = []
        for pair_bundle_path, bundle in zip(args.pair_bundle_paths, pair_bundles):
            pair_payload = export_pair_heatmaps(
                bundle=bundle,
                output_dir=output_dir / str(bundle["model_type"]),
                top_k=args.pair_top_k,
                selected_feature_names=args.selected_features,
                selected_feature_prefixes=args.feature_prefixes,
                plots_per_figure=args.pair_plots_per_figure,
            )
            pair_payload["bundle_path"] = str(Path(pair_bundle_path).resolve())
            pair_payload["model_type"] = str(bundle["model_type"])
            payload["pairwise"].append(pair_payload)

    if args.combined_pdf_path:
        payload["combined_pdf"] = export_combined_ebm_pdf(
            output_pdf_path=args.combined_pdf_path,
            global_bundle=global_bundle,
            pair_bundles=pair_bundles,
            global_top_k=args.global_top_k,
            pair_top_k=args.pair_top_k,
            selected_feature_names=args.selected_features,
            selected_feature_prefixes=args.feature_prefixes,
        )

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
