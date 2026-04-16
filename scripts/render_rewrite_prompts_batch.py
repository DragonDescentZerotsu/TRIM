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

from trim.reasoning.rewrite.pipeline import (
    DEFAULT_CANDIDATE_ROOT,
    DEFAULT_FILTERED_ROOT,
    DEFAULT_REWRITE_OUTPUT_ROOT,
    build_candidates_from_filtered_records,
    extract_reasoning_text_for_mode,
    model_slug,
    resolve_task_list,
)
from trim.reasoning.rewrite.rendering import render_rewrite_prompt
from trim.utils.io import load_json, save_json
from trim.utils.paths import resolve_project_path


DEFAULT_GLOBAL_ROOT = "outputs/reasoning_evidence/global/all_tasks_core_pka_no_fr_keep_nan"
DEFAULT_LOCAL_ROOT = "outputs/reasoning_evidence/local/all_tasks_core_pka_no_fr_counts"
DEFAULT_PROMPT_OUTPUT_ROOT = "outputs/rewrite_prompts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch render filled rewrite prompts from both-wrong-filtered samples."
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["global", "local", "hybrid", "all"],
        help="'all' renders every mode that has enough inputs available.",
    )
    parser.add_argument("--split", default="train")
    parser.add_argument("--task", action="append", dest="tasks", default=None)
    parser.add_argument("--filtered-root", default=str(DEFAULT_FILTERED_ROOT))
    parser.add_argument("--global-root", default=DEFAULT_GLOBAL_ROOT)
    parser.add_argument("--local-root", default=DEFAULT_LOCAL_ROOT)
    parser.add_argument("--playbook-root", default="playbooks")
    parser.add_argument("--candidate-root", default=str(DEFAULT_CANDIDATE_ROOT))
    parser.add_argument("--output-root", default=DEFAULT_PROMPT_OUTPUT_ROOT)
    parser.add_argument("--template-root", default="prompt_templates/reasoning_sft")
    parser.add_argument("--provider", default=None, help="Required for hybrid when loading prior rewrites")
    parser.add_argument("--model", default=None, help="Required for hybrid when loading prior rewrites")
    parser.add_argument("--rewrite-output-root", default=str(DEFAULT_REWRITE_OUTPUT_ROOT))
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def _rewrite_json_path(
    *,
    rewrite_output_root: str | Path,
    provider: str,
    model: str,
    mode: str,
    split: str,
    task: str,
    sample_index: int,
) -> Path:
    return (
        resolve_project_path(rewrite_output_root)
        / provider
        / model_slug(model)
        / mode
        / split
        / task
        / f"sample_{int(sample_index):05d}"
        / "result.json"
    )


def _load_reasoning_text_from_saved_output(
    *,
    rewrite_output_root: str | Path,
    provider: str,
    model: str,
    mode: str,
    split: str,
    task: str,
    sample_index: int,
) -> str:
    payload = load_json(
        _rewrite_json_path(
            rewrite_output_root=rewrite_output_root,
            provider=provider,
            model=model,
            mode=mode,
            split=split,
            task=task,
            sample_index=sample_index,
        )
    )
    return extract_reasoning_text_for_mode(payload=payload, mode=mode)


def _prompt_output_path(
    *,
    output_root: str | Path,
    mode: str,
    split: str,
    task: str,
    sample_index: int,
) -> Path:
    return (
        resolve_project_path(output_root)
        / mode
        / split
        / task
        / f"sample_{int(sample_index):05d}.md"
    )


def main() -> int:
    args = parse_args()
    tasks = resolve_task_list(
        filtered_root=args.filtered_root,
        split=args.split,
        requested_tasks=args.tasks,
    )
    requested_modes = ["global", "local", "hybrid"] if args.mode == "all" else [args.mode]

    if "hybrid" in requested_modes:
        if not args.provider or not args.model:
            raise ValueError("--provider and --model are required when rendering hybrid prompts")

    rows: list[dict[str, object]] = []
    skipped_rows: list[dict[str, object]] = []

    for task in tasks:
        candidate_manifest = build_candidates_from_filtered_records(
            task=task,
            split=args.split,
            filtered_root=args.filtered_root,
            global_root=args.global_root,
            local_root=args.local_root,
            playbook_root=args.playbook_root,
            candidate_root=args.candidate_root,
            max_samples=args.max_samples,
        )
        candidate_dir = Path(candidate_manifest["artifacts"]["output_dir"])
        for candidate_path in sorted(candidate_dir.glob("sample_*.json")):
            candidate_payload = load_json(candidate_path)
            sample_index = int(candidate_payload["sample_index"])

            for mode in requested_modes:
                output_path = _prompt_output_path(
                    output_root=args.output_root,
                    mode=mode,
                    split=args.split,
                    task=task,
                    sample_index=sample_index,
                )
                if output_path.exists() and not args.overwrite:
                    rows.append(
                        {
                            "task": task,
                            "split": args.split,
                            "sample_index": sample_index,
                            "mode": mode,
                            "output_path": str(output_path.resolve()),
                            "status": "existing",
                        }
                    )
                    continue

                kwargs: dict[str, str] = {}
                try:
                    if mode == "hybrid":
                        kwargs["global_reasoning"] = _load_reasoning_text_from_saved_output(
                            rewrite_output_root=args.rewrite_output_root,
                            provider=args.provider,
                            model=args.model,
                            mode="global",
                            split=args.split,
                            task=task,
                            sample_index=sample_index,
                        )
                        kwargs["local_reasoning"] = _load_reasoning_text_from_saved_output(
                            rewrite_output_root=args.rewrite_output_root,
                            provider=args.provider,
                            model=args.model,
                            mode="local",
                            split=args.split,
                            task=task,
                            sample_index=sample_index,
                        )
                    prompt_text = render_rewrite_prompt(
                        candidate_payload=candidate_payload,
                        mode=mode,
                        template_root=args.template_root,
                        **kwargs,
                    )
                except FileNotFoundError as exc:
                    skipped_rows.append(
                        {
                            "task": task,
                            "split": args.split,
                            "sample_index": sample_index,
                            "mode": mode,
                            "reason": str(exc),
                        }
                    )
                    continue

                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(prompt_text, encoding="utf-8")
                rows.append(
                    {
                        "task": task,
                        "split": args.split,
                        "sample_index": sample_index,
                        "mode": mode,
                        "output_path": str(output_path.resolve()),
                        "status": "rendered",
                    }
                )

    summary = {
        "schema_version": "trim_rewrite_prompt_batch_summary_v1",
        "mode": args.mode,
        "split": args.split,
        "tasks": tasks,
        "filtered_root": str(resolve_project_path(args.filtered_root)),
        "candidate_root": str(resolve_project_path(args.candidate_root)),
        "output_root": str(resolve_project_path(args.output_root)),
        "rows": rows,
        "skipped_rows": skipped_rows,
    }
    save_json(resolve_project_path(args.output_root) / "batch_summary.json", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
