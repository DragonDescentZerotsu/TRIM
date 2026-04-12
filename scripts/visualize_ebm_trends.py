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

from trim.evaluation.ebm_visualization import export_global_curves, export_pair_heatmaps
from trim.utils.io import load_pickle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Visualize global and pairwise EBM contribution trends.")
    parser.add_argument("--global-bundle-path", default=None)
    parser.add_argument("--pair-bundle-path", action="append", dest="pair_bundle_paths", default=None)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--global-top-k", type=int, default=12)
    parser.add_argument("--pair-top-k", type=int, default=9)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload: dict[str, object] = {}
    if args.global_bundle_path:
        bundle = load_pickle(args.global_bundle_path)
        payload["global"] = export_global_curves(
            bundle=bundle,
            output_dir=output_dir / "global",
            top_k=args.global_top_k,
        )

    if args.pair_bundle_paths:
        payload["pairwise"] = []
        for pair_bundle_path in args.pair_bundle_paths:
            bundle = load_pickle(pair_bundle_path)
            pair_payload = export_pair_heatmaps(
                bundle=bundle,
                output_dir=output_dir / str(bundle["model_type"]),
                top_k=args.pair_top_k,
            )
            pair_payload["bundle_path"] = str(Path(pair_bundle_path).resolve())
            pair_payload["model_type"] = str(bundle["model_type"])
            payload["pairwise"].append(pair_payload)

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
