from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, Future, ProcessPoolExecutor, wait
import json
from pathlib import Path
from typing import Any

from trim.data.datasets import load_tdc_split
from trim.reasoning.rewrite.pipeline import extract_reasoning_text_for_mode, load_mode_output_json, model_slug
from trim.reasoning.semantics.task_semantics import load_brief_task_semantics, load_task_label_semantics
from trim.reasoning.task_user_prompts import (
    DEFAULT_TASK_MANIFEST_INDEX,
    DEFAULT_TASK_USER_PROMPT_ROOT,
    load_task_names_from_manifest_index,
    render_task_user_message,
)
from trim.utils.io import ensure_directory
from trim.utils.paths import DATA_ROOT, DEFAULT_PROCESSED_DATA_ROOT, OUTPUTS_ROOT, resolve_project_path

try:
    from tqdm.auto import tqdm
except Exception:  # pragma: no cover - tqdm is optional in some environments
    def tqdm(iterable=None, **kwargs):
        return iterable


AGENT_REASONING_SFT_SCHEMA_VERSION = "trim_agent_reasoning_sft_messages_v1"
DEFAULT_AGENT_REASONING_SFT_OUTPUT_ROOT = DATA_ROOT / "sft" / "agent_reasoning_messages"
DEFAULT_REWRITE_OUTPUT_ROOT = OUTPUTS_ROOT / "reasoning_rewrite_outputs"
DEFAULT_REWRITE_FILTER_ROOT = OUTPUTS_ROOT / "reasoning_rewrite_filters"
DEFAULT_REWRITE_PROVIDER = "openrouter"
DEFAULT_REWRITE_MODEL = "openai/gpt-5.4-mini"
DEFAULT_AGENT_TOOL_FEATURE_SET_NAME = "fg_top_level+rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts"
DEFAULT_AGENT_TOOL_MANIFEST_ROOT = OUTPUTS_ROOT / "reasoning_agent_tools" / "manifests"
DEFAULT_TOOL_CACHE_ROOT = "data/cache/tdc_mol_fingerprints"
SFT_MODE_FULL = "full"
SFT_MODE_GLOBAL_ONLY = "global_only"
SFT_MODE_LOCAL_ONLY = "local_only"
SFT_MODES = (SFT_MODE_FULL, SFT_MODE_GLOBAL_ONLY, SFT_MODE_LOCAL_ONLY)

GET_MOL_PROPERTIES_TOOL_NAME = "get_mol_properties_and_fg"
COMPARE_SIMILAR_MOLS_TOOL_NAME = "compare_similar_mols"
GET_MOL_PROPERTIES_CALL_ID = "call_get_mol_properties_and_fg"
COMPARE_SIMILAR_MOLS_CALL_ID = "call_compare_similar_mols"

GLOBAL_TOOL_BRIDGE_TEMPLATE = (
    "We need to predict {brief_task_semantics} for the given SMILES. "
    "We can use the tool get_mol_properties_and_fg to get actual properties and functional groups, "
    "then base our prediction on this information. Let's call it."
)
GLOBAL_TOOL_BRIDGE = GLOBAL_TOOL_BRIDGE_TEMPLATE.format(brief_task_semantics="the target drug property")
LOCAL_TOOL_BRIDGE = (
    "We can also use compare_similar_mols to see similar compounds to make more informed predictions. Let's try."
)
LOCAL_ONLY_TOOL_BRIDGE_TEMPLATE = (
    "We need to predict {brief_task_semantics} for the given SMILES. "
    "We can use the tool compare_similar_mols to retrieve similar compounds and compare them with the query, "
    "then base our prediction on this neighbor evidence. Let's call it."
)

_AGENT_SFT_WORKER_CONTEXT: dict[str, Any] = {}


def _dataset_output_dir(
    *,
    output_root: str | Path,
    provider: str,
    model: str,
    split: str,
    sft_mode: str = SFT_MODE_FULL,
) -> Path:
    validated_mode = _validate_sft_mode(sft_mode)
    root = resolve_project_path(output_root) / provider / model_slug(model)
    if validated_mode != SFT_MODE_FULL:
        root = root / validated_mode
    return ensure_directory(root / split)


def _validate_sft_mode(sft_mode: str) -> str:
    normalized = str(sft_mode).strip()
    if normalized not in SFT_MODES:
        raise ValueError(f"Unsupported SFT mode {sft_mode!r}; expected one of {SFT_MODES}")
    return normalized


def _rewrite_modes_for_sft_mode(sft_mode: str) -> tuple[str, ...]:
    validated_mode = _validate_sft_mode(sft_mode)
    if validated_mode == SFT_MODE_GLOBAL_ONLY:
        return ("global",)
    if validated_mode == SFT_MODE_LOCAL_ONLY:
        return ("local",)
    return ("global", "local", "hybrid")


def _read_jsonl_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            parsed = json.loads(stripped)
            if not isinstance(parsed, dict):
                raise ValueError(f"Expected JSON object line in {path}")
            records.append(parsed)
    return records


def _longest_matching_prefix_length(
    *,
    existing_indices: list[int],
    target_indices: list[int],
) -> int:
    prefix_len = 0
    for existing_index, target_index in zip(existing_indices, target_indices, strict=False):
        if int(existing_index) != int(target_index):
            break
        prefix_len += 1
    return prefix_len


def _load_existing_task_records(
    *,
    output_path: Path,
    task: str,
    split: str,
    sft_mode: str = SFT_MODE_FULL,
    target_indices: list[int],
) -> list[dict[str, Any]]:
    existing_records = _read_jsonl_records(output_path)
    if not existing_records:
        return []

    existing_indices: list[int] = []
    for record in existing_records:
        if str(record.get("task")) != task:
            raise ValueError(f"Existing JSONL task mismatch in {output_path}: {record.get('task')!r}")
        if str(record.get("split")) != split:
            raise ValueError(f"Existing JSONL split mismatch in {output_path}: {record.get('split')!r}")
        existing_mode = record.get("sft_mode")
        if existing_mode is not None and str(existing_mode) != sft_mode:
            raise ValueError(f"Existing JSONL SFT mode mismatch in {output_path}: {existing_mode!r}")
        sample_index = int(record["sample_index"])
        existing_indices.append(sample_index)

    if len(existing_indices) != len(set(existing_indices)):
        raise ValueError(f"Duplicate sample_index entries found in existing JSONL: {output_path}")
    if existing_indices != sorted(existing_indices):
        raise ValueError(f"Existing JSONL is not sorted by sample_index: {output_path}")

    prefix_len = _longest_matching_prefix_length(
        existing_indices=existing_indices,
        target_indices=target_indices,
    )
    prefix_records = existing_records[:prefix_len]

    if prefix_len < len(existing_records):
        with output_path.open("w", encoding="utf-8") as handle:
            for record in prefix_records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    return prefix_records


def _append_jsonl_record(handle, record: dict[str, Any]) -> None:
    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    handle.flush()


def _rewrite_result_path(
    *,
    output_root: str | Path,
    provider: str,
    model: str,
    mode: str,
    split: str,
    task: str,
    sample_index: int,
) -> Path:
    return (
        resolve_project_path(output_root)
        / provider
        / model_slug(model)
        / mode
        / split
        / task
        / f"sample_{int(sample_index):05d}"
        / "result.json"
    )


def _sample_indices_with_saved_rewrites(
    *,
    rewrite_output_root: str | Path,
    provider: str,
    model: str,
    mode: str,
    split: str,
    task: str,
) -> set[int]:
    mode_root = (
        resolve_project_path(rewrite_output_root)
        / provider
        / model_slug(model)
        / mode
        / split
        / task
    )
    if not mode_root.exists():
        raise FileNotFoundError(f"Rewrite output directory does not exist for mode={mode}: {mode_root}")

    sample_indices: set[int] = set()
    for result_path in sorted(mode_root.glob("sample_*/result.json")):
        sample_dir = result_path.parent.name
        try:
            sample_index = int(sample_dir.split("_")[-1])
        except ValueError as exc:
            raise ValueError(f"Could not parse sample index from rewrite artifact path: {result_path}") from exc
        sample_indices.add(sample_index)

    if not sample_indices:
        raise FileNotFoundError(f"No saved rewrite outputs found under {mode_root}")
    return sample_indices


def _load_rewrite_filter_records(
    *,
    filter_root: str | Path,
    split: str,
    task: str,
) -> list[dict[str, Any]]:
    records_path = resolve_project_path(filter_root) / split / task / "kept_records.json"
    if not records_path.exists():
        raise FileNotFoundError(
            f"Rewrite filter records are required for ablation SFT modes but were not found: {records_path}"
        )
    payload = json.loads(records_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Expected a JSON list in rewrite filter records: {records_path}")

    records: list[dict[str, Any]] = []
    for row in payload:
        if not isinstance(row, dict):
            raise ValueError(f"Expected object rows in rewrite filter records: {records_path}")
        if str(row.get("task")) != task:
            raise ValueError(f"Rewrite filter task mismatch in {records_path}: {row.get('task')!r}")
        if str(row.get("split")) != split:
            raise ValueError(f"Rewrite filter split mismatch in {records_path}: {row.get('split')!r}")
        records.append(row)
    return records


def list_fully_rewritten_sample_indices(
    *,
    task: str,
    split: str,
    rewrite_output_root: str | Path = DEFAULT_REWRITE_OUTPUT_ROOT,
    provider: str = DEFAULT_REWRITE_PROVIDER,
    model: str = DEFAULT_REWRITE_MODEL,
) -> list[int]:
    mode_to_indices = {
        mode: _sample_indices_with_saved_rewrites(
            rewrite_output_root=rewrite_output_root,
            provider=provider,
            model=model,
            mode=mode,
            split=split,
            task=task,
        )
        for mode in ("global", "local", "hybrid")
    }

    shared_indices = sorted(set.intersection(*mode_to_indices.values()))
    if not shared_indices:
        raise FileNotFoundError(
            f"No shared fully rewritten samples found for task={task!r}, split={split!r}, "
            f"provider={provider!r}, model={model!r}"
        )
    return shared_indices


def list_rewritten_sample_indices_for_sft_mode(
    *,
    task: str,
    split: str,
    sft_mode: str = SFT_MODE_FULL,
    rewrite_output_root: str | Path = DEFAULT_REWRITE_OUTPUT_ROOT,
    rewrite_filter_root: str | Path = DEFAULT_REWRITE_FILTER_ROOT,
    provider: str = DEFAULT_REWRITE_PROVIDER,
    model: str = DEFAULT_REWRITE_MODEL,
) -> list[int]:
    validated_mode = _validate_sft_mode(sft_mode)
    if validated_mode == SFT_MODE_FULL:
        return list_fully_rewritten_sample_indices(
            task=task,
            split=split,
            rewrite_output_root=rewrite_output_root,
            provider=provider,
            model=model,
        )

    rewrite_mode = "global" if validated_mode == SFT_MODE_GLOBAL_ONLY else "local"
    correct_field = f"{rewrite_mode}_prediction_correct"
    records = _load_rewrite_filter_records(filter_root=rewrite_filter_root, split=split, task=task)
    correct_indices = {
        int(record["sample_index"])
        for record in records
        if bool(record.get(correct_field))
    }
    saved_indices = _sample_indices_with_saved_rewrites(
        rewrite_output_root=rewrite_output_root,
        provider=provider,
        model=model,
        mode=rewrite_mode,
        split=split,
        task=task,
    )
    selected_indices = sorted(correct_indices.intersection(saved_indices))
    if not selected_indices:
        raise FileNotFoundError(
            f"No rewritten {validated_mode} samples found for task={task!r}, split={split!r}, "
            f"provider={provider!r}, model={model!r}"
        )
    return selected_indices


def _tool_call(*, call_id: str, name: str, smiles: str) -> dict[str, Any]:
    return {
        "id": call_id,
        "type": "function",
        "function": {
            "name": name,
            "arguments": json.dumps({"smiles": smiles}, ensure_ascii=False),
        },
    }


def _require_non_empty_text(value: Any, *, context: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"Expected non-empty text for {context}")
    return text


def _load_reasoning_bundle(
    *,
    task: str,
    split: str,
    sample_index: int,
    rewrite_output_root: str | Path,
    provider: str,
    model: str,
    modes: tuple[str, ...] = ("global", "local", "hybrid"),
) -> dict[str, Any]:
    bundles: dict[str, dict[str, Any]] = {}
    paths: dict[str, str] = {}

    if not modes:
        raise ValueError("At least one rewrite mode is required")

    for mode in modes:
        result_path = _rewrite_result_path(
            output_root=rewrite_output_root,
            provider=provider,
            model=model,
            mode=mode,
            split=split,
            task=task,
            sample_index=sample_index,
        )
        payload = load_mode_output_json(
            output_root=rewrite_output_root,
            provider=provider,
            model=model,
            mode=mode,
            split=split,
            task=task,
            sample_index=sample_index,
        )
        if str(payload.get("task")) != task:
            raise ValueError(f"{mode} rewrite payload task mismatch for sample {sample_index}: {payload.get('task')!r}")
        if str(payload.get("split")) != split:
            raise ValueError(f"{mode} rewrite payload split mismatch for sample {sample_index}: {payload.get('split')!r}")
        if int(payload.get("sample_index")) != int(sample_index):
            raise ValueError(
                f"{mode} rewrite payload sample_index mismatch for task={task}: {payload.get('sample_index')!r}"
            )
        bundles[mode] = payload
        paths[f"{mode}_result_json"] = str(result_path.resolve())

    first_mode = modes[0]
    sample_id = str(bundles[first_mode].get("sample_id", "") or "")
    for mode in modes[1:]:
        other_sample_id = str(bundles[mode].get("sample_id", "") or "")
        if sample_id != other_sample_id:
            raise ValueError(
                f"Rewrite payload sample_id mismatch for task={task} sample_index={sample_index}: "
                f"{sample_id!r} != {other_sample_id!r}"
            )

    result: dict[str, Any] = {
        "sample_id": sample_id,
        "source_paths": paths,
    }
    for mode in modes:
        result[f"{mode}_reasoning"] = _require_non_empty_text(
            extract_reasoning_text_for_mode(payload=bundles[mode], mode=mode),
            context=f"{mode} reasoning for {task} sample {sample_index}",
        )
    return result


def _resolve_final_answer_option(task: str, gt_label: int) -> str:
    if int(gt_label) not in (0, 1):
        raise ValueError(f"Unsupported binary ground-truth label: {gt_label!r}")

    semantics = load_task_label_semantics(task)
    if semantics is not None:
        option_zero = str(semantics.get(0, {}).get("option", "")).strip()
        option_one = str(semantics.get(1, {}).get("option", "")).strip()
        if option_zero == "A" and option_one == "B":
            return option_zero if int(gt_label) == 0 else option_one

    return "A" if int(gt_label) == 0 else "B"


def build_global_tool_bridge(task: str) -> str:
    return GLOBAL_TOOL_BRIDGE_TEMPLATE.format(brief_task_semantics=load_brief_task_semantics(task))


def build_local_only_tool_bridge(task: str) -> str:
    return LOCAL_ONLY_TOOL_BRIDGE_TEMPLATE.format(brief_task_semantics=load_brief_task_semantics(task))


def build_task_tool_runner(
    *,
    task: str,
    feature_set_name: str = DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    manifest_root: str | Path = DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
    dataset_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT,
    cache_root: str | Path = DEFAULT_TOOL_CACHE_ROOT,
):
    from trim.reasoning.agent_tools import TaskReasoningAgentTools

    return TaskReasoningAgentTools.from_task(
        task=task,
        feature_set_name=feature_set_name,
        manifest_root=manifest_root,
        dataset_root=dataset_root,
        cache_root=cache_root,
    )


def _prewarm_tool_runner(tool_runner: Any, *, task: str, sft_mode: str = SFT_MODE_FULL) -> None:
    validated_mode = _validate_sft_mode(sft_mode)
    get_smiles_index = getattr(tool_runner, "_get_smiles_index", None)
    if callable(get_smiles_index):
        get_smiles_index()

    if validated_mode == SFT_MODE_GLOBAL_ONLY:
        return

    get_train_feature_cache = getattr(tool_runner, "_get_train_feature_cache", None)
    if callable(get_train_feature_cache):
        get_train_feature_cache()

    retriever = getattr(tool_runner, "retriever", None)
    if retriever is not None:
        load_train_metadata = getattr(retriever, "_load_train_metadata", None)
        if callable(load_train_metadata):
            load_train_metadata(task)
        load_similarity_file = getattr(retriever, "_load_similarity_file", None)
        if callable(load_similarity_file):
            for family in ("Morgan_similarity", "Feature_Morgan_similarity"):
                load_similarity_file(task, family, "train")


def _init_agent_sft_worker(
    task: str,
    split: str,
    sft_mode: str,
    rewrite_output_root: str,
    provider: str,
    model: str,
    prompt_root: str,
    feature_set_name: str,
    manifest_root: str,
    dataset_root: str,
    cache_root: str,
) -> None:
    tool_runner = build_task_tool_runner(
        task=task,
        feature_set_name=feature_set_name,
        manifest_root=manifest_root,
        dataset_root=dataset_root,
        cache_root=cache_root,
    )
    _prewarm_tool_runner(tool_runner, task=task, sft_mode=sft_mode)
    _AGENT_SFT_WORKER_CONTEXT.clear()
    _AGENT_SFT_WORKER_CONTEXT.update(
        {
            "task": task,
            "split": split,
            "sft_mode": sft_mode,
            "rewrite_output_root": rewrite_output_root,
            "provider": provider,
            "model": model,
            "prompt_root": prompt_root,
            "tool_runner": tool_runner,
        }
    )


def _build_agent_reasoning_sft_record_worker(
    sample_index: int,
    smiles: str,
    gt_label: int,
) -> dict[str, Any]:
    if not _AGENT_SFT_WORKER_CONTEXT:
        raise RuntimeError("Agent SFT worker context is not initialized")
    return build_agent_reasoning_sft_record(
        task=str(_AGENT_SFT_WORKER_CONTEXT["task"]),
        split=str(_AGENT_SFT_WORKER_CONTEXT["split"]),
        sft_mode=str(_AGENT_SFT_WORKER_CONTEXT["sft_mode"]),
        sample_index=int(sample_index),
        smiles=smiles,
        gt_label=int(gt_label),
        tool_runner=_AGENT_SFT_WORKER_CONTEXT["tool_runner"],
        rewrite_output_root=str(_AGENT_SFT_WORKER_CONTEXT["rewrite_output_root"]),
        provider=str(_AGENT_SFT_WORKER_CONTEXT["provider"]),
        model=str(_AGENT_SFT_WORKER_CONTEXT["model"]),
        prompt_root=str(_AGENT_SFT_WORKER_CONTEXT["prompt_root"]),
    )


def build_agent_reasoning_sft_record(
    *,
    task: str,
    split: str,
    sft_mode: str = SFT_MODE_FULL,
    sample_index: int,
    smiles: str,
    gt_label: int,
    tool_runner: Any,
    rewrite_output_root: str | Path = DEFAULT_REWRITE_OUTPUT_ROOT,
    provider: str = DEFAULT_REWRITE_PROVIDER,
    model: str = DEFAULT_REWRITE_MODEL,
    prompt_root: str | Path = DEFAULT_TASK_USER_PROMPT_ROOT,
) -> dict[str, Any]:
    validated_mode = _validate_sft_mode(sft_mode)
    reasoning_bundle = _load_reasoning_bundle(
        task=task,
        split=split,
        sample_index=sample_index,
        rewrite_output_root=rewrite_output_root,
        provider=provider,
        model=model,
        modes=_rewrite_modes_for_sft_mode(validated_mode),
    )
    user_message = render_task_user_message(task=task, smiles=smiles, prompt_root=prompt_root)
    final_answer_option = _resolve_final_answer_option(task, gt_label)

    messages: list[dict[str, Any]]
    if validated_mode == SFT_MODE_GLOBAL_ONLY:
        global_tool_text = _require_non_empty_text(
            tool_runner.get_mol_properties_and_fg(smiles),
            context=f"{GET_MOL_PROPERTIES_TOOL_NAME} for {task} sample {sample_index}",
        )
        messages = [
            {
                "role": "user",
                "content": user_message,
            },
            {
                "role": "assistant",
                "thinking": build_global_tool_bridge(task),
                "content": "",
                "tool_calls": [
                    _tool_call(
                        call_id=GET_MOL_PROPERTIES_CALL_ID,
                        name=GET_MOL_PROPERTIES_TOOL_NAME,
                        smiles=smiles,
                    )
                ],
            },
            {
                "role": "tool",
                "tool_call_id": GET_MOL_PROPERTIES_CALL_ID,
                "name": GET_MOL_PROPERTIES_TOOL_NAME,
                "content": global_tool_text,
            },
            {
                "role": "assistant",
                "thinking": reasoning_bundle["global_reasoning"],
                "content": f"Answer: ({final_answer_option})",
            },
        ]
    elif validated_mode == SFT_MODE_LOCAL_ONLY:
        local_tool_text = _require_non_empty_text(
            tool_runner.compare_similar_mols(smiles),
            context=f"{COMPARE_SIMILAR_MOLS_TOOL_NAME} for {task} sample {sample_index}",
        )
        messages = [
            {
                "role": "user",
                "content": user_message,
            },
            {
                "role": "assistant",
                "thinking": build_local_only_tool_bridge(task),
                "content": "",
                "tool_calls": [
                    _tool_call(
                        call_id=COMPARE_SIMILAR_MOLS_CALL_ID,
                        name=COMPARE_SIMILAR_MOLS_TOOL_NAME,
                        smiles=smiles,
                    )
                ],
            },
            {
                "role": "tool",
                "tool_call_id": COMPARE_SIMILAR_MOLS_CALL_ID,
                "name": COMPARE_SIMILAR_MOLS_TOOL_NAME,
                "content": local_tool_text,
            },
            {
                "role": "assistant",
                "thinking": reasoning_bundle["local_reasoning"],
                "content": f"Answer: ({final_answer_option})",
            },
        ]
    else:
        global_tool_text = _require_non_empty_text(
            tool_runner.get_mol_properties_and_fg(smiles),
            context=f"{GET_MOL_PROPERTIES_TOOL_NAME} for {task} sample {sample_index}",
        )
        local_tool_text = _require_non_empty_text(
            tool_runner.compare_similar_mols(smiles),
            context=f"{COMPARE_SIMILAR_MOLS_TOOL_NAME} for {task} sample {sample_index}",
        )
        messages = [
            {
                "role": "user",
                "content": user_message,
            },
            {
                "role": "assistant",
                "thinking": build_global_tool_bridge(task),
                "content": "",
                "tool_calls": [
                    _tool_call(
                        call_id=GET_MOL_PROPERTIES_CALL_ID,
                        name=GET_MOL_PROPERTIES_TOOL_NAME,
                        smiles=smiles,
                    )
                ],
            },
            {
                "role": "tool",
                "tool_call_id": GET_MOL_PROPERTIES_CALL_ID,
                "name": GET_MOL_PROPERTIES_TOOL_NAME,
                "content": global_tool_text,
            },
            {
                "role": "assistant",
                "thinking": f"{reasoning_bundle['global_reasoning']}\n\n{LOCAL_TOOL_BRIDGE}",
                "content": "",
                "tool_calls": [
                    _tool_call(
                        call_id=COMPARE_SIMILAR_MOLS_CALL_ID,
                        name=COMPARE_SIMILAR_MOLS_TOOL_NAME,
                        smiles=smiles,
                    )
                ],
            },
            {
                "role": "tool",
                "tool_call_id": COMPARE_SIMILAR_MOLS_CALL_ID,
                "name": COMPARE_SIMILAR_MOLS_TOOL_NAME,
                "content": local_tool_text,
            },
            {
                "role": "assistant",
                "thinking": f"{reasoning_bundle['local_reasoning']}\n\n{reasoning_bundle['hybrid_reasoning']}",
                "content": f"Answer: ({final_answer_option})",
            },
        ]

    return {
        "schema_version": AGENT_REASONING_SFT_SCHEMA_VERSION,
        "sft_mode": validated_mode,
        "task": task,
        "split": split,
        "sample_index": int(sample_index),
        "sample_id": reasoning_bundle["sample_id"] or f"{split}_sample_{int(sample_index)}",
        "smiles": smiles,
        "gt_label": int(gt_label),
        "final_answer_option": final_answer_option,
        "source_paths": reasoning_bundle["source_paths"],
        "messages": messages,
    }


def build_agent_reasoning_sft_for_task(
    *,
    task: str,
    split: str = "train",
    sft_mode: str = SFT_MODE_FULL,
    rewrite_output_root: str | Path = DEFAULT_REWRITE_OUTPUT_ROOT,
    rewrite_filter_root: str | Path = DEFAULT_REWRITE_FILTER_ROOT,
    provider: str = DEFAULT_REWRITE_PROVIDER,
    model: str = DEFAULT_REWRITE_MODEL,
    dataset_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT,
    output_root: str | Path = DEFAULT_AGENT_REASONING_SFT_OUTPUT_ROOT,
    prompt_root: str | Path = DEFAULT_TASK_USER_PROMPT_ROOT,
    feature_set_name: str = DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    manifest_root: str | Path = DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
    cache_root: str | Path = DEFAULT_TOOL_CACHE_ROOT,
    max_concurrency: int = 1,
    skip_existing: bool = True,
) -> dict[str, Any]:
    validated_mode = _validate_sft_mode(sft_mode)
    split_payload = load_tdc_split(task, split, data_root=dataset_root)
    rewritten_sample_indices = list_rewritten_sample_indices_for_sft_mode(
        task=task,
        split=split,
        sft_mode=validated_mode,
        rewrite_output_root=rewrite_output_root,
        rewrite_filter_root=rewrite_filter_root,
        provider=provider,
        model=model,
    )

    output_path = _dataset_output_dir(
        output_root=output_root,
        provider=provider,
        model=model,
        split=split,
        sft_mode=validated_mode,
    ) / f"{task}.jsonl"

    existing_records: list[dict[str, Any]] = []
    if skip_existing:
        existing_records = _load_existing_task_records(
            output_path=output_path,
            task=task,
            split=split,
            sft_mode=validated_mode,
            target_indices=rewritten_sample_indices,
        )

    completed_count = len(existing_records)
    pending_sample_indices = rewritten_sample_indices[completed_count:]

    records = list(existing_records)
    sample_iterator = tqdm(
        rewritten_sample_indices,
        desc=f"{task} ({split})",
        leave=False,
        initial=completed_count,
    )
    if pending_sample_indices:
        open_mode = "a" if completed_count > 0 else "w"
        with output_path.open(open_mode, encoding="utf-8") as handle:
            next_write_position = completed_count
            pending_buffer: dict[int, dict[str, Any]] = {}
            max_workers = max(1, int(max_concurrency))
            if max_workers == 1:
                tool_runner = build_task_tool_runner(
                    task=task,
                    feature_set_name=feature_set_name,
                    manifest_root=manifest_root,
                    dataset_root=dataset_root,
                    cache_root=cache_root,
                )
                _prewarm_tool_runner(tool_runner, task=task, sft_mode=validated_mode)
                for sample_index in pending_sample_indices:
                    sample_index = int(sample_index)
                    record = build_agent_reasoning_sft_record(
                        task=task,
                        split=split,
                        sft_mode=validated_mode,
                        sample_index=sample_index,
                        smiles=split_payload.smiles[sample_index],
                        gt_label=int(split_payload.labels[sample_index]),
                        tool_runner=tool_runner,
                        rewrite_output_root=rewrite_output_root,
                        provider=provider,
                        model=model,
                        prompt_root=prompt_root,
                    )
                    records.append(record)
                    _append_jsonl_record(handle, record)
                    next_write_position += 1
                    sample_iterator.update(1)
            else:
                with ProcessPoolExecutor(
                    max_workers=max_workers,
                    initializer=_init_agent_sft_worker,
                    initargs=(
                        task,
                        split,
                        validated_mode,
                        str(rewrite_output_root),
                        provider,
                        model,
                        str(prompt_root),
                        feature_set_name,
                        str(manifest_root),
                        str(dataset_root),
                        str(cache_root),
                    ),
                ) as executor:
                    in_flight: dict[Future[dict[str, Any]], int] = {}
                    submit_index = 0

                    while submit_index < len(pending_sample_indices) and len(in_flight) < max_workers:
                        sample_index = int(pending_sample_indices[submit_index])
                        in_flight[
                            executor.submit(
                                _build_agent_reasoning_sft_record_worker,
                                sample_index,
                                split_payload.smiles[sample_index],
                                int(split_payload.labels[sample_index]),
                            )
                        ] = sample_index
                        submit_index += 1

                    while in_flight:
                        done, _ = wait(in_flight.keys(), return_when=FIRST_COMPLETED)
                        for future in done:
                            sample_index = in_flight.pop(future)
                            record = future.result()
                            pending_buffer[int(sample_index)] = record

                        while next_write_position < len(rewritten_sample_indices):
                            expected_sample_index = int(rewritten_sample_indices[next_write_position])
                            record = pending_buffer.get(expected_sample_index)
                            if record is None:
                                break
                            records.append(record)
                            _append_jsonl_record(handle, record)
                            pending_buffer.pop(expected_sample_index, None)
                            next_write_position += 1
                            sample_iterator.update(1)

                        while submit_index < len(pending_sample_indices) and len(in_flight) < max_workers:
                            sample_index = int(pending_sample_indices[submit_index])
                            in_flight[
                                executor.submit(
                                    _build_agent_reasoning_sft_record_worker,
                                    sample_index,
                                    split_payload.smiles[sample_index],
                                    int(split_payload.labels[sample_index]),
                                )
                            ] = sample_index
                            submit_index += 1

    sample_iterator.close()

    return {
        "task": task,
        "split": split,
        "sft_mode": validated_mode,
        "num_records": len(records),
        "output_path": str(output_path.resolve()),
    }


def build_agent_reasoning_sft_datasets(
    *,
    tasks: list[str] | None = None,
    split: str = "train",
    sft_mode: str = SFT_MODE_FULL,
    manifest_index_path: str | Path = DEFAULT_TASK_MANIFEST_INDEX,
    rewrite_output_root: str | Path = DEFAULT_REWRITE_OUTPUT_ROOT,
    rewrite_filter_root: str | Path = DEFAULT_REWRITE_FILTER_ROOT,
    provider: str = DEFAULT_REWRITE_PROVIDER,
    model: str = DEFAULT_REWRITE_MODEL,
    dataset_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT,
    output_root: str | Path = DEFAULT_AGENT_REASONING_SFT_OUTPUT_ROOT,
    prompt_root: str | Path = DEFAULT_TASK_USER_PROMPT_ROOT,
    feature_set_name: str = DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    manifest_root: str | Path = DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
    cache_root: str | Path = DEFAULT_TOOL_CACHE_ROOT,
    max_concurrency: int = 1,
    skip_existing: bool = True,
) -> dict[str, Any]:
    validated_mode = _validate_sft_mode(sft_mode)
    task_list = tasks or load_task_names_from_manifest_index(manifest_index_path)
    summaries: list[dict[str, Any]] = []
    total_records = 0

    task_iterator = tqdm(task_list, desc=f"Agent SFT {validated_mode} ({split})")
    for task in task_iterator:
        summary = build_agent_reasoning_sft_for_task(
            task=task,
            split=split,
            sft_mode=validated_mode,
            rewrite_output_root=rewrite_output_root,
            rewrite_filter_root=rewrite_filter_root,
            provider=provider,
            model=model,
            dataset_root=dataset_root,
            output_root=output_root,
            prompt_root=prompt_root,
            feature_set_name=feature_set_name,
            manifest_root=manifest_root,
            cache_root=cache_root,
            max_concurrency=max_concurrency,
            skip_existing=skip_existing,
        )
        summaries.append(summary)
        total_records += int(summary["num_records"])

    payload = {
        "schema_version": AGENT_REASONING_SFT_SCHEMA_VERSION,
        "sft_mode": validated_mode,
        "provider": provider,
        "model": model,
        "split": split,
        "max_concurrency": int(max_concurrency),
        "skip_existing": bool(skip_existing),
        "num_tasks": len(summaries),
        "num_records": total_records,
        "tasks": summaries,
    }
    summary_path = _dataset_output_dir(
        output_root=output_root,
        provider=provider,
        model=model,
        split=split,
        sft_mode=validated_mode,
    ) / "manifest.json"
    summary_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    payload["summary_path"] = str(summary_path.resolve())
    return payload
