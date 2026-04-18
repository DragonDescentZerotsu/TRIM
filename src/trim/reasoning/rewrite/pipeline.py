from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import re
import time
from typing import Any

from trim.reasoning.rewrite.candidates import build_rewrite_candidates
from trim.reasoning.rewrite.llm import (
    LLMRequestConfig,
    extract_json_from_response_text,
    run_chat_completion,
)
from trim.reasoning.rewrite.rendering import render_rewrite_prompt
from trim.utils.io import ensure_directory, load_json, save_json
from trim.utils.paths import OUTPUTS_ROOT, resolve_project_path

try:
    from tqdm.auto import tqdm
except Exception:  # pragma: no cover - tqdm is optional in some environments
    def tqdm(iterable=None, **kwargs):
        return iterable


DEFAULT_FILTERED_ROOT = OUTPUTS_ROOT / "reasoning_rewrite_filters"
DEFAULT_CANDIDATE_ROOT = OUTPUTS_ROOT / "reasoning_rewrite_candidates" / "from_filters"
DEFAULT_REWRITE_OUTPUT_ROOT = OUTPUTS_ROOT / "reasoning_rewrite_outputs"

_META_LANGUAGE_TERMS = (
    "draft",
    "playbook",
    "prompt",
    "input",
    "instruction",
    "pair score",
)

_HARD_FAIL_META_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("contribution_numeric", re.compile(r"contribution\s*[:=]?\s*[-+]?\d", re.IGNORECASE)),
    ("parenthesized_contribution_numeric", re.compile(r"\(contribution\s*[:=]?\s*[-+]?\d", re.IGNORECASE)),
    ("model_assigns_contribution", re.compile(r"model assigns .*contribution", re.IGNORECASE)),
    ("contribution_listed", re.compile(r"contribution listed", re.IGNORECASE)),
    ("contribution_interpreted", re.compile(r"contribution is interpreted", re.IGNORECASE)),
    ("contribution_recorded", re.compile(r"contribution is recorded", re.IGNORECASE)),
    ("contribution_here_is", re.compile(r"contribution here is", re.IGNORECASE)),
    ("feature_contribution", re.compile(r"feature contribution", re.IGNORECASE)),
    ("pairwise_contribution", re.compile(r"pairwise contribution", re.IGNORECASE)),
    ("weighted_contribution", re.compile(r"weighted contribution", re.IGNORECASE)),
    ("summed_contributions", re.compile(r"summed contributions", re.IGNORECASE)),
)


def model_slug(model_name: str) -> str:
    return (
        str(model_name)
        .strip()
        .replace("/", "__")
        .replace(":", "_")
        .replace(" ", "_")
    )


def load_filtered_kept_records(
    *,
    filtered_root: str | Path,
    split: str,
    task: str,
) -> list[dict[str, Any]]:
    kept_path = resolve_project_path(filtered_root) / split / task / "kept_records.json"
    records = json.loads(kept_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError(f"Expected list payload in {kept_path}")
    return [dict(record) for record in records]


def resolve_task_list(*, filtered_root: str | Path, split: str, requested_tasks: list[str] | None) -> list[str]:
    root = resolve_project_path(filtered_root) / split
    available = sorted(path.name for path in root.iterdir() if path.is_dir())
    if requested_tasks is None:
        return available
    requested = set(requested_tasks)
    selected = [task for task in available if task in requested]
    missing = sorted(requested.difference(selected))
    if missing:
        raise ValueError(f"Tasks not found in filtered root {root}: {missing}")
    return selected


def build_candidates_from_filtered_records(
    *,
    task: str,
    split: str,
    filtered_root: str | Path,
    global_root: str | Path,
    local_root: str | Path,
    playbook_root: str | Path,
    candidate_root: str | Path = DEFAULT_CANDIDATE_ROOT,
    max_samples: int | None = None,
) -> dict[str, Any]:
    kept_records = load_filtered_kept_records(filtered_root=filtered_root, split=split, task=task)
    sample_indices = [int(record["sample_index"]) for record in kept_records]
    if max_samples is not None:
        sample_indices = sample_indices[: int(max_samples)]
    return build_rewrite_candidates(
        global_dir=resolve_project_path(global_root) / task / split,
        local_dir=resolve_project_path(local_root) / task / split,
        output_dir=resolve_project_path(candidate_root) / split / task,
        playbook_root=playbook_root,
        sample_indices=sample_indices,
    )


def _rewrite_artifact_base(
    *,
    output_root: str | Path,
    provider: str,
    model: str,
    mode: str,
    split: str,
    task: str,
) -> Path:
    return ensure_directory(resolve_project_path(output_root) / provider / model_slug(model) / mode / split / task)


def _sample_artifact_dir(
    *,
    output_root: str | Path,
    provider: str,
    model: str,
    mode: str,
    split: str,
    task: str,
    sample_index: int,
) -> Path:
    return ensure_directory(
        _rewrite_artifact_base(
            output_root=output_root,
            provider=provider,
            model=model,
            mode=mode,
            split=split,
            task=task,
        )
        / f"sample_{int(sample_index):05d}"
    )


def load_mode_output_json(
    *,
    output_root: str | Path,
    provider: str,
    model: str,
    mode: str,
    split: str,
    task: str,
    sample_index: int,
) -> dict[str, Any]:
    path = _sample_artifact_dir(
        output_root=output_root,
        provider=provider,
        model=model,
        mode=mode,
        split=split,
        task=task,
        sample_index=sample_index,
    ) / "result.json"
    return load_json(path)


def reasoning_key_for_mode(mode: str) -> str:
    if mode == "global":
        return "reasoning"
    if mode == "local":
        return "reasoning"
    if mode == "hybrid":
        return "reasoning"
    raise ValueError(f"Unsupported rewrite mode for reasoning key lookup: {mode}")


def extract_reasoning_text_for_mode(*, payload: dict[str, Any], mode: str) -> str:
    parsed_output = payload.get("parsed_output")
    if not isinstance(parsed_output, dict):
        raise ValueError("Saved rewrite payload does not contain a parsed_output object")
    reasoning_key = reasoning_key_for_mode(mode)
    value = parsed_output.get(reasoning_key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Saved rewrite payload is missing non-empty {reasoning_key}")
    return value.strip()


def collect_reasoning_post_checks(*, mode: str, parsed_output: dict[str, Any]) -> dict[str, Any]:
    reasoning_key = reasoning_key_for_mode(mode)
    reasoning_text = str(parsed_output.get(reasoning_key, "") or "")
    lowered = reasoning_text.lower()
    meta_terms_found = [term for term in _META_LANGUAGE_TERMS if term in lowered]
    meta_patterns_found = [
        pattern_name
        for pattern_name, pattern in _HARD_FAIL_META_PATTERNS
        if pattern.search(reasoning_text)
    ]
    return {
        "reasoning_key": reasoning_key,
        "meta_reference_free": len(meta_terms_found) == 0 and len(meta_patterns_found) == 0,
        "meta_terms_found": meta_terms_found,
        "meta_patterns_found": meta_patterns_found,
    }


def validate_saved_rewrite_output(*, mode: str, payload: dict[str, Any]) -> None:
    parsed_output = payload.get("parsed_output")
    if not isinstance(parsed_output, dict):
        raise ValueError("Saved rewrite payload does not contain a parsed_output object")

    extract_reasoning_text_for_mode(payload=payload, mode=mode)

    post_checks = payload.get("post_checks")
    if not isinstance(post_checks, dict):
        post_checks = collect_reasoning_post_checks(mode=mode, parsed_output=parsed_output)
    if not bool(post_checks.get("meta_reference_free")):
        meta_terms = list(post_checks.get("meta_terms_found", []) or [])
        meta_patterns = list(post_checks.get("meta_patterns_found", []) or [])
        found_items = meta_terms + meta_patterns
        raise ValueError(
            f"Rewrite post-check failed for mode={mode}: meta terms found {found_items!r}"
        )


def _build_rewrite_output_payload(
    *,
    candidate_payload: dict[str, Any],
    mode: str,
    llm_config: LLMRequestConfig,
    sample_index: int,
    prompt_path: Path,
    raw_text_path: Path,
    parsed_output: dict[str, Any],
    post_checks: dict[str, Any],
    response_content: str,
    raw_response: Any,
    attempt_count: int,
    recovered_from_existing_response_text: bool = False,
) -> dict[str, Any]:
    return {
        "schema_version": "trim_reasoning_rewrite_output_v1",
        "mode": mode,
        "provider": llm_config.provider,
        "model": llm_config.model,
        "api_base": llm_config.api_base,
        "task": str(candidate_payload["task"]),
        "split": str(candidate_payload["split"]),
        "sample_id": str(candidate_payload["sample_id"]),
        "sample_index": int(sample_index),
        "prompt_path": str(prompt_path.resolve()),
        "response_text_path": str(raw_text_path.resolve()),
        "candidate_json_path": str(candidate_payload.get("_candidate_json_path", "")),
        "parsed_output": parsed_output,
        "post_checks": post_checks,
        "response_content": response_content,
        "raw_response": raw_response,
        "attempt_count": int(attempt_count),
        "recovered_from_existing_response_text": bool(recovered_from_existing_response_text),
    }


def _recover_saved_response_output(
    *,
    candidate_payload: dict[str, Any],
    mode: str,
    llm_config: LLMRequestConfig,
    sample_index: int,
    prompt_path: Path,
    raw_text_path: Path,
    output_path: Path,
) -> dict[str, Any] | None:
    if not raw_text_path.exists():
        return None

    response_content = raw_text_path.read_text(encoding="utf-8")
    parsed_output = extract_json_from_response_text(response_content)
    post_checks = collect_reasoning_post_checks(mode=mode, parsed_output=parsed_output)
    payload = _build_rewrite_output_payload(
        candidate_payload=candidate_payload,
        mode=mode,
        llm_config=llm_config,
        sample_index=sample_index,
        prompt_path=prompt_path,
        raw_text_path=raw_text_path,
        parsed_output=parsed_output,
        post_checks=post_checks,
        response_content=response_content,
        raw_response={"recovered_from_response_text": True},
        attempt_count=0,
        recovered_from_existing_response_text=True,
    )
    validate_saved_rewrite_output(mode=mode, payload=payload)
    save_json(output_path, payload)
    return payload


def run_single_rewrite(
    *,
    candidate_payload: dict[str, Any],
    mode: str,
    llm_config: LLMRequestConfig,
    output_root: str | Path = DEFAULT_REWRITE_OUTPUT_ROOT,
    template_root: str | Path | None = None,
    global_reasoning: str | None = None,
    local_reasoning: str | None = None,
    hybrid_reasoning: str | None = None,
    max_retries: int = 0,
    retry_delay_s: float = 0.0,
    skip_existing: bool = True,
) -> dict[str, Any]:
    split = str(candidate_payload["split"])
    task = str(candidate_payload["task"])
    sample_index = int(candidate_payload["sample_index"])
    sample_dir = _sample_artifact_dir(
        output_root=output_root,
        provider=llm_config.provider,
        model=llm_config.model,
        mode=mode,
        split=split,
        task=task,
        sample_index=sample_index,
    )
    output_path = sample_dir / "result.json"
    prompt_path = sample_dir / "prompt.md"
    raw_text_path = sample_dir / "response.txt"

    if skip_existing and output_path.exists():
        existing_payload = load_json(output_path)
        try:
            validate_saved_rewrite_output(mode=mode, payload=existing_payload)
            return existing_payload
        except Exception:
            pass

    prompt_text = render_rewrite_prompt(
        candidate_payload=candidate_payload,
        mode=mode,
        template_root=template_root,
        global_reasoning=global_reasoning,
        local_reasoning=local_reasoning,
        hybrid_reasoning=hybrid_reasoning,
    )
    prompt_path.write_text(prompt_text, encoding="utf-8")

    if skip_existing and not output_path.exists():
        try:
            recovered_payload = _recover_saved_response_output(
                candidate_payload=candidate_payload,
                mode=mode,
                llm_config=llm_config,
                sample_index=sample_index,
                prompt_path=prompt_path,
                raw_text_path=raw_text_path,
                output_path=output_path,
            )
            if recovered_payload is not None:
                return recovered_payload
        except Exception:
            pass

    total_attempts = max(1, int(max_retries) + 1)
    last_error: Exception | None = None
    for attempt_index in range(1, total_attempts + 1):
        try:
            completion = run_chat_completion(prompt=prompt_text, config=llm_config)
            raw_text_path.write_text(str(completion["content"]), encoding="utf-8")
            parsed_output = extract_json_from_response_text(str(completion["content"]))
            post_checks = collect_reasoning_post_checks(mode=mode, parsed_output=parsed_output)

            payload = _build_rewrite_output_payload(
                candidate_payload=candidate_payload,
                mode=mode,
                llm_config=llm_config,
                sample_index=sample_index,
                prompt_path=prompt_path,
                raw_text_path=raw_text_path,
                parsed_output=parsed_output,
                post_checks=post_checks,
                response_content=str(completion["content"]),
                raw_response=completion["raw_response"],
                attempt_count=attempt_index,
            )
            validate_saved_rewrite_output(mode=mode, payload=payload)
            save_json(output_path, payload)
            return payload
        except Exception as exc:
            last_error = exc
            if attempt_index >= total_attempts:
                break
            if retry_delay_s > 0:
                time.sleep(float(retry_delay_s))

    assert last_error is not None
    raise RuntimeError(
        f"Rewrite failed for task={task} split={split} sample_index={sample_index} mode={mode} "
        f"after {total_attempts} attempt(s): {last_error}"
    ) from last_error


def run_rewrite_batch(
    *,
    task: str,
    split: str,
    mode: str,
    llm_config: LLMRequestConfig,
    filtered_root: str | Path = DEFAULT_FILTERED_ROOT,
    global_root: str | Path,
    local_root: str | Path,
    playbook_root: str | Path,
    candidate_root: str | Path = DEFAULT_CANDIDATE_ROOT,
    output_root: str | Path = DEFAULT_REWRITE_OUTPUT_ROOT,
    template_root: str | Path | None = None,
    max_samples: int | None = None,
    max_concurrency: int = 1,
    max_retries: int = 0,
    retry_delay_s: float = 0.0,
    skip_existing: bool = True,
) -> dict[str, Any]:
    candidate_manifest = build_candidates_from_filtered_records(
        task=task,
        split=split,
        filtered_root=filtered_root,
        global_root=global_root,
        local_root=local_root,
        playbook_root=playbook_root,
        candidate_root=candidate_root,
        max_samples=max_samples,
    )
    candidate_dir = Path(candidate_manifest["artifacts"]["output_dir"])
    candidate_paths = sorted(candidate_dir.glob("sample_*.json"))

    requested_modes = ["global", "local", "hybrid"] if mode == "all" else [mode]

    def _process_candidate(candidate_path: Path) -> dict[str, Any]:
        candidate_payload = load_json(candidate_path)
        candidate_payload["_candidate_json_path"] = str(candidate_path.resolve())

        candidate_rows: list[dict[str, Any]] = []
        mode_outputs: dict[str, dict[str, Any]] = {}
        for requested_mode in requested_modes:
            try:
                if requested_mode == "hybrid":
                    global_output = mode_outputs.get("global")
                    if global_output is None:
                        global_output = load_mode_output_json(
                            output_root=output_root,
                            provider=llm_config.provider,
                            model=llm_config.model,
                            mode="global",
                            split=split,
                            task=task,
                            sample_index=int(candidate_payload["sample_index"]),
                        )
                    local_output = mode_outputs.get("local")
                    if local_output is None:
                        local_output = load_mode_output_json(
                            output_root=output_root,
                            provider=llm_config.provider,
                            model=llm_config.model,
                            mode="local",
                            split=split,
                            task=task,
                            sample_index=int(candidate_payload["sample_index"]),
                        )
                    output_payload = run_single_rewrite(
                        candidate_payload=candidate_payload,
                        mode="hybrid",
                        llm_config=llm_config,
                        output_root=output_root,
                        template_root=template_root,
                        global_reasoning=extract_reasoning_text_for_mode(payload=global_output, mode="global"),
                        local_reasoning=extract_reasoning_text_for_mode(payload=local_output, mode="local"),
                        max_retries=max_retries,
                        retry_delay_s=retry_delay_s,
                        skip_existing=skip_existing,
                    )
                else:
                    output_payload = run_single_rewrite(
                        candidate_payload=candidate_payload,
                        mode=requested_mode,
                        llm_config=llm_config,
                        output_root=output_root,
                        template_root=template_root,
                        max_retries=max_retries,
                        retry_delay_s=retry_delay_s,
                        skip_existing=skip_existing,
                    )
                mode_outputs[requested_mode] = output_payload
                candidate_rows.append(
                    {
                        "task": task,
                        "split": split,
                        "sample_index": int(candidate_payload["sample_index"]),
                        "mode": requested_mode,
                        "status": "succeeded",
                        "output_path": str(
                            (
                                _sample_artifact_dir(
                                    output_root=output_root,
                                    provider=llm_config.provider,
                                    model=llm_config.model,
                                    mode=requested_mode,
                                    split=split,
                                    task=task,
                                    sample_index=int(candidate_payload["sample_index"]),
                                )
                                / "result.json"
                            ).resolve()
                        ),
                    }
                )
            except Exception as exc:
                return {
                    "status": "failed",
                    "task": task,
                    "split": split,
                    "sample_index": int(candidate_payload["sample_index"]),
                    "sample_id": str(candidate_payload.get("sample_id", "")),
                    "failed_mode": requested_mode,
                    "candidate_path": str(candidate_path.resolve()),
                    "error": f"{type(exc).__name__}: {exc}",
                    "rows": candidate_rows,
                }
        return {
            "status": "succeeded",
            "sample_index": int(candidate_payload["sample_index"]),
            "rows": candidate_rows,
        }

    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    resolved_max_concurrency = max(1, int(max_concurrency))
    progress_desc = f"{task} ({mode})"
    if resolved_max_concurrency == 1 or len(candidate_paths) <= 1:
        for candidate_path in tqdm(candidate_paths, total=len(candidate_paths), desc=progress_desc):
            result = _process_candidate(candidate_path)
            rows.extend(result.get("rows", []))
            if result.get("status") != "succeeded":
                failures.append({key: value for key, value in result.items() if key != "rows"})
    else:
        with ThreadPoolExecutor(max_workers=resolved_max_concurrency) as executor:
            future_to_path = {executor.submit(_process_candidate, candidate_path): candidate_path for candidate_path in candidate_paths}
            for future in tqdm(as_completed(future_to_path), total=len(future_to_path), desc=progress_desc):
                result = future.result()
                rows.extend(result.get("rows", []))
                if result.get("status") != "succeeded":
                    failures.append({key: value for key, value in result.items() if key != "rows"})

    mode_order = {requested_mode: index for index, requested_mode in enumerate(requested_modes)}
    rows.sort(key=lambda row: (int(row["sample_index"]), mode_order[str(row["mode"])]))
    failures.sort(key=lambda row: int(row["sample_index"]))

    summary = {
        "schema_version": "trim_reasoning_rewrite_batch_summary_v1",
        "provider": llm_config.provider,
        "model": llm_config.model,
        "task": task,
        "split": split,
        "mode": mode,
        "candidate_manifest": candidate_manifest,
        "num_candidates": int(len(candidate_paths)),
        "max_concurrency": int(resolved_max_concurrency),
        "max_retries": int(max_retries),
        "retry_delay_s": float(retry_delay_s),
        "num_succeeded": int(len(candidate_paths) - len(failures)),
        "num_failed": int(len(failures)),
        "failures": failures,
        "rows": rows,
    }
    summary_dir = _rewrite_artifact_base(
        output_root=output_root,
        provider=llm_config.provider,
        model=llm_config.model,
        mode=mode,
        split=split,
        task=task,
    )
    save_json(summary_dir / "manifest.json", summary)
    return summary
