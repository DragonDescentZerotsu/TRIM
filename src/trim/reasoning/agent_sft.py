from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trim.data.datasets import load_tdc_split
from trim.reasoning.rewrite.pipeline import extract_reasoning_text_for_mode, load_mode_output_json, model_slug
from trim.reasoning.semantics.task_semantics import load_task_label_semantics
from trim.reasoning.task_user_prompts import (
    DEFAULT_TASK_MANIFEST_INDEX,
    DEFAULT_TASK_USER_PROMPT_ROOT,
    load_task_names_from_manifest_index,
    render_task_user_message,
)
from trim.utils.io import ensure_directory
from trim.utils.paths import DATA_ROOT, DEFAULT_PROCESSED_DATA_ROOT, OUTPUTS_ROOT, resolve_project_path


AGENT_REASONING_SFT_SCHEMA_VERSION = "trim_agent_reasoning_sft_messages_v1"
DEFAULT_AGENT_REASONING_SFT_OUTPUT_ROOT = DATA_ROOT / "sft" / "agent_reasoning_messages"
DEFAULT_REWRITE_OUTPUT_ROOT = OUTPUTS_ROOT / "reasoning_rewrite_outputs"
DEFAULT_REWRITE_PROVIDER = "openrouter"
DEFAULT_REWRITE_MODEL = "openai/gpt-5.4-mini"
DEFAULT_AGENT_TOOL_FEATURE_SET_NAME = "fg_top_level+rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts"
DEFAULT_AGENT_TOOL_MANIFEST_ROOT = OUTPUTS_ROOT / "reasoning_agent_tools" / "manifests"
DEFAULT_TOOL_CACHE_ROOT = "data/cache/tdc_mol_fingerprints"

GET_MOL_PROPERTIES_TOOL_NAME = "get_mol_properties_and_fg"
COMPARE_SIMILAR_MOLS_TOOL_NAME = "compare_similar_mols"
GET_MOL_PROPERTIES_CALL_ID = "call_get_mol_properties_and_fg"
COMPARE_SIMILAR_MOLS_CALL_ID = "call_compare_similar_mols"

GLOBAL_TOOL_BRIDGE = (
    "Let me first inspect the molecule's intrinsic properties with get_mol_properties_and_fg."
)
LOCAL_TOOL_BRIDGE = (
    "Let me compare this molecule against similar labeled molecules with compare_similar_mols."
)


def _dataset_output_dir(
    *,
    output_root: str | Path,
    provider: str,
    model: str,
    split: str,
) -> Path:
    return ensure_directory(resolve_project_path(output_root) / provider / model_slug(model) / split)


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
) -> dict[str, Any]:
    bundles: dict[str, dict[str, Any]] = {}
    paths: dict[str, str] = {}

    for mode in ("global", "local", "hybrid"):
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

    sample_id = str(bundles["global"].get("sample_id", "") or "")
    for mode in ("local", "hybrid"):
        other_sample_id = str(bundles[mode].get("sample_id", "") or "")
        if sample_id != other_sample_id:
            raise ValueError(
                f"Rewrite payload sample_id mismatch for task={task} sample_index={sample_index}: "
                f"{sample_id!r} != {other_sample_id!r}"
            )

    return {
        "sample_id": sample_id,
        "source_paths": paths,
        "global_reasoning": _require_non_empty_text(
            extract_reasoning_text_for_mode(payload=bundles["global"], mode="global"),
            context=f"global reasoning for {task} sample {sample_index}",
        ),
        "local_reasoning": _require_non_empty_text(
            extract_reasoning_text_for_mode(payload=bundles["local"], mode="local"),
            context=f"local reasoning for {task} sample {sample_index}",
        ),
        "hybrid_reasoning": _require_non_empty_text(
            extract_reasoning_text_for_mode(payload=bundles["hybrid"], mode="hybrid"),
            context=f"hybrid reasoning for {task} sample {sample_index}",
        ),
    }


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


def build_agent_reasoning_sft_record(
    *,
    task: str,
    split: str,
    sample_index: int,
    smiles: str,
    gt_label: int,
    tool_runner: Any,
    rewrite_output_root: str | Path = DEFAULT_REWRITE_OUTPUT_ROOT,
    provider: str = DEFAULT_REWRITE_PROVIDER,
    model: str = DEFAULT_REWRITE_MODEL,
    prompt_root: str | Path = DEFAULT_TASK_USER_PROMPT_ROOT,
) -> dict[str, Any]:
    reasoning_bundle = _load_reasoning_bundle(
        task=task,
        split=split,
        sample_index=sample_index,
        rewrite_output_root=rewrite_output_root,
        provider=provider,
        model=model,
    )
    user_message = render_task_user_message(task=task, smiles=smiles, prompt_root=prompt_root)
    global_tool_text = _require_non_empty_text(
        tool_runner.get_mol_properties_and_fg(smiles),
        context=f"{GET_MOL_PROPERTIES_TOOL_NAME} for {task} sample {sample_index}",
    )
    local_tool_text = _require_non_empty_text(
        tool_runner.compare_similar_mols(smiles),
        context=f"{COMPARE_SIMILAR_MOLS_TOOL_NAME} for {task} sample {sample_index}",
    )

    final_answer_option = _resolve_final_answer_option(task, gt_label)
    messages = [
        {
            "role": "user",
            "content": user_message,
        },
        {
            "role": "assistant",
            "thinking": GLOBAL_TOOL_BRIDGE,
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
    rewrite_output_root: str | Path = DEFAULT_REWRITE_OUTPUT_ROOT,
    provider: str = DEFAULT_REWRITE_PROVIDER,
    model: str = DEFAULT_REWRITE_MODEL,
    dataset_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT,
    output_root: str | Path = DEFAULT_AGENT_REASONING_SFT_OUTPUT_ROOT,
    prompt_root: str | Path = DEFAULT_TASK_USER_PROMPT_ROOT,
    feature_set_name: str = DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    manifest_root: str | Path = DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
    cache_root: str | Path = DEFAULT_TOOL_CACHE_ROOT,
) -> dict[str, Any]:
    split_payload = load_tdc_split(task, split, data_root=dataset_root)
    rewritten_sample_indices = list_fully_rewritten_sample_indices(
        task=task,
        split=split,
        rewrite_output_root=rewrite_output_root,
        provider=provider,
        model=model,
    )
    tool_runner = build_task_tool_runner(
        task=task,
        feature_set_name=feature_set_name,
        manifest_root=manifest_root,
        dataset_root=dataset_root,
        cache_root=cache_root,
    )

    records: list[dict[str, Any]] = []
    for sample_index in rewritten_sample_indices:
        smiles = split_payload.smiles[sample_index]
        gt_label = int(split_payload.labels[sample_index])
        records.append(
            build_agent_reasoning_sft_record(
                task=task,
                split=split,
                sample_index=sample_index,
                smiles=smiles,
                gt_label=gt_label,
                tool_runner=tool_runner,
                rewrite_output_root=rewrite_output_root,
                provider=provider,
                model=model,
                prompt_root=prompt_root,
            )
        )

    output_path = _dataset_output_dir(
        output_root=output_root,
        provider=provider,
        model=model,
        split=split,
    ) / f"{task}.jsonl"
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    return {
        "task": task,
        "split": split,
        "num_records": len(records),
        "output_path": str(output_path.resolve()),
    }


def build_agent_reasoning_sft_datasets(
    *,
    tasks: list[str] | None = None,
    split: str = "train",
    manifest_index_path: str | Path = DEFAULT_TASK_MANIFEST_INDEX,
    rewrite_output_root: str | Path = DEFAULT_REWRITE_OUTPUT_ROOT,
    provider: str = DEFAULT_REWRITE_PROVIDER,
    model: str = DEFAULT_REWRITE_MODEL,
    dataset_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT,
    output_root: str | Path = DEFAULT_AGENT_REASONING_SFT_OUTPUT_ROOT,
    prompt_root: str | Path = DEFAULT_TASK_USER_PROMPT_ROOT,
    feature_set_name: str = DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    manifest_root: str | Path = DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
    cache_root: str | Path = DEFAULT_TOOL_CACHE_ROOT,
) -> dict[str, Any]:
    task_list = tasks or load_task_names_from_manifest_index(manifest_index_path)
    summaries: list[dict[str, Any]] = []
    total_records = 0

    for task in task_list:
        summary = build_agent_reasoning_sft_for_task(
            task=task,
            split=split,
            rewrite_output_root=rewrite_output_root,
            provider=provider,
            model=model,
            dataset_root=dataset_root,
            output_root=output_root,
            prompt_root=prompt_root,
            feature_set_name=feature_set_name,
            manifest_root=manifest_root,
            cache_root=cache_root,
        )
        summaries.append(summary)
        total_records += int(summary["num_records"])

    payload = {
        "schema_version": AGENT_REASONING_SFT_SCHEMA_VERSION,
        "provider": provider,
        "model": model,
        "split": split,
        "num_tasks": len(summaries),
        "num_records": total_records,
        "tasks": summaries,
    }
    summary_path = _dataset_output_dir(
        output_root=output_root,
        provider=provider,
        model=model,
        split=split,
    ) / "manifest.json"
    summary_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    payload["summary_path"] = str(summary_path.resolve())
    return payload
