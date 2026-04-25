#!/usr/bin/env python3
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import sys
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from scripts.run_local_neighbor_rewrite_examples import _run_one as run_one_local_neighbor_rewrite
from scripts.run_local_summary_rewrite_examples import (
    _load_neighbor_outputs,
    run_one_summary_rewrite,
)
from trim.reasoning.rewrite.candidates import build_rewrite_candidates
from trim.reasoning.rewrite.llm import build_llm_request_config
from trim.reasoning.rewrite.pipeline import model_slug
from trim.utils.io import ensure_directory, load_json, save_json
from trim.utils.paths import resolve_project_path, serialize_project_path

try:
    from tqdm.auto import tqdm
except Exception:  # pragma: no cover - tqdm is optional in some environments
    def tqdm(iterable=None, **kwargs):
        return iterable


DEFAULT_GLOBAL_ROOT = "outputs/reasoning_evidence/global/all_tasks_core_pka_no_fr_keep_nan"
DEFAULT_LOCAL_ROOT = "outputs/reasoning_evidence/local/all_tasks_core_pka_no_fr_counts"
DEFAULT_CANDIDATE_ROOT = "outputs/reasoning_rewrite_candidates/no_step"
DEFAULT_OUTPUT_ROOT = "outputs/reasoning_rewrite_outputs_neighbor_level_no_step"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Batch run the new local-only rewrite stack: six per-neighbor rewrites "
            "followed by one local-summary rewrite per sample."
        )
    )
    parser.add_argument("--provider", required=True, choices=["openrouter", "openai", "vllm"])
    parser.add_argument(
        "--output-provider",
        default=None,
        choices=["openrouter", "openai", "vllm"],
        help="Optional provider name to use only for output directory layout.",
    )
    parser.add_argument(
        "--output-model",
        default=None,
        help="Optional model name to use only for output directory layout.",
    )
    parser.add_argument("--model", required=True, help="Model name exposed by the selected provider")
    parser.add_argument(
        "--mode",
        default="all",
        choices=["all", "local_neighbor", "local_summary"],
        help="Run only per-neighbor rewrites, only summaries from existing neighbors, or both.",
    )
    parser.add_argument("--split", default="train")
    parser.add_argument("--task", action="append", dest="tasks", default=None)
    parser.add_argument("--global-root", default=DEFAULT_GLOBAL_ROOT)
    parser.add_argument("--local-root", default=DEFAULT_LOCAL_ROOT)
    parser.add_argument("--playbook-root", default="playbooks")
    parser.add_argument("--allow-missing-playbook", action="store_true")
    parser.add_argument("--candidate-root", default=DEFAULT_CANDIDATE_ROOT)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--template-root", default="prompt_templates/reasoning_sft")
    parser.add_argument(
        "--skip-candidate-build",
        action="store_true",
        help="Use existing sample_*.json files under candidate-root instead of rebuilding candidates.",
    )
    parser.add_argument("--sample-index", action="append", type=int, default=None)
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--expected-neighbor-count", type=int, default=6)
    parser.add_argument(
        "--teacher-filter",
        default="local_correct",
        choices=["any_correct", "local_correct", "global_correct", "none"],
        help=(
            "Correctness filter used when building candidates. The local-neighbor SFT path "
            "defaults to local_correct to avoid rewriting samples where the local teacher is wrong."
        ),
    )
    parser.add_argument("--max-concurrency", type=int, default=1)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--retry-delay-s", type=float, default=0.0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-output-tokens", type=int, default=3500)
    parser.add_argument("--timeout-s", type=int, default=300)
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--dotenv-path", default=".env")
    parser.add_argument("--overwrite", action="store_true", help="Re-run even if result JSON already exists")
    return parser.parse_args()


def _resolve_tasks(*, global_root: str | Path, split: str, requested_tasks: list[str] | None) -> list[str]:
    if requested_tasks:
        return list(dict.fromkeys(requested_tasks))
    root = resolve_project_path(global_root)
    return sorted(path.name for path in root.iterdir() if (path / split).is_dir())


def _candidate_dir(*, candidate_root: str | Path, split: str, task: str) -> Path:
    return resolve_project_path(candidate_root) / split / task


def _candidate_paths_from_dir(
    *,
    candidate_root: str | Path,
    split: str,
    task: str,
    sample_indices: list[int] | None,
    max_samples: int | None,
) -> list[Path]:
    root = _candidate_dir(candidate_root=candidate_root, split=split, task=task)
    if sample_indices is None:
        paths = sorted(root.glob("sample_*.json"))
    else:
        paths = [root / f"sample_{int(index):05d}.json" for index in sample_indices]
    if max_samples is not None:
        paths = paths[: int(max_samples)]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing candidate JSON files: {missing[:5]}")
    if not paths:
        raise FileNotFoundError(f"No candidate sample_*.json files found in {root}")
    return [path.resolve() for path in paths]


def _build_or_load_candidates(
    *,
    task: str,
    split: str,
    global_root: str | Path,
    local_root: str | Path,
    playbook_root: str | Path,
    allow_missing_playbook: bool,
    candidate_root: str | Path,
    sample_indices: list[int] | None,
    max_samples: int | None,
    expected_neighbor_count: int,
    teacher_filter: str,
    skip_candidate_build: bool,
) -> tuple[dict[str, Any] | None, list[Path]]:
    if skip_candidate_build:
        return None, _candidate_paths_from_dir(
            candidate_root=candidate_root,
            split=split,
            task=task,
            sample_indices=sample_indices,
            max_samples=max_samples,
        )

    manifest = build_rewrite_candidates(
        global_dir=resolve_project_path(global_root) / task / split,
        local_dir=resolve_project_path(local_root) / task / split,
        output_dir=resolve_project_path(candidate_root) / split / task,
        playbook_root=playbook_root,
        allow_missing_playbook=allow_missing_playbook,
        sample_indices=sample_indices,
        max_samples=max_samples,
        expected_neighbor_count=expected_neighbor_count,
        teacher_filter=teacher_filter,
    )
    sample_files = manifest.get("artifacts", {}).get("sample_files") or []
    candidate_paths = [resolve_project_path(path) for path in sample_files]
    return manifest, candidate_paths


def _local_neighbor_result_path(
    *,
    output_root: str | Path,
    provider: str,
    model: str,
    split: str,
    task: str,
    sample_index: int,
    neighbor_index: int,
) -> Path:
    return (
        resolve_project_path(output_root)
        / provider
        / model_slug(model)
        / "local_neighbor"
        / split
        / task
        / f"sample_{int(sample_index):05d}"
        / f"neighbor_{int(neighbor_index):02d}"
        / "result.json"
    )


def _local_summary_result_path(
    *,
    output_root: str | Path,
    provider: str,
    model: str,
    split: str,
    task: str,
    sample_index: int,
) -> Path:
    return (
        resolve_project_path(output_root)
        / provider
        / model_slug(model)
        / "local_summary"
        / split
        / task
        / f"sample_{int(sample_index):05d}"
        / "result.json"
    )


def _manifest_dir(*, output_root: str | Path, provider: str, model: str, split: str, task: str) -> Path:
    return ensure_directory(
        resolve_project_path(output_root)
        / provider
        / model_slug(model)
        / "local_neighbor_summary"
        / split
        / task
    )


def _run_candidate(
    *,
    candidate_path: Path,
    mode: str,
    llm_config,
    output_root: str | Path,
    template_root: str | Path,
    max_retries: int,
    retry_delay_s: float,
    overwrite: bool,
    output_provider: str | None = None,
    output_model: str | None = None,
) -> dict[str, Any]:
    candidate_payload = load_json(candidate_path)
    task = str(candidate_payload["task"])
    split = str(candidate_payload["split"])
    sample_index = int(candidate_payload["sample_index"])

    rows: list[dict[str, Any]] = []
    neighbor_outputs: dict[int, dict[str, Any]] = {}

    if mode in {"all", "local_neighbor"}:
        for neighbor_index in range(1, 7):
            output_payload = run_one_local_neighbor_rewrite(
                candidate_payload=candidate_payload,
                candidate_json_path=candidate_path,
                neighbor_index=neighbor_index,
                llm_config=llm_config,
                output_root=output_root,
                template_root=template_root,
                overwrite=overwrite,
                max_retries=max_retries,
                retry_delay_s=retry_delay_s,
                output_provider=output_provider,
                output_model=output_model,
            )
            neighbor_outputs[neighbor_index] = output_payload
            rows.append(
                {
                    "task": task,
                    "split": split,
                    "sample_index": sample_index,
                    "mode": "local_neighbor",
                    "neighbor_index": neighbor_index,
                    "status": "succeeded",
                    "output_path": serialize_project_path(
                        _local_neighbor_result_path(
                            output_root=output_root,
                            provider=str(output_provider or llm_config.provider),
                            model=str(output_model or llm_config.model),
                            split=split,
                            task=task,
                            sample_index=sample_index,
                            neighbor_index=neighbor_index,
                        )
                    ),
                }
            )

    if mode in {"all", "local_summary"}:
        if not neighbor_outputs:
            neighbor_outputs = _load_neighbor_outputs(
                root=output_root,
                provider=str(output_provider or llm_config.provider),
                model=str(output_model or llm_config.model),
                split=split,
                task=task,
                sample_index=sample_index,
            )
        run_one_summary_rewrite(
            candidate_payload=candidate_payload,
            candidate_json_path=candidate_path,
            neighbor_outputs=neighbor_outputs,
            llm_config=llm_config,
            output_root=output_root,
            neighbor_output_root=output_root,
            template_root=template_root,
            overwrite=overwrite,
            max_retries=max_retries,
            retry_delay_s=retry_delay_s,
            output_provider=output_provider,
            output_model=output_model,
        )
        rows.append(
            {
                "task": task,
                "split": split,
                "sample_index": sample_index,
                "mode": "local_summary",
                "status": "succeeded",
                "output_path": serialize_project_path(
                    _local_summary_result_path(
                        output_root=output_root,
                        provider=str(output_provider or llm_config.provider),
                        model=str(output_model or llm_config.model),
                        split=split,
                        task=task,
                        sample_index=sample_index,
                    )
                ),
            }
        )

    return {
        "status": "succeeded",
        "task": task,
        "split": split,
        "sample_index": sample_index,
        "candidate_path": serialize_project_path(candidate_path),
        "rows": rows,
    }


def run_task_batch(
    *,
    task: str,
    split: str,
    mode: str,
    llm_config,
    global_root: str | Path,
    local_root: str | Path,
    playbook_root: str | Path,
    allow_missing_playbook: bool,
    candidate_root: str | Path,
    output_root: str | Path,
    template_root: str | Path,
    sample_indices: list[int] | None,
    max_samples: int | None,
    expected_neighbor_count: int,
    teacher_filter: str,
    skip_candidate_build: bool,
    max_concurrency: int,
    max_retries: int,
    retry_delay_s: float,
    overwrite: bool,
    output_provider: str | None = None,
    output_model: str | None = None,
) -> dict[str, Any]:
    candidate_manifest, candidate_paths = _build_or_load_candidates(
        task=task,
        split=split,
        global_root=global_root,
        local_root=local_root,
        playbook_root=playbook_root,
        allow_missing_playbook=allow_missing_playbook,
        candidate_root=candidate_root,
        sample_indices=sample_indices,
        max_samples=max_samples,
        expected_neighbor_count=expected_neighbor_count,
        teacher_filter=teacher_filter,
        skip_candidate_build=skip_candidate_build,
    )

    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    resolved_max_concurrency = max(1, int(max_concurrency))

    def _process(path: Path) -> dict[str, Any]:
        try:
            return _run_candidate(
                candidate_path=path,
                mode=mode,
                llm_config=llm_config,
                output_root=output_root,
                template_root=template_root,
                max_retries=max_retries,
                retry_delay_s=retry_delay_s,
                overwrite=overwrite,
                output_provider=output_provider,
                output_model=output_model,
            )
        except Exception as exc:
            sample_index = int(path.stem.split("_")[-1])
            return {
                "status": "failed",
                "task": task,
                "split": split,
                "sample_index": sample_index,
                "candidate_path": serialize_project_path(path),
                "error": f"{type(exc).__name__}: {exc}",
                "rows": [],
            }

    progress_desc = f"{task} ({mode})"
    if resolved_max_concurrency == 1 or len(candidate_paths) <= 1:
        iterator = (_process(path) for path in candidate_paths)
        for result in tqdm(iterator, total=len(candidate_paths), desc=progress_desc):
            rows.extend(result.get("rows", []))
            if result.get("status") != "succeeded":
                failures.append({key: value for key, value in result.items() if key != "rows"})
    else:
        with ThreadPoolExecutor(max_workers=resolved_max_concurrency) as executor:
            future_to_path = {executor.submit(_process, path): path for path in candidate_paths}
            for future in tqdm(as_completed(future_to_path), total=len(future_to_path), desc=progress_desc):
                result = future.result()
                rows.extend(result.get("rows", []))
                if result.get("status") != "succeeded":
                    failures.append({key: value for key, value in result.items() if key != "rows"})

    mode_order = {"local_neighbor": 0, "local_summary": 1}
    rows.sort(
        key=lambda row: (
            int(row["sample_index"]),
            mode_order[str(row["mode"])],
            int(row.get("neighbor_index", 0)),
        )
    )
    failures.sort(key=lambda row: int(row["sample_index"]))

    summary = {
        "schema_version": "trim_local_neighbor_summary_rewrite_batch_v1",
        "provider": llm_config.provider,
        "output_provider": str(output_provider or llm_config.provider),
        "output_model": str(output_model or llm_config.model),
        "model": llm_config.model,
        "task": task,
        "split": split,
        "mode": mode,
        "candidate_manifest": candidate_manifest,
        "candidate_root": serialize_project_path(resolve_project_path(candidate_root)),
        "output_root": serialize_project_path(resolve_project_path(output_root)),
        "teacher_filter": str(teacher_filter),
        "num_candidates": int(len(candidate_paths)),
        "max_concurrency": int(resolved_max_concurrency),
        "max_retries": int(max_retries),
        "retry_delay_s": float(retry_delay_s),
        "num_succeeded": int(len(candidate_paths) - len(failures)),
        "num_failed": int(len(failures)),
        "failures": failures,
        "rows": rows,
    }
    save_json(
        _manifest_dir(
            output_root=output_root,
            provider=str(output_provider or llm_config.provider),
            model=str(output_model or llm_config.model),
            split=split,
            task=task,
        )
        / "manifest.json",
        summary,
    )
    return summary


def main() -> int:
    args = parse_args()
    llm_config = build_llm_request_config(
        provider=args.provider,
        model=args.model,
        api_base=args.api_base,
        api_key=args.api_key,
        temperature=args.temperature,
        max_tokens=args.max_output_tokens,
        timeout_s=args.timeout_s,
        dotenv_path=args.dotenv_path,
    )
    tasks = _resolve_tasks(global_root=args.global_root, split=args.split, requested_tasks=args.tasks)

    summaries = []
    for task in tasks:
        summary = run_task_batch(
            task=task,
            split=args.split,
            mode=args.mode,
            llm_config=llm_config,
            global_root=args.global_root,
            local_root=args.local_root,
            playbook_root=args.playbook_root,
            allow_missing_playbook=args.allow_missing_playbook,
            candidate_root=args.candidate_root,
            output_root=args.output_root,
            template_root=args.template_root,
            sample_indices=args.sample_index,
            max_samples=args.max_samples,
            expected_neighbor_count=args.expected_neighbor_count,
            teacher_filter=args.teacher_filter,
            skip_candidate_build=args.skip_candidate_build,
            max_concurrency=args.max_concurrency,
            max_retries=args.max_retries,
            retry_delay_s=args.retry_delay_s,
            overwrite=args.overwrite,
            output_provider=args.output_provider,
            output_model=args.output_model,
        )
        summaries.append(summary)

    run_summary = {
        "schema_version": "trim_local_neighbor_summary_rewrite_run_v1",
        "provider": llm_config.provider,
        "output_provider": str(args.output_provider or llm_config.provider),
        "output_model": str(args.output_model or llm_config.model),
        "model": llm_config.model,
        "mode": args.mode,
        "split": args.split,
        "tasks": tasks,
        "max_concurrency": int(args.max_concurrency),
        "max_retries": int(args.max_retries),
        "retry_delay_s": float(args.retry_delay_s),
        "candidate_root": serialize_project_path(resolve_project_path(args.candidate_root)),
        "output_root": serialize_project_path(resolve_project_path(args.output_root)),
        "teacher_filter": str(args.teacher_filter),
        "summaries": summaries,
    }
    save_json(
        resolve_project_path(args.output_root)
        / str(args.output_provider or llm_config.provider)
        / model_slug(str(args.output_model or llm_config.model))
        / "local_neighbor_summary"
        / args.split
        / "last_run_summary.json",
        run_summary,
    )
    print(json.dumps(run_summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
