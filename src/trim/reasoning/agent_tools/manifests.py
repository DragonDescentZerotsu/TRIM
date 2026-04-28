from __future__ import annotations

from pathlib import Path

from trim.data.datasets import load_tdc_split
from trim.features.table_loader import build_feature_source_bundle
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
DEFAULT_AGENT_TOOL_FEATURE_CONFIG_PATHS = [
    "configs/features/fg_top_level_plus_rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts.json"
]
DEFAULT_COMPARE_MODE = "retrieval_only"


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
    require_global_bundle: bool = False,
    require_pair_bundles: bool = False,
) -> dict[str, str]:
    outputs_root = Path(outputs_root)
    global_candidates = list(
        (outputs_root / "models" / "global_ebm").glob(f"*/{task}/{feature_set_name}/model_bundle.pkl")
    )
    bundle_paths: dict[str, str] = {}
    if not global_candidates and require_global_bundle:
        raise FileNotFoundError(f"Could not find a global bundle for task={task!r}, feature_set={feature_set_name!r}")
    if global_candidates:
        global_bundle_path = _preferred_paths(
            global_candidates,
            preferred_fragments=("keep_nan", "all_tasks_njobs16_parallel"),
        )[0]
        bundle_paths["global_bundle_path"] = _serialize_project_path(global_bundle_path)

    pos_candidates = list(
        (outputs_root / "models" / "pair_ebm").glob(f"*/{task}/{feature_set_name}/pos_model_bundle.pkl")
    )
    neg_candidates = list(
        (outputs_root / "models" / "pair_ebm").glob(f"*/{task}/{feature_set_name}/neg_model_bundle.pkl")
    )
    if (not pos_candidates or not neg_candidates) and require_pair_bundles:
        raise FileNotFoundError(f"Could not find both pair bundles for task={task!r}, feature_set={feature_set_name!r}")
    if not pos_candidates or not neg_candidates:
        return bundle_paths

    pos_bundle_path = _preferred_paths(
        pos_candidates,
        preferred_fragments=("fg_plus_rdkit", "parallel15_njobs16", "njobs64"),
    )[0]
    neg_bundle_path = _preferred_paths(
        neg_candidates,
        preferred_fragments=("fg_plus_rdkit", "parallel15_njobs16", "njobs64"),
    )[0]

    bundle_paths["pos_bundle_path"] = _serialize_project_path(pos_bundle_path)
    bundle_paths["neg_bundle_path"] = _serialize_project_path(neg_bundle_path)
    return bundle_paths


def _load_optional_bundle(bundle_paths: dict[str, str], key: str) -> dict[str, object] | None:
    path = bundle_paths.get(key)
    if not path:
        return None
    return load_pickle(_resolve_saved_project_path(path))


def _infer_feature_columns_from_configs(
    *,
    task: str,
    dataset_root: str | Path,
    feature_config_paths: list[str | Path],
) -> list[str]:
    task_split = load_tdc_split(task, "train", data_root=dataset_root)
    if not task_split.smiles:
        raise ValueError(f"Cannot infer feature columns for task={task!r}: empty train split")
    feature_bundle = build_feature_source_bundle(feature_config_paths)
    feature_df = feature_bundle["feature_source"].load([task_split.smiles[0]])
    return [str(column) for column in feature_df.columns]


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
    feature_config_paths: list[str | Path] | None = None,
    compare_mode: str = DEFAULT_COMPARE_MODE,
    global_top_k: int = DEFAULT_GLOBAL_TOP_K,
    local_top_term_k: int = DEFAULT_LOCAL_TOP_TERM_K,
    local_top_k_pos: int = DEFAULT_LOCAL_TOP_K_POS,
    local_top_k_neg: int = DEFAULT_LOCAL_TOP_K_NEG,
    strict_cross_scaffold_pairs: bool = True,
    outputs_root: str | Path = OUTPUTS_ROOT,
    manifest_root: str | Path = DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
    save: bool = True,
) -> dict[str, object]:
    if compare_mode not in {"retrieval_only", "pair_ebm"}:
        raise ValueError("compare_mode must be either 'retrieval_only' or 'pair_ebm'")
    if feature_config_paths is None:
        feature_config_paths = list(DEFAULT_AGENT_TOOL_FEATURE_CONFIG_PATHS)

    bundle_paths = discover_task_bundle_paths(
        task=task,
        feature_set_name=feature_set_name,
        outputs_root=outputs_root,
        require_pair_bundles=compare_mode == "pair_ebm",
    )
    global_bundle = _load_optional_bundle(bundle_paths, "global_bundle_path")
    pos_bundle = _load_optional_bundle(bundle_paths, "pos_bundle_path")
    neg_bundle = _load_optional_bundle(bundle_paths, "neg_bundle_path")

    if global_bundle is not None:
        global_feature_columns = [str(column) for column in global_bundle["feature_columns"]]
        feature_config_paths = list(global_bundle.get("feature_config_paths", feature_config_paths))
    else:
        global_feature_columns = _infer_feature_columns_from_configs(
            task=task,
            dataset_root=dataset_root,
            feature_config_paths=list(feature_config_paths),
        )

    if pos_bundle is not None and neg_bundle is not None:
        local_raw_feature_columns = _resolve_raw_feature_columns(pos_bundle)
        neg_raw_feature_columns = _resolve_raw_feature_columns(neg_bundle)
        if local_raw_feature_columns != neg_raw_feature_columns:
            raise ValueError("Positive and negative pair bundles must share the same raw feature columns")
    else:
        local_raw_feature_columns = list(global_feature_columns)

    global_dense_features = _dense_feature_entries(global_feature_columns)
    local_dense_features = _dense_feature_entries(local_raw_feature_columns)
    global_dense_feature_names = [str(item["feature_name"]) for item in global_dense_features]
    local_dense_feature_names = [str(item["feature_name"]) for item in local_dense_features]

    manifest = {
        "schema_version": AGENT_TOOL_SCHEMA_VERSION,
        "task": task,
        "feature_set_name": feature_set_name,
        "dataset_root": _serialize_project_path(dataset_root),
        "cache_root": _serialize_project_path(cache_root),
        "feature_config_paths": [_serialize_project_path(path) for path in feature_config_paths],
        "bundle_paths": bundle_paths,
        "label_semantics": _task_label_semantics(task),
        "global_tool": {
            "tool_name": "get_mol_properties_and_fg",
            "requires_model": bool(global_bundle is not None),
            "feature_mode": "full_dense_properties_plus_sparse_functional_groups",
            "top_k_per_sample": int(global_top_k),
            "dense_feature_count": int(len(global_dense_feature_names)),
            "dense_feature_names": global_dense_feature_names,
            "dense_features": global_dense_features,
        },
        "local_tool": {
            "tool_name": "compare_similar_mols",
            "compare_mode": compare_mode,
            "requires_pair_model": bool(compare_mode == "pair_ebm"),
            "feature_mode": "full_dense_pair_features_plus_sparse_functional_group_differences",
            "top_k_pos": int(local_top_k_pos),
            "top_k_neg": int(local_top_k_neg),
            "top_term_k_per_neighbor": int(local_top_term_k),
            "strict_cross_scaffold_pairs": bool(strict_cross_scaffold_pairs),
            "raw_feature_count": int(len(local_raw_feature_columns)),
            "raw_feature_names": local_raw_feature_columns,
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
    feature_config_paths: list[str | Path] | None = None,
    compare_mode: str = DEFAULT_COMPARE_MODE,
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
            feature_config_paths=feature_config_paths,
            compare_mode=compare_mode,
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
