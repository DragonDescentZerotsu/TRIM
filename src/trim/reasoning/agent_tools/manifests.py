from __future__ import annotations

from pathlib import Path

from trim.reasoning.evidence.global_evidence import _default_label_semantics
from trim.reasoning.evidence.local_evidence import _resolve_raw_feature_columns
from trim.reasoning.semantics import build_feature_semantics_map, load_task_label_semantics
from trim.utils.io import load_json, load_pickle, save_json
from trim.utils.paths import (
    DEFAULT_PROCESSED_DATA_ROOT,
    DEFAULT_SIMILARITY_CACHE_ROOT,
    OUTPUTS_ROOT,
    PROJECT_ROOT,
    resolve_project_path,
    serialize_project_path,
)


AGENT_TOOL_SCHEMA_VERSION = "trim_agent_tools_v1_simple"
DEFAULT_AGENT_TOOL_MANIFEST_ROOT = OUTPUTS_ROOT / "reasoning_agent_tools" / "manifests"
DEFAULT_AGENT_TOOL_FEATURE_SET_NAME = "fg_top_level+rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts"
DEFAULT_GLOBAL_TOP_K = 10
DEFAULT_LOCAL_TOP_TERM_K = 8
DEFAULT_LOCAL_TOP_K_POS = 3
DEFAULT_LOCAL_TOP_K_NEG = 3


def _serialize_project_path(path_like: str | Path) -> str:
    return serialize_project_path(path_like)


def _resolve_saved_project_path(path_like: str | Path) -> str:
    return str(resolve_project_path(path_like))


def _resolve_manifest_payload_paths(payload: dict[str, object]) -> dict[str, object]:
    normalized = dict(payload)

    bundle_paths = normalized.get("bundle_paths")
    if isinstance(bundle_paths, dict):
        normalized["bundle_paths"] = {
            str(name): _resolve_saved_project_path(path_like)
            for name, path_like in bundle_paths.items()
        }

    return normalized


def _task_label_semantics(task: str) -> dict[int, dict[str, str]]:
    payload = _default_label_semantics()
    loaded = load_task_label_semantics(task)
    if loaded is not None:
        payload.update(loaded)
    return payload


def _is_functional_group_feature(semantics: dict[str, str]) -> bool:
    return str(semantics.get("source_family", "")) == "fg_top_level"


def _dense_feature_entries(feature_names: list[str]) -> list[dict[str, object]]:
    semantics_map = build_feature_semantics_map(feature_names)
    dense_entries: list[dict[str, object]] = []
    for index, feature_name in enumerate(feature_names, start=1):
        semantics = semantics_map[feature_name]
        if _is_functional_group_feature(semantics):
            continue
        dense_entries.append(
            {
                **semantics,
                "feature_name": feature_name,
                "feature_rank": int(index),
            }
        )
    return dense_entries


def _preferred_paths(paths: list[Path], preferred_fragments: tuple[str, ...]) -> list[Path]:
    def _fragment_rank(path: Path) -> int:
        rendered = str(path)
        for index, fragment in enumerate(preferred_fragments):
            if fragment in rendered:
                return index
        return len(preferred_fragments)

    return sorted(
        paths,
        key=lambda path: (
            _fragment_rank(path),
            len(path.parts),
            str(path),
        ),
    )


def discover_task_bundle_paths(
    *,
    task: str,
    feature_set_name: str = DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    outputs_root: str | Path = OUTPUTS_ROOT,
) -> dict[str, str]:
    outputs_root = Path(outputs_root)
    global_candidates = list(
        (outputs_root / "models" / "global_ebm").glob(f"*/{task}/{feature_set_name}/model_bundle.pkl")
    )
    if not global_candidates:
        raise FileNotFoundError(f"Could not find a global bundle for task={task!r}, feature_set={feature_set_name!r}")
    global_bundle_path = _preferred_paths(
        global_candidates,
        preferred_fragments=("keep_nan", "all_tasks_njobs16_parallel"),
    )[0]

    pos_candidates = list(
        (outputs_root / "models" / "pair_ebm").glob(f"*/{task}/{feature_set_name}/pos_model_bundle.pkl")
    )
    neg_candidates = list(
        (outputs_root / "models" / "pair_ebm").glob(f"*/{task}/{feature_set_name}/neg_model_bundle.pkl")
    )
    if not pos_candidates or not neg_candidates:
        raise FileNotFoundError(f"Could not find both pair bundles for task={task!r}, feature_set={feature_set_name!r}")

    pos_bundle_path = _preferred_paths(
        pos_candidates,
        preferred_fragments=("fg_plus_rdkit", "parallel15_njobs16", "njobs64"),
    )[0]
    neg_bundle_path = _preferred_paths(
        neg_candidates,
        preferred_fragments=("fg_plus_rdkit", "parallel15_njobs16", "njobs64"),
    )[0]

    return {
        "global_bundle_path": _serialize_project_path(global_bundle_path),
        "pos_bundle_path": _serialize_project_path(pos_bundle_path),
        "neg_bundle_path": _serialize_project_path(neg_bundle_path),
    }


def get_task_tool_manifest_path(
    *,
    task: str,
    feature_set_name: str = DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    manifest_root: str | Path = DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
) -> Path:
    return Path(manifest_root) / feature_set_name / f"{task}.json"


def load_task_tool_manifest(
    *,
    task: str,
    feature_set_name: str = DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    manifest_root: str | Path = DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
) -> dict[str, object]:
    manifest_path = resolve_project_path(
        get_task_tool_manifest_path(
            task=task,
            feature_set_name=feature_set_name,
            manifest_root=manifest_root,
        )
    )
    return _resolve_manifest_payload_paths(load_json(manifest_path))


def build_task_tool_manifest(
    *,
    task: str,
    feature_set_name: str = DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    dataset_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT,
    cache_root: str | Path = DEFAULT_SIMILARITY_CACHE_ROOT,
    global_top_k: int = DEFAULT_GLOBAL_TOP_K,
    local_top_term_k: int = DEFAULT_LOCAL_TOP_TERM_K,
    local_top_k_pos: int = DEFAULT_LOCAL_TOP_K_POS,
    local_top_k_neg: int = DEFAULT_LOCAL_TOP_K_NEG,
    strict_cross_scaffold_pairs: bool = True,
    outputs_root: str | Path = OUTPUTS_ROOT,
    manifest_root: str | Path = DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
    save: bool = True,
) -> dict[str, object]:
    bundle_paths = discover_task_bundle_paths(
        task=task,
        feature_set_name=feature_set_name,
        outputs_root=outputs_root,
    )
    resolved_bundle_paths = {
        key: _resolve_saved_project_path(path_like)
        for key, path_like in bundle_paths.items()
    }
    global_bundle = load_pickle(resolved_bundle_paths["global_bundle_path"])
    pos_bundle = load_pickle(resolved_bundle_paths["pos_bundle_path"])
    neg_bundle = load_pickle(resolved_bundle_paths["neg_bundle_path"])

    global_feature_columns = [str(column) for column in global_bundle["feature_columns"]]
    pos_raw_feature_columns = _resolve_raw_feature_columns(pos_bundle)
    neg_raw_feature_columns = _resolve_raw_feature_columns(neg_bundle)
    if pos_raw_feature_columns != neg_raw_feature_columns:
        raise ValueError("Positive and negative pair bundles must share the same raw feature columns")

    global_dense_features = _dense_feature_entries(global_feature_columns)
    local_dense_features = _dense_feature_entries(pos_raw_feature_columns)
    global_dense_feature_names = [str(item["feature_name"]) for item in global_dense_features]
    local_dense_feature_names = [str(item["feature_name"]) for item in local_dense_features]

    manifest = {
        "schema_version": AGENT_TOOL_SCHEMA_VERSION,
        "task": task,
        "feature_set_name": feature_set_name,
        "dataset_root": _serialize_project_path(dataset_root),
        "cache_root": _serialize_project_path(cache_root),
        "bundle_paths": bundle_paths,
        "label_semantics": _task_label_semantics(task),
        "global_tool": {
            "tool_name": "get_mol_properties_and_fg",
            "feature_mode": "full_dense_properties_plus_sparse_functional_groups",
            "top_k_per_sample": int(global_top_k),
            "dense_feature_count": int(len(global_dense_feature_names)),
            "dense_feature_names": global_dense_feature_names,
            "dense_features": global_dense_features,
        },
        "local_tool": {
            "tool_name": "compare_similar_mols",
            "feature_mode": "full_dense_pair_features_plus_sparse_functional_group_differences",
            "top_k_pos": int(local_top_k_pos),
            "top_k_neg": int(local_top_k_neg),
            "top_term_k_per_neighbor": int(local_top_term_k),
            "strict_cross_scaffold_pairs": bool(strict_cross_scaffold_pairs),
            "dense_feature_count": int(len(local_dense_feature_names)),
            "dense_feature_names": local_dense_feature_names,
            "dense_features": local_dense_features,
        },
    }

    if save:
        save_json(
            get_task_tool_manifest_path(
                task=task,
                feature_set_name=feature_set_name,
                manifest_root=manifest_root,
            ),
            manifest,
        )
    return manifest


def build_all_task_tool_manifests(
    *,
    tasks: list[str] | None = None,
    feature_set_name: str = DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    dataset_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT,
    cache_root: str | Path = DEFAULT_SIMILARITY_CACHE_ROOT,
    global_top_k: int = DEFAULT_GLOBAL_TOP_K,
    local_top_term_k: int = DEFAULT_LOCAL_TOP_TERM_K,
    local_top_k_pos: int = DEFAULT_LOCAL_TOP_K_POS,
    local_top_k_neg: int = DEFAULT_LOCAL_TOP_K_NEG,
    strict_cross_scaffold_pairs: bool = True,
    outputs_root: str | Path = OUTPUTS_ROOT,
    manifest_root: str | Path = DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
) -> dict[str, object]:
    if tasks is None:
        global_candidates = sorted(
            (Path(outputs_root) / "models" / "global_ebm").glob(f"*/*/{feature_set_name}/model_bundle.pkl")
        )
        tasks = sorted({path.parent.parent.name for path in global_candidates})

    task_entries: list[dict[str, object]] = []
    for task in tasks:
        manifest = build_task_tool_manifest(
            task=task,
            feature_set_name=feature_set_name,
            dataset_root=dataset_root,
            cache_root=cache_root,
            global_top_k=global_top_k,
            local_top_term_k=local_top_term_k,
            local_top_k_pos=local_top_k_pos,
            local_top_k_neg=local_top_k_neg,
            strict_cross_scaffold_pairs=strict_cross_scaffold_pairs,
            outputs_root=outputs_root,
            manifest_root=manifest_root,
            save=True,
        )
        task_entries.append(
            {
                "task": task,
                "manifest_path": _serialize_project_path(
                    get_task_tool_manifest_path(
                        task=task,
                        feature_set_name=feature_set_name,
                        manifest_root=manifest_root,
                    )
                ),
                "global_dense_feature_count": int(manifest["global_tool"]["dense_feature_count"]),
                "local_dense_feature_count": int(manifest["local_tool"]["dense_feature_count"]),
            }
        )

    summary = {
        "schema_version": AGENT_TOOL_SCHEMA_VERSION,
        "feature_set_name": feature_set_name,
        "num_tasks": int(len(task_entries)),
        "tasks": task_entries,
    }
    save_json(Path(manifest_root) / feature_set_name / "manifest_index.json", summary)
    return summary
