#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from trim.reasoning.rewrite.llm import (
    build_llm_request_config,
    extract_json_from_response_text,
    run_chat_completion,
)
from trim.reasoning.rewrite.pipeline import (
    collect_reasoning_post_checks,
    model_slug,
    validate_saved_rewrite_output,
)
from trim.reasoning.rewrite.rendering import render_rewrite_prompt
from trim.utils.io import load_json, save_json
from trim.utils.paths import resolve_project_path, serialize_project_path


DEFAULT_CANDIDATE_ROOT = "outputs/reasoning_rewrite_candidates/from_filters"
DEFAULT_OUTPUT_ROOT = "outputs/reasoning_rewrite_outputs_neighbor_level"
_BANNED_REASONING_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (name, re.compile(pattern, re.IGNORECASE))
    for name, pattern in (
        # Keep this script-level validator narrow. Broader meta-language and
        # EBM-score leakage checks are handled by collect_reasoning_post_checks.
        ("mechanical_step", r"\bStep [0-9]+"),
    )
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a few single-neighbor local rewrite examples using existing rewrite utilities."
    )
    parser.add_argument("--provider", default="openrouter", choices=["openrouter", "openai", "vllm"])
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
    parser.add_argument("--model", default="openai/gpt-5.4-mini")
    parser.add_argument("--split", default="train")
    parser.add_argument("--task", default="BBB_Martins")
    parser.add_argument(
        "--sample-index",
        action="append",
        type=int,
        default=None,
        help="Sample index to run. Can be repeated. Defaults to 0.",
    )
    parser.add_argument(
        "--neighbor-index",
        action="append",
        type=int,
        default=None,
        help="1-based neighbor index to run. Can be repeated. Defaults to 1, 4, and 6.",
    )
    parser.add_argument("--candidate-root", default=DEFAULT_CANDIDATE_ROOT)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--template-root", default="prompt_templates/reasoning_sft")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-output-tokens", type=int, default=None)
    parser.add_argument("--timeout-s", type=int, default=300)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--retry-delay-s", type=float, default=0.0)
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--dotenv-path", default=".env")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def _candidate_path(*, candidate_root: str | Path, split: str, task: str, sample_index: int) -> Path:
    return (
        resolve_project_path(candidate_root)
        / split
        / task
        / f"sample_{int(sample_index):05d}.json"
    )


def _output_dir(
    *,
    output_root: str | Path,
    provider: str,
    model: str,
    split: str,
    task: str,
    sample_index: int,
    neighbor_index: int,
) -> Path:
    path = (
        resolve_project_path(output_root)
        / provider
        / model_slug(model)
        / "local_neighbor"
        / split
        / task
        / f"sample_{int(sample_index):05d}"
        / f"neighbor_{int(neighbor_index):02d}"
    )
    path.mkdir(parents=True, exist_ok=True)
    return path


def _neighbor_payload(candidate_payload: dict[str, Any], *, neighbor_index: int) -> dict[str, Any]:
    neighbors = list(candidate_payload["local_per_neighbor_rewrite_input"]["neighbors"])
    for neighbor in neighbors:
        if int(neighbor["neighbor_index"]) == int(neighbor_index):
            return dict(neighbor)
    raise IndexError(f"Neighbor {neighbor_index} not found for sample {candidate_payload.get('sample_index')}")


def _validate_local_neighbor_output(
    *,
    parsed_output: dict[str, Any],
    source_neighbor: dict[str, Any],
) -> None:
    expected_neighbor_index = int(source_neighbor["neighbor_index"])
    observed_neighbor_index = int(parsed_output.get("neighbor_index", -1))
    if observed_neighbor_index != expected_neighbor_index:
        raise ValueError(
            f"neighbor_index mismatch: expected {expected_neighbor_index}, got {observed_neighbor_index}"
        )

    prediction = parsed_output.get("neighbor_prediction")
    if not isinstance(prediction, dict):
        raise ValueError("parsed_output.neighbor_prediction must be an object")
    expected_label = int(source_neighbor["pair_teacher"]["pair_prediction"])
    observed_label = int(prediction.get("label", -1))
    if observed_label != expected_label:
        raise ValueError(f"neighbor_prediction.label mismatch: expected {expected_label}, got {observed_label}")

    expected_strength = str(source_neighbor["evidence_strength"]["teacher_aligned_evidence_strength"])
    observed_strength = str(parsed_output.get("evidence_strength", ""))
    if observed_strength != expected_strength:
        raise ValueError(
            f"evidence_strength mismatch: expected {expected_strength!r}, got {observed_strength!r}"
        )

    reasoning = str(parsed_output.get("reasoning", "") or "")
    found_patterns = [
        name for name, pattern in _BANNED_REASONING_PATTERNS if pattern.search(reasoning)
    ]
    if found_patterns:
        raise ValueError(f"reasoning contains banned source/meta phrasing: {found_patterns!r}")


def _run_one(
    *,
    candidate_payload: dict[str, Any],
    candidate_json_path: Path,
    neighbor_index: int,
    llm_config,
    output_root: str | Path,
    template_root: str | Path,
    overwrite: bool,
    max_retries: int,
    retry_delay_s: float = 0.0,
    output_provider: str | None = None,
    output_model: str | None = None,
) -> dict[str, Any]:
    split = str(candidate_payload["split"])
    task = str(candidate_payload["task"])
    sample_index = int(candidate_payload["sample_index"])
    storage_provider = str(output_provider or llm_config.provider)
    storage_model = str(output_model or llm_config.model)
    sample_output_dir = _output_dir(
        output_root=output_root,
        provider=storage_provider,
        model=storage_model,
        split=split,
        task=task,
        sample_index=sample_index,
        neighbor_index=neighbor_index,
    )
    result_path = sample_output_dir / "result.json"
    prompt_path = sample_output_dir / "prompt.md"
    response_path = sample_output_dir / "response.txt"

    if result_path.exists() and not overwrite:
        payload = load_json(result_path)
        validate_saved_rewrite_output(mode="local_neighbor", payload=payload)
        _validate_local_neighbor_output(
            parsed_output=dict(payload["parsed_output"]),
            source_neighbor=_neighbor_payload(candidate_payload, neighbor_index=neighbor_index),
        )
        return payload

    prompt_text = render_rewrite_prompt(
        candidate_payload=candidate_payload,
        mode="local_neighbor",
        template_root=template_root,
        neighbor_index=neighbor_index,
    )
    prompt_path.write_text(prompt_text, encoding="utf-8")

    source_neighbor = _neighbor_payload(candidate_payload, neighbor_index=neighbor_index)
    total_attempts = max(1, int(max_retries) + 1)
    last_error: Exception | None = None
    for attempt_index in range(1, total_attempts + 1):
        try:
            completion = run_chat_completion(prompt=prompt_text, config=llm_config)
            response_content = str(completion["content"])
            response_path.write_text(response_content, encoding="utf-8")

            parsed_output = extract_json_from_response_text(response_content)
            _validate_local_neighbor_output(parsed_output=parsed_output, source_neighbor=source_neighbor)
            post_checks = collect_reasoning_post_checks(mode="local_neighbor", parsed_output=parsed_output)
            result_payload = {
                "schema_version": "trim_reasoning_rewrite_output_v1",
                "mode": "local_neighbor",
                "provider": llm_config.provider,
                "output_provider": storage_provider,
                "output_model": storage_model,
                "model": llm_config.model,
                "api_base": llm_config.api_base,
                "task": task,
                "split": split,
                "sample_id": str(candidate_payload["sample_id"]),
                "sample_index": sample_index,
                "neighbor_index": int(neighbor_index),
                "prompt_path": serialize_project_path(prompt_path),
                "response_text_path": serialize_project_path(response_path),
                "candidate_json_path": serialize_project_path(candidate_json_path),
                "source_neighbor": {
                    "neighbor_index": int(source_neighbor["neighbor_index"]),
                    "neighbor_role": str(source_neighbor["neighbor_role"]),
                    "neighbor_label_semantics": str(source_neighbor["neighbor_label_semantics"]),
                    "neighbor_similarity": float(source_neighbor["neighbor_similarity"]),
                    "pair_prediction_semantics": str(source_neighbor["pair_teacher"]["pair_prediction_semantics"]),
                    "teacher_aligned_evidence_strength": str(
                        source_neighbor["evidence_strength"]["teacher_aligned_evidence_strength"]
                    ),
                },
                "parsed_output": parsed_output,
                "post_checks": post_checks,
                "response_content": response_content,
                "raw_response": completion["raw_response"],
                "attempt_count": attempt_index,
            }
            validate_saved_rewrite_output(mode="local_neighbor", payload=result_payload)
            save_json(result_path, result_payload)
            return result_payload
        except Exception as exc:
            last_error = exc
            if attempt_index < total_attempts and retry_delay_s > 0:
                time.sleep(float(retry_delay_s))

    assert last_error is not None
    raise RuntimeError(
        f"Local-neighbor rewrite failed after {total_attempts} attempts for "
        f"task={task} split={split} sample_index={sample_index} neighbor_index={neighbor_index}: {last_error}"
    ) from last_error


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
    sample_indices = args.sample_index or [0]
    neighbor_indices = args.neighbor_index or [1, 4, 6]

    rows: list[dict[str, Any]] = []
    for sample_index in sample_indices:
        candidate_json_path = _candidate_path(
            candidate_root=args.candidate_root,
            split=args.split,
            task=args.task,
            sample_index=sample_index,
        )
        candidate_payload = load_json(candidate_json_path)
        for neighbor_index in neighbor_indices:
            output_payload = _run_one(
                candidate_payload=candidate_payload,
                candidate_json_path=candidate_json_path,
                neighbor_index=neighbor_index,
                llm_config=llm_config,
                output_root=args.output_root,
                template_root=args.template_root,
                overwrite=args.overwrite,
                max_retries=args.max_retries,
                retry_delay_s=args.retry_delay_s,
                output_provider=args.output_provider,
                output_model=args.output_model,
            )
            rows.append(
                {
                    "task": args.task,
                    "split": args.split,
                    "sample_index": int(sample_index),
                    "neighbor_index": int(neighbor_index),
                    "output_path": serialize_project_path(
                        resolve_project_path(output_payload["prompt_path"]).parent / "result.json"
                    ),
                    "meta_reference_free": bool(
                        output_payload.get("post_checks", {}).get("meta_reference_free")
                    ),
                }
            )

    summary = {
        "schema_version": "trim_local_neighbor_rewrite_examples_summary_v1",
        "provider": llm_config.provider,
        "output_provider": str(args.output_provider or llm_config.provider),
        "output_model": str(args.output_model or llm_config.model),
        "model": llm_config.model,
        "task": args.task,
        "split": args.split,
        "sample_indices": [int(index) for index in sample_indices],
        "neighbor_indices": [int(index) for index in neighbor_indices],
        "output_root": serialize_project_path(resolve_project_path(args.output_root)),
        "rows": rows,
    }
    summary_path = (
        resolve_project_path(args.output_root)
        / str(args.output_provider or llm_config.provider)
        / model_slug(str(args.output_model or llm_config.model))
        / "local_neighbor"
        / args.split
        / args.task
        / "examples_summary.json"
    )
    save_json(summary_path, summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
