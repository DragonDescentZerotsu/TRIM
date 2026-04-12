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

from trim.data.legacy_assets import prepare_legacy_assets


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create TRIM-local symlinks to legacy cached assets.")
    parser.add_argument("--force", action="store_true", help="Replace existing symlinks if they point elsewhere.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = prepare_legacy_assets(force=args.force)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

