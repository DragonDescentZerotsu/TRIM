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

from trim.utils.paths import serialize_project_path


DEFAULT_ROOTS = [
    "prompt_templates/reasoning_sft",
    "outputs/reasoning_rewrite_examples",
    "outputs/reasoning_rewrite_outputs",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replace the typo 'Nrighbor' with 'Neighbor' in local prompt/template artifacts."
    )
    parser.add_argument(
        "--root",
        action="append",
        dest="roots",
        default=None,
        help="Root directory to scan recursively. Repeat for multiple roots.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only report matching files without editing them.",
    )
    return parser.parse_args()


def _candidate_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return [path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in {".md", ".txt", ".json"}]


def main() -> int:
    args = parse_args()
    roots = [Path(root) for root in (args.roots or DEFAULT_ROOTS)]

    changed_files: list[str] = []
    total_replacements = 0

    for root in roots:
        for path in _candidate_files(root):
            text = path.read_text(encoding="utf-8")
            count = text.count("Nrighbor")
            if count == 0:
                continue
            total_replacements += count
            changed_files.append(serialize_project_path(path))
            if args.dry_run:
                continue
            path.write_text(text.replace("Nrighbor", "Neighbor"), encoding="utf-8")

    print(
        json.dumps(
            {
                "roots": [serialize_project_path(root) for root in roots],
                "dry_run": bool(args.dry_run),
                "num_changed_files": len(changed_files),
                "total_replacements": total_replacements,
                "changed_files": changed_files,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
