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

from trim.reasoning.rewrite import build_rewrite_candidates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge global/local reasoning evidence, filter both-wrong samples, and build rewrite candidates."
    )
    parser.add_argument("--global-dir", required=True, help="Directory containing global sample_*.json files")
    parser.add_argument("--local-dir", required=True, help="Directory containing local sample_*.json files")
    parser.add_argument(
        "--playbook-root",
        default="playbooks",
        help="Directory containing task playbooks named <task>.md",
    )
    parser.add_argument(
        "--allow-missing-playbook",
        action="store_true",
        help="Allow candidate generation to continue with an empty playbook field if <task>.md is missing.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/reasoning_rewrite_candidates",
        help="Output directory for filtered candidate JSON files and manifest",
    )
    parser.add_argument(
        "--sample-indices",
        nargs="*",
        type=int,
        default=None,
        help="Optional explicit sample indices to process",
    )
    parser.add_argument("--max-samples", type=int, default=None, help="Optional max number of shared samples")
    parser.add_argument(
        "--expected-neighbor-count",
        type=int,
        default=6,
        help="Expected number of per-neighbor local drafts to keep in each candidate",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = build_rewrite_candidates(
        global_dir=args.global_dir,
        local_dir=args.local_dir,
        output_dir=args.output_dir,
        playbook_root=args.playbook_root,
        allow_missing_playbook=args.allow_missing_playbook,
        sample_indices=args.sample_indices,
        max_samples=args.max_samples,
        expected_neighbor_count=args.expected_neighbor_count,
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
