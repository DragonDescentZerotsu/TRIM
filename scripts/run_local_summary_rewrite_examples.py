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
from trim.reasoning.rewrite.neighbor_selection import (
    display_index_by_source_index,
    format_neighbor_names,
    parse_source_neighbor_indices,
)
from trim.reasoning.rewrite.rendering import render_rewrite_prompt
from trim.utils.io import load_json, save_json
from trim.utils.paths import resolve_project_path, serialize_project_path


DEFAULT_CANDIDATE_ROOT = "outputs/reasoning_rewrite_candidates/from_filters"
DEFAULT_NEIGHBOR_OUTPUT_ROOT = "outputs/reasoning_rewrite_outputs_neighbor_level"
DEFAULT_OUTPUT_ROOT = "outputs/reasoning_rewrite_outputs_neighbor_level"

_REQUIRED_QUALITY_CHECKS: tuple[str, ...] = (
    "uses_all_selected_neighbors",
    "uses_similarity_and_evidence_strength",
    "handles_conflicting_neighbors",
    "uses_neighbor_level_predictions_as_votes",
    "does_not_add_new_descriptor_evidence",
    "preserves_neighbor_predictions",
    "preserves_neighbor_strengths",
    "final_prediction_matches_required_label",
    "no_meta_references",
)
_QUALITY_CHECK_ALIASES: dict[str, tuple[str, ...]] = {
    "uses_all_selected_neighbors": ("uses_all_six_neighbors",),
}


def _neighbor_prediction_counts(neighbor_outputs: dict[int, dict[str, Any]]) -> dict[str, int]:
    counts = {"A": 0, "B": 0}
    for neighbor_index, payload in sorted(neighbor_outputs.items()):
        parsed = payload.get("parsed_output", payload)
        if not isinstance(parsed, dict):
            raise ValueError(f"Neighbor {neighbor_index} output must be a JSON object")
        prediction = parsed.get("neighbor_prediction")
        if not isinstance(prediction, dict):
            raise ValueError(f"Neighbor {neighbor_index} output is missing neighbor_prediction")
        option = prediction.get("option")
        if option not in counts:
            raise ValueError(f"Neighbor {neighbor_index} has invalid prediction option: {option!r}")
        counts[str(option)] += 1
    return counts


def _count_phrase_present(reasoning: str, *, option: str, count: int) -> bool:
    option_label = re.escape(option)
    option_pattern = rf"option\s*\({option_label}\)"
    count_pattern = rf"{int(count)}"
    patterns = (
        # option (A) has 0 neighbors / receives 0 votes
        rf"{option_pattern}[^.{{}};\n]{{0,100}}\b{count_pattern}\s+(?:neighbors?|votes?)\b",
        # 0 neighbors / votes for option (A)
        rf"\b{count_pattern}\s+(?:neighbors?|votes?)\b[^.{{}};\n]{{0,100}}{option_pattern}",
        # 0 for option (A)
        rf"\b{count_pattern}\s+for\s+{option_pattern}",
        # option (A)=0 / A=0
        rf"{option_pattern}\s*=\s*{count_pattern}\b",
        rf"\b{option_label}\s*=\s*{count_pattern}\b",
    )
    return any(re.search(pattern, reasoning, flags=re.IGNORECASE) for pattern in patterns)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run local summary rewrite examples from existing per-neighbor rewrite outputs."
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
    parser.add_argument("--task", required=True)
    parser.add_argument("--sample-index", type=int, required=True)
    parser.add_argument("--candidate-root", default=DEFAULT_CANDIDATE_ROOT)
    parser.add_argument("--neighbor-output-root", default=DEFAULT_NEIGHBOR_OUTPUT_ROOT)
    parser.add_argument("--neighbor-output-provider", default=None)
    parser.add_argument("--neighbor-output-model", default=None)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--template-root", default="prompt_templates/reasoning_sft")
    parser.add_argument(
        "--summary-source-neighbor-indices",
        default="1,2,3,4,5,6",
        help=(
            "Comma-separated original per-neighbor indices to include in the summary. "
            "For two neighbors per label use 1,2,4,5; they are displayed as Neighbor 1..4."
        ),
    )
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


def _neighbor_result_path(
    *,
    root: str | Path,
    provider: str,
    model: str,
    split: str,
    task: str,
    sample_index: int,
    neighbor_index: int,
) -> Path:
    return (
        resolve_project_path(root)
        / provider
        / model_slug(model)
        / "local_neighbor"
        / split
        / task
        / f"sample_{int(sample_index):05d}"
        / f"neighbor_{int(neighbor_index):02d}"
        / "result.json"
    )


def _summary_output_dir(
    *,
    root: str | Path,
    provider: str,
    model: str,
    split: str,
    task: str,
    sample_index: int,
) -> Path:
    path = (
        resolve_project_path(root)
        / provider
        / model_slug(model)
        / "local_summary"
        / split
        / task
        / f"sample_{int(sample_index):05d}"
    )
    path.mkdir(parents=True, exist_ok=True)
    return path


def _load_neighbor_outputs(
    *,
    root: str | Path,
    provider: str,
    model: str,
    split: str,
    task: str,
    sample_index: int,
    source_neighbor_indices: object = None,
) -> dict[int, dict[str, Any]]:
    outputs: dict[int, dict[str, Any]] = {}
    for neighbor_index in parse_source_neighbor_indices(source_neighbor_indices):
        path = _neighbor_result_path(
            root=root,
            provider=provider,
            model=model,
            split=split,
            task=task,
            sample_index=sample_index,
            neighbor_index=neighbor_index,
        )
        outputs[neighbor_index] = load_json(path)
    return outputs


def _expected_local_label(candidate_payload: dict[str, Any]) -> int:
    return int(candidate_payload["local_rewrite_input"]["local_prediction"])


def _validate_summary_output(
    *,
    parsed_output: dict[str, Any],
    candidate_payload: dict[str, Any],
    neighbor_outputs: dict[int, dict[str, Any]],
    source_neighbor_indices: object = None,
) -> None:
    quality_check = parsed_output.get("quality_check")
    if not isinstance(quality_check, dict) or not quality_check:
        raise ValueError("parsed_output.quality_check must be a non-empty object")
    missing_checks = []
    for name in _REQUIRED_QUALITY_CHECKS:
        aliases = _QUALITY_CHECK_ALIASES.get(name, ())
        if name not in quality_check and not any(alias in quality_check for alias in aliases):
            missing_checks.append(name)
    if missing_checks:
        raise ValueError(f"summary quality_check is missing required fields: {missing_checks!r}")
    failed_checks = [
        name for name, value in quality_check.items() if value is not True
    ]
    if failed_checks:
        raise ValueError(f"summary quality_check fields are not true: {failed_checks!r}")

    prediction = parsed_output.get("local_prediction")
    if not isinstance(prediction, dict):
        raise ValueError("parsed_output.local_prediction must be an object")
    observed_label = int(prediction.get("label", -1))
    expected_label = _expected_local_label(candidate_payload)
    if observed_label != expected_label:
        raise ValueError(f"local_prediction.label mismatch: expected {expected_label}, got {observed_label}")

    reasoning = str(parsed_output.get("reasoning", "") or "")
    source_indices = parse_source_neighbor_indices(source_neighbor_indices)
    missing_neighbors = [
        index
        for index in range(1, len(source_indices) + 1)
        if not re.search(rf"\bNeighbors?\s*{index}\b", reasoning)
    ]
    if missing_neighbors:
        raise ValueError(
            "summary reasoning does not mention all selected display neighbors "
            f"({format_neighbor_names(len(source_indices))}); missing {missing_neighbors}"
        )

    counts = _neighbor_prediction_counts(neighbor_outputs)
    missing_count_phrases = [
        f"option ({option}) = {count}"
        for option, count in sorted(counts.items())
        if not _count_phrase_present(reasoning, option=option, count=count)
    ]
    if missing_count_phrases:
        raise ValueError(
            "summary reasoning does not state the exact neighbor-level vote count: "
            f"{missing_count_phrases!r}"
        )


def run_one_summary_rewrite(
    *,
    candidate_payload: dict[str, Any],
    candidate_json_path: Path,
    neighbor_outputs: dict[int, dict[str, Any]],
    llm_config,
    output_root: str | Path,
    neighbor_output_root: str | Path,
    template_root: str | Path,
    overwrite: bool,
    max_retries: int,
    retry_delay_s: float = 0.0,
    output_provider: str | None = None,
    output_model: str | None = None,
    neighbor_output_provider: str | None = None,
    neighbor_output_model: str | None = None,
    source_neighbor_indices: object = None,
) -> dict[str, Any]:
    split = str(candidate_payload["split"])
    task = str(candidate_payload["task"])
    sample_index = int(candidate_payload["sample_index"])
    storage_provider = str(output_provider or llm_config.provider)
    storage_model = str(output_model or llm_config.model)
    neighbor_storage_provider = str(neighbor_output_provider or storage_provider)
    neighbor_storage_model = str(neighbor_output_model or storage_model)
    sample_output_dir = _summary_output_dir(
        root=output_root,
        provider=storage_provider,
        model=storage_model,
        split=split,
        task=task,
        sample_index=sample_index,
    )
    result_path = sample_output_dir / "result.json"
    prompt_path = sample_output_dir / "prompt.md"
    response_path = sample_output_dir / "response.txt"

    if result_path.exists() and not overwrite:
        payload = load_json(result_path)
        validate_saved_rewrite_output(mode="local_summary", payload=payload)
        expected_source_indices = [int(index) for index in parse_source_neighbor_indices(source_neighbor_indices)]
        saved_source_indices = payload.get("selected_source_neighbor_indices")
        if saved_source_indices is not None and [int(index) for index in saved_source_indices] != expected_source_indices:
            raise ValueError(
                "Saved local_summary selected_source_neighbor_indices mismatch: "
                f"expected {expected_source_indices}, got {saved_source_indices}"
            )
        _validate_summary_output(
            parsed_output=dict(payload["parsed_output"]),
            candidate_payload=candidate_payload,
            neighbor_outputs=neighbor_outputs,
            source_neighbor_indices=source_neighbor_indices,
        )
        return payload

    prompt_text = render_rewrite_prompt(
        candidate_payload=candidate_payload,
        mode="local_summary",
        template_root=template_root,
        local_neighbor_outputs=neighbor_outputs,
        summary_source_neighbor_indices=source_neighbor_indices,
    )
    prompt_path.write_text(prompt_text, encoding="utf-8")

    total_attempts = max(1, int(max_retries) + 1)
    last_error: Exception | None = None
    for attempt_index in range(1, total_attempts + 1):
        try:
            completion = run_chat_completion(prompt=prompt_text, config=llm_config)
            response_content = str(completion["content"])
            response_path.write_text(response_content, encoding="utf-8")
            parsed_output = extract_json_from_response_text(response_content)
            _validate_summary_output(
                parsed_output=parsed_output,
                candidate_payload=candidate_payload,
                neighbor_outputs=neighbor_outputs,
                source_neighbor_indices=source_neighbor_indices,
            )
            post_checks = collect_reasoning_post_checks(mode="local_summary", parsed_output=parsed_output)
            source_indices = parse_source_neighbor_indices(source_neighbor_indices)
            source_to_display = display_index_by_source_index(source_indices)
            result_payload = {
                "schema_version": "trim_reasoning_rewrite_output_v1",
                "mode": "local_summary",
                "provider": llm_config.provider,
                "output_provider": storage_provider,
                "output_model": storage_model,
                "model": llm_config.model,
                "api_base": llm_config.api_base,
                "task": task,
                "split": split,
                "sample_id": str(candidate_payload["sample_id"]),
                "sample_index": int(sample_index),
                "prompt_path": serialize_project_path(prompt_path),
                "response_text_path": serialize_project_path(response_path),
                "candidate_json_path": serialize_project_path(candidate_json_path),
                "neighbor_result_paths": {
                    str(source_to_display[index]): serialize_project_path(
                        _neighbor_result_path(
                            root=neighbor_output_root,
                            provider=neighbor_storage_provider,
                            model=neighbor_storage_model,
                            split=split,
                            task=task,
                            sample_index=sample_index,
                            neighbor_index=index,
                        )
                    )
                    for index in source_indices
                },
                "selected_source_neighbor_indices": [int(index) for index in source_indices],
                "summary_neighbor_index_map": {
                    str(source_index): int(display_index)
                    for source_index, display_index in source_to_display.items()
                },
                "source_local_prediction_semantics": str(
                    candidate_payload["local_rewrite_input"]["local_prediction_semantics"]
                ),
                "parsed_output": parsed_output,
                "post_checks": post_checks,
                "response_content": response_content,
                "raw_response": completion["raw_response"],
                "attempt_count": attempt_index,
            }
            validate_saved_rewrite_output(mode="local_summary", payload=result_payload)
            save_json(result_path, result_payload)
            return result_payload
        except Exception as exc:
            last_error = exc
            if attempt_index < total_attempts and retry_delay_s > 0:
                time.sleep(float(retry_delay_s))

    assert last_error is not None
    raise RuntimeError(
        f"Local-summary rewrite failed after {total_attempts} attempts for "
        f"task={task} split={split} sample_index={sample_index}: {last_error}"
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

    candidate_json_path = _candidate_path(
        candidate_root=args.candidate_root,
        split=args.split,
        task=args.task,
        sample_index=args.sample_index,
    )
    candidate_payload = load_json(candidate_json_path)
    neighbor_outputs = _load_neighbor_outputs(
        root=args.neighbor_output_root,
        provider=str(args.neighbor_output_provider or args.output_provider or llm_config.provider),
        model=str(args.neighbor_output_model or args.output_model or llm_config.model),
        split=args.split,
        task=args.task,
        sample_index=args.sample_index,
        source_neighbor_indices=args.summary_source_neighbor_indices,
    )
    result_payload = run_one_summary_rewrite(
        candidate_payload=candidate_payload,
        candidate_json_path=candidate_json_path,
        neighbor_outputs=neighbor_outputs,
        llm_config=llm_config,
        output_root=args.output_root,
        neighbor_output_root=args.neighbor_output_root,
        template_root=args.template_root,
        overwrite=args.overwrite,
        max_retries=args.max_retries,
        retry_delay_s=args.retry_delay_s,
        output_provider=args.output_provider,
        output_model=args.output_model,
        neighbor_output_provider=args.neighbor_output_provider,
        neighbor_output_model=args.neighbor_output_model,
        source_neighbor_indices=args.summary_source_neighbor_indices,
    )
    print(json.dumps(result_payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
