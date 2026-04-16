#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from trim.reasoning.agent_sft import (
    DEFAULT_AGENT_REASONING_SFT_OUTPUT_ROOT,
    DEFAULT_REWRITE_MODEL,
    DEFAULT_REWRITE_PROVIDER,
)
from trim.reasoning.rewrite.pipeline import model_slug
from trim.utils.io import ensure_directory, load_json, save_json
from trim.utils.paths import resolve_project_path


HF_PUBLIC_RECORD_SCHEMA_VERSION = "trim_agent_reasoning_sft_messages_hf_public_v1"
HF_PUBLIC_MANIFEST_SCHEMA_VERSION = "trim_agent_reasoning_sft_hf_public_manifest_v1"
DEFAULT_HF_PUBLIC_OUTPUT_ROOT = "data/sft/agent_reasoning_messages/hf_public"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export agent reasoning SFT JSONL files into a Hugging Face-friendly public dataset layout."
        )
    )
    parser.add_argument(
        "--source-root",
        default=str(DEFAULT_AGENT_REASONING_SFT_OUTPUT_ROOT),
        help="Base root containing provider/model/split agent reasoning SFT JSONL outputs.",
    )
    parser.add_argument("--provider", default=DEFAULT_REWRITE_PROVIDER)
    parser.add_argument("--model", default=DEFAULT_REWRITE_MODEL)
    parser.add_argument("--split", default="train")
    parser.add_argument(
        "--output-root",
        default=DEFAULT_HF_PUBLIC_OUTPUT_ROOT,
        help="Base output root for sanitized HF-public exports.",
    )
    parser.add_argument(
        "--drop-source-paths",
        action="store_true",
        default=True,
        help="Drop local absolute source_paths from exported records.",
    )
    parser.add_argument(
        "--keep-source-paths",
        dest="drop_source_paths",
        action="store_false",
        help="Keep source_paths in the exported records.",
    )
    return parser.parse_args()


def _source_split_dir(*, source_root: str | Path, provider: str, model: str, split: str) -> Path:
    return resolve_project_path(source_root) / provider / model_slug(model) / split


def _dataset_root(*, output_root: str | Path, provider: str, model: str) -> Path:
    return ensure_directory(resolve_project_path(output_root) / provider / model_slug(model))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if not isinstance(payload, dict):
                raise ValueError(f"Expected JSON object in {path}:{line_number}")
            records.append(payload)
    return records


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _sanitize_record(record: dict[str, Any], *, drop_source_paths: bool) -> dict[str, Any]:
    cleaned = dict(record)
    cleaned["schema_version"] = HF_PUBLIC_RECORD_SCHEMA_VERSION
    if drop_source_paths:
        cleaned.pop("source_paths", None)
    return cleaned


def _relative_posix(path: Path, *, start: Path) -> str:
    return path.relative_to(start).as_posix()


def _build_public_manifest(
    *,
    source_manifest: dict[str, Any] | None,
    split: str,
    exported_files: list[tuple[str, int, Path]],
    dataset_root: Path,
    provider: str,
    model: str,
    drop_source_paths: bool,
) -> dict[str, Any]:
    tasks = [
        {
            "task": task,
            "split": split,
            "num_records": num_records,
            "path": _relative_posix(path, start=dataset_root),
        }
        for task, num_records, path in exported_files
    ]
    payload: dict[str, Any] = {
        "schema_version": HF_PUBLIC_MANIFEST_SCHEMA_VERSION,
        "provider": provider,
        "model": model,
        "split": split,
        "num_tasks": len(tasks),
        "num_records": sum(num_records for _, num_records, _ in exported_files),
        "tasks": tasks,
        "export_options": {
            "drop_source_paths": drop_source_paths,
        },
        "source": {
            "layout": f"{provider}/{model_slug(model)}/{split}",
        },
    }
    if source_manifest is not None:
        payload["source_manifest"] = {
            "schema_version": source_manifest.get("schema_version"),
            "num_tasks": source_manifest.get("num_tasks"),
            "num_records": source_manifest.get("num_records"),
        }
    return payload


def _discover_exported_splits(dataset_root: Path) -> list[str]:
    split_names: list[str] = []
    for split_dir in sorted(path for path in dataset_root.iterdir() if path.is_dir()):
        if split_dir.name == "metadata":
            continue
        if any(split_dir.glob("*.jsonl")):
            split_names.append(split_dir.name)
    return split_names


def _yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _build_readme(*, dataset_root: Path, exported_splits: list[str], manifest_payload: dict[str, Any]) -> str:
    config_lines = ["---", "configs:"]
    for split in exported_splits:
        config_lines.extend(
            [
                "- config_name: default",
                "  data_files:",
                f"  - split: {split}",
                f"    path: {_yaml_quote(f'{split}/*.jsonl')}",
            ]
        )
        break
    for split in exported_splits[1:]:
        config_lines.extend(
            [
                f"  - split: {split}",
                f"    path: {_yaml_quote(f'{split}/*.jsonl')}",
            ]
        )
    config_lines.append("---")

    task_names = ", ".join(task["task"] for task in manifest_payload.get("tasks", []))
    lines = list(config_lines)
    lines.extend(
        [
            "",
            "# TRIM Agent Reasoning Messages (HF Public Export)",
            "",
            "This directory is a Hugging Face-friendly public export of the TRIM agent reasoning SFT data.",
            "",
            "## What Is Included",
            "",
            f"- Provider: `{manifest_payload.get('provider', '')}`",
            f"- Model: `{manifest_payload.get('model', '')}`",
            f"- Splits present: `{', '.join(exported_splits)}`",
            f"- Records in this export manifest: `{manifest_payload.get('num_records', 0)}`",
            f"- Tasks in this split: `{task_names}`",
            "",
            "## Record Schema",
            "",
            "Each JSONL line is one training example with these top-level fields:",
            "",
            "- `schema_version`",
            "- `task`",
            "- `split`",
            "- `sample_index`",
            "- `sample_id`",
            "- `smiles`",
            "- `gt_label`",
            "- `final_answer_option`",
            "- `messages`",
            "",
            "The `messages` field stores a tool-augmented chat transcript, including nested `tool_calls` and the assistant `thinking` text used in the original SFT export.",
            "",
            "## Public Sanitization",
            "",
            "- Local absolute `source_paths` have been removed from the sample records by default.",
            "- Task-level export metadata is stored under `metadata/manifest.json`.",
            "",
            "## Loading Example",
            "",
            "```python",
            "from datasets import load_dataset",
            "",
            "ds = load_dataset(",
            "    \"json\",",
            "    data_files={\"train\": \"train/*.jsonl\"},",
            ")",
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def export_hf_public_dataset(
    *,
    source_root: str | Path,
    provider: str,
    model: str,
    split: str,
    output_root: str | Path,
    drop_source_paths: bool,
) -> dict[str, Any]:
    source_split_dir = _source_split_dir(
        source_root=source_root,
        provider=provider,
        model=model,
        split=split,
    )
    if not source_split_dir.exists():
        raise FileNotFoundError(f"Source split directory does not exist: {source_split_dir}")

    dataset_root = _dataset_root(output_root=output_root, provider=provider, model=model)
    split_output_dir = ensure_directory(dataset_root / split)
    metadata_dir = ensure_directory(dataset_root / "metadata")

    source_manifest_path = source_split_dir / "manifest.json"
    source_manifest = load_json(source_manifest_path) if source_manifest_path.exists() else None

    exported_files: list[tuple[str, int, Path]] = []
    for source_jsonl in sorted(source_split_dir.glob("*.jsonl")):
        task = source_jsonl.stem
        records = _read_jsonl(source_jsonl)
        cleaned_records = [
            _sanitize_record(record, drop_source_paths=drop_source_paths) for record in records
        ]
        output_jsonl = split_output_dir / source_jsonl.name
        _write_jsonl(output_jsonl, cleaned_records)
        exported_files.append((task, len(cleaned_records), output_jsonl))

    public_manifest = _build_public_manifest(
        source_manifest=source_manifest,
        split=split,
        exported_files=exported_files,
        dataset_root=dataset_root,
        provider=provider,
        model=model,
        drop_source_paths=drop_source_paths,
    )
    manifest_path = save_json(metadata_dir / "manifest.json", public_manifest)

    exported_splits = _discover_exported_splits(dataset_root)
    readme_text = _build_readme(
        dataset_root=dataset_root,
        exported_splits=exported_splits,
        manifest_payload=public_manifest,
    )
    readme_path = dataset_root / "README.md"
    readme_path.write_text(readme_text, encoding="utf-8")

    return {
        "dataset_root": str(dataset_root.resolve()),
        "split_output_dir": str(split_output_dir.resolve()),
        "manifest_path": str(manifest_path.resolve()),
        "readme_path": str(readme_path.resolve()),
        "split": split,
        "provider": provider,
        "model": model,
        "num_tasks": public_manifest["num_tasks"],
        "num_records": public_manifest["num_records"],
        "exported_files": [
            {
                "task": task,
                "num_records": num_records,
                "path": str(path.resolve()),
            }
            for task, num_records, path in exported_files
        ],
        "drop_source_paths": drop_source_paths,
    }


def main() -> int:
    args = parse_args()
    summary = export_hf_public_dataset(
        source_root=args.source_root,
        provider=args.provider,
        model=args.model,
        split=args.split,
        output_root=args.output_root,
        drop_source_paths=args.drop_source_paths,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
