from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, Future, ProcessPoolExecutor, wait
from pathlib import Path
from typing import Any

from trim.data.datasets import load_tdc_split
from trim.reasoning.agent_tools.tools import (
    DEFAULT_AGENT_TOOL_CACHE_ROOT,
    DEFAULT_NEIGHBORS_PER_LABEL,
    TaskReasoningAgentTools,
    _normalize_neighbors_per_label,
)
from trim.reasoning.agent_tools.manifests import (
    DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
)
from trim.reasoning.task_user_prompts import DEFAULT_TASK_MANIFEST_INDEX, load_task_names_from_manifest_index
from trim.utils.io import save_json
from trim.utils.paths import DEFAULT_PROCESSED_DATA_ROOT, DEFAULT_SIMILARITY_CACHE_ROOT, OUTPUTS_ROOT, resolve_project_path

try:
    from tqdm.auto import tqdm
except Exception:  # pragma: no cover - tqdm is optional in some environments
    def tqdm(iterable=None, **kwargs):
        return iterable


AGENT_TOOL_PREWARM_SCHEMA_VERSION = "trim_agent_tool_cache_prewarm_v1"
DEFAULT_AGENT_TOOL_PREWARM_SUMMARY_ROOT = OUTPUTS_ROOT / "reasoning_agent_tools" / "tool_cache_prewarm"
DEFAULT_PREWARM_SPLITS = ("train", "valid", "test")
SUPPORTED_AGENT_TOOL_NAMES = (
    "get_mol_properties_and_fg",
    "compare_similar_mols",
)

_PREWARM_WORKER_CONTEXT: dict[str, Any] = {}


def _normalize_tool_names(tool_names: list[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    resolved = tuple(tool_names or SUPPORTED_AGENT_TOOL_NAMES)
    invalid = sorted(set(resolved) - set(SUPPORTED_AGENT_TOOL_NAMES))
    if invalid:
        raise ValueError(f"Unsupported tool names: {invalid!r}")
    if not resolved:
        raise ValueError("At least one tool name must be selected for prewarming")
    return resolved


def _normalize_neighbors_per_label_values(values: list[int] | tuple[int, ...] | None) -> tuple[int, ...]:
    if values is None:
        return (DEFAULT_NEIGHBORS_PER_LABEL,)
    resolved = tuple(dict.fromkeys(_normalize_neighbors_per_label(value) for value in values))
    if not resolved:
        raise ValueError("At least one neighbors_per_label value must be selected")
    return resolved


def _normalize_splits(splits: list[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    resolved = tuple(splits or DEFAULT_PREWARM_SPLITS)
    invalid = [split for split in resolved if split not in {"train", "valid", "test"}]
    if invalid:
        raise ValueError(f"Unsupported split names: {invalid!r}")
    if not resolved:
        raise ValueError("At least one split must be selected for prewarming")
    return resolved


def build_task_tool_runner(
    *,
    task: str,
    feature_set_name: str = DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    manifest_root: str | Path = DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
    dataset_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT,
    cache_root: str | Path = DEFAULT_SIMILARITY_CACHE_ROOT,
    tool_cache_root: str | Path = DEFAULT_AGENT_TOOL_CACHE_ROOT,
) -> TaskReasoningAgentTools:
    return TaskReasoningAgentTools.from_task(
        task=task,
        feature_set_name=feature_set_name,
        manifest_root=manifest_root,
        dataset_root=dataset_root,
        cache_root=cache_root,
        tool_cache_root=tool_cache_root,
        enable_tool_cache=True,
    )


def _prewarm_tool_runner(
    tool_runner: TaskReasoningAgentTools,
    *,
    task: str,
    query_splits: tuple[str, ...],
    selected_tools: tuple[str, ...],
) -> None:
    get_smiles_index = getattr(tool_runner, "_get_smiles_index", None)
    if callable(get_smiles_index):
        get_smiles_index()

    if "compare_similar_mols" not in selected_tools:
        return

    get_train_feature_cache = getattr(tool_runner, "_get_train_feature_cache", None)
    if callable(get_train_feature_cache):
        get_train_feature_cache()

    retriever = getattr(tool_runner, "retriever", None)
    if retriever is None:
        return

    load_train_metadata = getattr(retriever, "_load_train_metadata", None)
    if callable(load_train_metadata):
        load_train_metadata(task)

    load_similarity_file = getattr(retriever, "_load_similarity_file", None)
    if callable(load_similarity_file):
        for family in ("Morgan_similarity", "Feature_Morgan_similarity"):
            for split in query_splits:
                load_similarity_file(task, family, split)


def _collect_task_smiles(
    *,
    task: str,
    splits: tuple[str, ...],
    dataset_root: str | Path,
    max_smiles: int | None = None,
) -> tuple[list[str], dict[str, int]]:
    seen: set[str] = set()
    ordered_smiles: list[str] = []
    split_row_counts: dict[str, int] = {}

    for split in splits:
        split_payload = load_tdc_split(task, split, data_root=dataset_root)
        split_row_counts[split] = len(split_payload.smiles)
        for smiles in split_payload.smiles:
            if smiles in seen:
                continue
            seen.add(smiles)
            ordered_smiles.append(str(smiles))
            if max_smiles is not None and len(ordered_smiles) >= int(max_smiles):
                return ordered_smiles, split_row_counts

    return ordered_smiles, split_row_counts


def _prewarm_single_smiles(
    tool_runner: TaskReasoningAgentTools,
    *,
    smiles: str,
    selected_tools: tuple[str, ...],
    neighbors_per_label_values: tuple[int, ...],
    force_refresh: bool,
) -> dict[str, Any]:
    warmed_tools: list[str] = []
    skipped_tools: list[str] = []

    for tool_name in selected_tools:
        if tool_name == "get_mol_properties_and_fg":
            is_cached = tool_runner.has_cached_tool_payload(tool_name=tool_name, smiles=smiles)
            if is_cached and not force_refresh:
                skipped_tools.append(tool_name)
                continue
            tool_runner.get_mol_properties_and_fg_payload(smiles)
            warmed_tools.append(tool_name)
        elif tool_name == "compare_similar_mols":
            for neighbors_per_label in neighbors_per_label_values:
                tool_label = f"{tool_name}:neighbors_per_label={neighbors_per_label}"
                is_cached = tool_runner.has_cached_tool_payload(
                    tool_name=tool_name,
                    smiles=smiles,
                    neighbors_per_label=neighbors_per_label,
                )
                if is_cached and not force_refresh:
                    skipped_tools.append(tool_label)
                    continue
                tool_runner.compare_similar_mols_payload(smiles, neighbors_per_label=neighbors_per_label)
                warmed_tools.append(tool_label)
        else:  # pragma: no cover - guarded by _normalize_tool_names
            raise ValueError(f"Unsupported tool name: {tool_name!r}")

    return {
        "smiles": str(smiles),
        "warmed_tools": warmed_tools,
        "skipped_tools": skipped_tools,
    }


def _init_prewarm_worker(
    task: str,
    feature_set_name: str,
    manifest_root: str,
    dataset_root: str,
    cache_root: str,
    tool_cache_root: str,
    query_splits: tuple[str, ...],
    selected_tools: tuple[str, ...],
    neighbors_per_label_values: tuple[int, ...],
) -> None:
    tool_runner = build_task_tool_runner(
        task=task,
        feature_set_name=feature_set_name,
        manifest_root=manifest_root,
        dataset_root=dataset_root,
        cache_root=cache_root,
        tool_cache_root=tool_cache_root,
    )
    _prewarm_tool_runner(
        tool_runner,
        task=task,
        query_splits=query_splits,
        selected_tools=selected_tools,
    )
    _PREWARM_WORKER_CONTEXT.clear()
    _PREWARM_WORKER_CONTEXT.update(
        {
            "tool_runner": tool_runner,
            "selected_tools": selected_tools,
            "neighbors_per_label_values": neighbors_per_label_values,
        }
    )


def _prewarm_single_smiles_worker(smiles: str, force_refresh: bool) -> dict[str, Any]:
    if not _PREWARM_WORKER_CONTEXT:
        raise RuntimeError("Prewarm worker context is not initialized")
    return _prewarm_single_smiles(
        _PREWARM_WORKER_CONTEXT["tool_runner"],
        smiles=smiles,
        selected_tools=_PREWARM_WORKER_CONTEXT["selected_tools"],
        neighbors_per_label_values=_PREWARM_WORKER_CONTEXT["neighbors_per_label_values"],
        force_refresh=force_refresh,
    )


def _update_prewarm_counts(summary: dict[str, Any], tool_labels: list[str], *, prefix: str) -> None:
    for tool_label in tool_labels:
        tool_name = tool_label.split(":", 1)[0]
        summary[f"{prefix}_{tool_name}"] += 1
        if tool_label.startswith("compare_similar_mols:neighbors_per_label="):
            value = tool_label.rsplit("=", 1)[1]
            summary[f"{prefix}_compare_similar_mols_neighbors_per_label_{value}"] += 1


def prewarm_agent_tool_cache_for_task(
    *,
    task: str,
    splits: list[str] | tuple[str, ...] | None = None,
    feature_set_name: str = DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    manifest_root: str | Path = DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
    dataset_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT,
    cache_root: str | Path = DEFAULT_SIMILARITY_CACHE_ROOT,
    tool_cache_root: str | Path = DEFAULT_AGENT_TOOL_CACHE_ROOT,
    tool_names: list[str] | tuple[str, ...] | None = None,
    neighbors_per_label_values: list[int] | tuple[int, ...] | None = None,
    max_concurrency: int = 1,
    force_refresh: bool = False,
    max_smiles: int | None = None,
) -> dict[str, Any]:
    resolved_splits = _normalize_splits(splits)
    selected_tools = _normalize_tool_names(tool_names)
    resolved_neighbors_per_label_values = _normalize_neighbors_per_label_values(neighbors_per_label_values)
    smiles_list, split_row_counts = _collect_task_smiles(
        task=task,
        splits=resolved_splits,
        dataset_root=dataset_root,
        max_smiles=max_smiles,
    )

    summary = {
        "task": task,
        "splits": list(resolved_splits),
        "selected_tools": list(selected_tools),
        "num_split_rows_by_split": split_row_counts,
        "num_unique_smiles": int(len(smiles_list)),
        "force_refresh": bool(force_refresh),
        "max_smiles": None if max_smiles is None else int(max_smiles),
        "neighbors_per_label_values": list(resolved_neighbors_per_label_values),
    }
    for tool_name in selected_tools:
        summary[f"warmed_{tool_name}"] = 0
        summary[f"skipped_{tool_name}"] = 0
    if "compare_similar_mols" in selected_tools:
        for neighbors_per_label in resolved_neighbors_per_label_values:
            summary[f"warmed_compare_similar_mols_neighbors_per_label_{neighbors_per_label}"] = 0
            summary[f"skipped_compare_similar_mols_neighbors_per_label_{neighbors_per_label}"] = 0

    progress = tqdm(total=len(smiles_list), desc=f"{task} (tool cache)", leave=False)
    max_workers = max(1, int(max_concurrency))

    if max_workers == 1:
        tool_runner = build_task_tool_runner(
            task=task,
            feature_set_name=feature_set_name,
            manifest_root=manifest_root,
            dataset_root=dataset_root,
            cache_root=cache_root,
            tool_cache_root=tool_cache_root,
        )
        _prewarm_tool_runner(
            tool_runner,
            task=task,
            query_splits=resolved_splits,
            selected_tools=selected_tools,
        )
        for smiles in smiles_list:
            result = _prewarm_single_smiles(
                tool_runner,
                smiles=smiles,
                selected_tools=selected_tools,
                neighbors_per_label_values=resolved_neighbors_per_label_values,
                force_refresh=force_refresh,
            )
            _update_prewarm_counts(summary, result["warmed_tools"], prefix="warmed")
            _update_prewarm_counts(summary, result["skipped_tools"], prefix="skipped")
            progress.update(1)
    else:
        with ProcessPoolExecutor(
            max_workers=max_workers,
            initializer=_init_prewarm_worker,
            initargs=(
                task,
                feature_set_name,
                str(manifest_root),
                str(dataset_root),
                str(cache_root),
                str(tool_cache_root),
                resolved_splits,
                selected_tools,
                resolved_neighbors_per_label_values,
            ),
        ) as executor:
            in_flight: dict[Future[dict[str, Any]], str] = {}
            submit_index = 0

            while submit_index < len(smiles_list) and len(in_flight) < max_workers:
                smiles = smiles_list[submit_index]
                in_flight[executor.submit(_prewarm_single_smiles_worker, smiles, force_refresh)] = smiles
                submit_index += 1

            while in_flight:
                done, _ = wait(in_flight.keys(), return_when=FIRST_COMPLETED)
                for future in done:
                    _ = in_flight.pop(future)
                    result = future.result()
                    _update_prewarm_counts(summary, result["warmed_tools"], prefix="warmed")
                    _update_prewarm_counts(summary, result["skipped_tools"], prefix="skipped")
                    progress.update(1)

                while submit_index < len(smiles_list) and len(in_flight) < max_workers:
                    smiles = smiles_list[submit_index]
                    in_flight[executor.submit(_prewarm_single_smiles_worker, smiles, force_refresh)] = smiles
                    submit_index += 1

    progress.close()
    return summary


def prewarm_agent_tool_cache(
    *,
    tasks: list[str] | None = None,
    splits: list[str] | tuple[str, ...] | None = None,
    manifest_index_path: str | Path = DEFAULT_TASK_MANIFEST_INDEX,
    feature_set_name: str = DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    manifest_root: str | Path = DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
    dataset_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT,
    cache_root: str | Path = DEFAULT_SIMILARITY_CACHE_ROOT,
    tool_cache_root: str | Path = DEFAULT_AGENT_TOOL_CACHE_ROOT,
    tool_names: list[str] | tuple[str, ...] | None = None,
    neighbors_per_label_values: list[int] | tuple[int, ...] | None = None,
    max_concurrency: int = 1,
    force_refresh: bool = False,
    max_smiles_per_task: int | None = None,
    summary_path: str | Path | None = None,
) -> dict[str, Any]:
    resolved_splits = _normalize_splits(splits)
    selected_tools = _normalize_tool_names(tool_names)
    resolved_neighbors_per_label_values = _normalize_neighbors_per_label_values(neighbors_per_label_values)
    task_list = tasks or load_task_names_from_manifest_index(manifest_index_path)

    task_summaries: list[dict[str, Any]] = []
    total_unique_smiles = 0
    total_warmed_by_tool = {tool_name: 0 for tool_name in selected_tools}
    total_skipped_by_tool = {tool_name: 0 for tool_name in selected_tools}

    task_iterator = tqdm(task_list, desc="Prewarm agent tool cache")
    for task in task_iterator:
        task_summary = prewarm_agent_tool_cache_for_task(
            task=task,
            splits=resolved_splits,
            feature_set_name=feature_set_name,
            manifest_root=manifest_root,
            dataset_root=dataset_root,
            cache_root=cache_root,
            tool_cache_root=tool_cache_root,
            tool_names=selected_tools,
            neighbors_per_label_values=resolved_neighbors_per_label_values,
            max_concurrency=max_concurrency,
            force_refresh=force_refresh,
            max_smiles=max_smiles_per_task,
        )
        task_summaries.append(task_summary)
        total_unique_smiles += int(task_summary["num_unique_smiles"])
        for tool_name in selected_tools:
            total_warmed_by_tool[tool_name] += int(task_summary[f"warmed_{tool_name}"])
            total_skipped_by_tool[tool_name] += int(task_summary[f"skipped_{tool_name}"])

    task_iterator.close()

    payload: dict[str, Any] = {
        "schema_version": AGENT_TOOL_PREWARM_SCHEMA_VERSION,
        "feature_set_name": feature_set_name,
        "manifest_index_path": str(resolve_project_path(manifest_index_path)),
        "manifest_root": str(resolve_project_path(manifest_root)),
        "dataset_root": str(resolve_project_path(dataset_root)),
        "cache_root": str(resolve_project_path(cache_root)),
        "tool_cache_root": str(resolve_project_path(tool_cache_root)),
        "splits": list(resolved_splits),
        "selected_tools": list(selected_tools),
        "neighbors_per_label_values": list(resolved_neighbors_per_label_values),
        "max_concurrency": int(max_concurrency),
        "force_refresh": bool(force_refresh),
        "max_smiles_per_task": None if max_smiles_per_task is None else int(max_smiles_per_task),
        "num_tasks": len(task_summaries),
        "total_unique_smiles": int(total_unique_smiles),
        "tasks": task_summaries,
    }
    for tool_name in selected_tools:
        payload[f"total_warmed_{tool_name}"] = int(total_warmed_by_tool[tool_name])
        payload[f"total_skipped_{tool_name}"] = int(total_skipped_by_tool[tool_name])

    resolved_summary_path = resolve_project_path(
        summary_path
        or (
            DEFAULT_AGENT_TOOL_PREWARM_SUMMARY_ROOT
            / feature_set_name
            / "manifest.json"
        )
    )
    save_json(resolved_summary_path, payload)
    payload["summary_path"] = str(resolved_summary_path.resolve())
    return payload
