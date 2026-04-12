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

from trim.evaluation.global_eval import evaluate_global_bundle
from trim.utils.paths import DEFAULT_PROCESSED_DATA_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a saved global EBM bundle on a target split.")
    parser.add_argument("--bundle-path", required=True)
    parser.add_argument("--split", default="test")
    parser.add_argument("--data-root", default=str(DEFAULT_PROCESSED_DATA_ROOT))
    parser.add_argument("--output-dir", default="outputs/metrics/global_eval")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = evaluate_global_bundle(
        bundle_path=args.bundle_path,
        split=args.split,
        dataset_root=args.data_root,
        output_dir=args.output_dir,
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

