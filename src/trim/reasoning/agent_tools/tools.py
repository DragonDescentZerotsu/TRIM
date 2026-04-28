from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

from trim.data.datasets import load_tdc_split
from trim.features.pair_features import build_pair_matrix, coerce_numeric_feature_frame
from trim.features.preprocessing import transform_feature_frame
from trim.features.table_loader import build_feature_source_bundle
from trim.models.aggregation import aggregate_local_scores
from trim.models.retrieval import CachedSimilarityRetriever
from trim.reasoning.agent_tools.manifests import (
    DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    DEFAULT_AGENT_TOOL_FEATURE_CONFIG_PATHS,
    DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
    load_task_tool_manifest,
)
from trim.reasoning.evidence.global_evidence import (
    _infer_value_phrase,
    _label_payload,
    _missing_value_reason,
    _resolve_label_semantics,
    _sanitize_json_value,
)
from trim.reasoning.evidence.local_evidence import _delta_value_payload, _resolve_raw_feature_columns
from trim.reasoning.semantics import build_feature_semantics_map
from trim.utils.io import load_json, load_pickle, save_json
from trim.utils.paths import (
    DEFAULT_PROCESSED_DATA_ROOT,
    DEFAULT_SIMILARITY_CACHE_ROOT,
    OUTPUTS_ROOT,
    PROJECT_ROOT,
    resolve_project_path,
)


AGENT_TOOL_PAYLOAD_CACHE_SCHEMA_VERSION = "trim_agent_tool_payload_cache_v1"
AGENT_TOOL_CACHE_SIGNATURE_VERSION = "portable_v3"
LEGACY_COMPATIBLE_CACHE_SIGNATURE_VERSIONS = {"portable_v2"}
DEFAULT_AGENT_TOOL_CACHE_ROOT = OUTPUTS_ROOT / "reasoning_agent_tools" / "tool_cache"
DEFAULT_NEIGHBORS_PER_LABEL = 3
SUPPORTED_NEIGHBORS_PER_LABEL = (1, 2, 3)
DEFAULT_COMPARE_MODE = "retrieval_only"
TOOL_CACHE_CONTENT_DIGEST_MAX_BYTES = 64 * 1024 * 1024
TOOL_CACHE_CONTENT_DIGEST_CHUNK_BYTES = 1024 * 1024


def _normalize_neighbors_per_label(value: object = DEFAULT_NEIGHBORS_PER_LABEL) -> int:
    if value is None:
        return DEFAULT_NEIGHBORS_PER_LABEL
    if isinstance(value, bool):
        raise ValueError("neighbors_per_label must be one of 1, 2, or 3")
    try:
        normalized = int(value)
        numeric_value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("neighbors_per_label must be one of 1, 2, or 3") from exc
    if not math.isfinite(numeric_value) or numeric_value != float(normalized):
        raise ValueError("neighbors_per_label must be one of 1, 2, or 3")
    if normalized not in SUPPORTED_NEIGHBORS_PER_LABEL:
        raise ValueError("neighbors_per_label must be one of 1, 2, or 3")
    return normalized


def _normalize_compare_mode(value: object = DEFAULT_COMPARE_MODE) -> str:
    mode = str(value or DEFAULT_COMPARE_MODE)
    if mode not in {"retrieval_only", "pair_ebm"}:
        raise ValueError("compare_mode must be either 'retrieval_only' or 'pair_ebm'")
    return mode


def _safe_scalar(value: object) -> object:
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            return value
    return value


def _stable_json_value(value: object) -> object:
    value = _safe_scalar(value)
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {str(key): _stable_json_value(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [_stable_json_value(item) for item in value]
    if isinstance(value, set):
        return [_stable_json_value(item) for item in sorted(value, key=str)]
    if isinstance(value, np.ndarray):
        return _stable_json_value(value.tolist())
    if isinstance(value, float):
        if math.isnan(value):
            return None
        if math.isinf(value):
            return "Infinity" if value > 0 else "-Infinity"
        return value
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    return str(value)


def _sorted_rank_map(term_contributions: np.ndarray) -> dict[int, int]:
    ranked_indices = [
        index
        for index, value in sorted(
            enumerate(term_contributions),
            key=lambda item: abs(float(item[1])),
            reverse=True,
        )
        if not math.isnan(float(value))
    ]
    return {term_index: rank for rank, term_index in enumerate(ranked_indices, start=1)}


def _is_functional_group_feature(semantics: dict[str, str]) -> bool:
    return str(semantics.get("source_family", "")) == "fg_top_level"


def _is_int_like(value: object) -> bool:
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(numeric_value) and abs(numeric_value - round(numeric_value)) < 1e-9


def _format_plain_numeric(value: object, *, signed: bool = False) -> str:
    numeric_value = float(value)
    if _is_int_like(numeric_value):
        integer_value = int(round(numeric_value))
        return f"{integer_value:+d}" if signed else str(integer_value)
    rendered = f"{numeric_value:+.4f}" if signed else f"{numeric_value:.4f}"
    rendered = rendered.rstrip("0").rstrip(".")
    if rendered in {"-0", "+0"}:
        return "+0" if signed else "0"
    return rendered


def _missing_reason_text(reason: object) -> str:
    mapping = {
        "no_acidic_site": "not applicable (no acidic site)",
        "no_basic_site": "not applicable (no basic site)",
    }
    return mapping.get(str(reason), "not applicable")


def _format_tool_value(value: object, *, missing_reason: object = None) -> str:
    if missing_reason is not None:
        return _missing_reason_text(missing_reason)
    if value is None:
        return "not applicable"
    if isinstance(value, str):
        return value
    if _is_int_like(value):
        return str(int(round(float(value))))
    try:
        return _format_plain_numeric(value)
    except (TypeError, ValueError):
        return str(value)


def _format_tool_delta(value: object, *, missing_reason: object = None, fallback_text: str | None = None) -> str:
    if missing_reason is not None:
        if fallback_text:
            return fallback_text
        return _missing_reason_text(missing_reason)
    if value is None:
        return fallback_text or "not applicable"
    try:
        return _format_plain_numeric(value, signed=True)
    except (TypeError, ValueError):
        return fallback_text or str(value)


def _render_global_payload_text(payload: dict[str, object]) -> str:
    lines: list[str] = []
    for feature in payload["features"]:
        lines.append(
            f"{feature['display_name']}: "
            f"{_format_tool_value(feature.get('feature_value'), missing_reason=feature.get('feature_value_missing_reason'))}"
        )

    lines.append("")
    if payload["present_functional_groups"]:
        lines.append("functional groups:")
        for group in payload["present_functional_groups"]:
            lines.append(f"{group['display_name']}: {_format_tool_value(group.get('feature_value'))}")
    else:
        lines.append("functional groups: none")
    return "\n".join(lines)


def _render_neighbor_payload_text(neighbor: dict[str, object], *, index: int) -> str:
    label_text = neighbor["neighbor_label_semantics"]["text"]
    lines = [
        f"Neighbor {index}",
        f"label: {label_text}",
        f"similarity: {_format_plain_numeric(neighbor['neighbor_similarity'])}",
        f"smiles: {neighbor['neighbor_smiles']}",
        "properties:",
    ]
    for feature in neighbor["feature_comparisons"]:
        lines.append(
            f"{feature['display_name']}: "
            f"neighbor={_format_tool_value(feature.get('neighbor_value'), missing_reason=feature.get('neighbor_value_missing_reason'))} | "
            f"query={_format_tool_value(feature.get('query_value'), missing_reason=feature.get('query_value_missing_reason'))} | "
            f"delta={_format_tool_delta(feature.get('delta_value'), missing_reason=feature.get('delta_value_missing_reason'), fallback_text=feature.get('delta_value_text'))}"
        )

    if neighbor["functional_group_differences"]:
        lines.append("functional group differences:")
        for group in neighbor["functional_group_differences"]:
            lines.append(
                f"{group['display_name']}: "
                f"neighbor={_format_tool_value(group.get('neighbor_value'))} | "
                f"query={_format_tool_value(group.get('query_value'))} | "
                f"delta={_format_tool_delta(group.get('delta_value'))}"
            )
    else:
        lines.append("functional group differences: none")
    return "\n".join(lines)


def _render_local_payload_text(payload: dict[str, object]) -> str:
    lines: list[str] = [
        "Definitions: query is the target molecule being analyzed, neighbor is a retrieved training-set analog for this task, and delta means query value minus neighbor value.",
        "",
    ]
    lines.append("positive neighbors:")
    if payload["positive_neighbors"]:
        for index, neighbor in enumerate(payload["positive_neighbors"], start=1):
            if index > 1:
                lines.append("")
            lines.append(_render_neighbor_payload_text(neighbor, index=index))
    else:
        lines.append("none")

    lines.append("")
    lines.append("negative neighbors:")
    if payload["negative_neighbors"]:
        start_index = len(payload["positive_neighbors"]) + 1
        for index, neighbor in enumerate(payload["negative_neighbors"], start=start_index):
            if index > start_index:
                lines.append("")
            lines.append(_render_neighbor_payload_text(neighbor, index=index))
    else:
        lines.append("none")
    return "\n".join(lines)


def _canonicalize_smiles_for_tool_lookup(smiles: str) -> str | None:
    try:
        from rdkit import Chem
        from rdkit.Chem.MolStandardize import rdMolStandardize
    except Exception:
        return None

    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None:
        return None
    try:
        mol = rdMolStandardize.LargestFragmentChooser(preferOrganic=True).choose(mol)
    except Exception:
        pass
    try:
        return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)
    except Exception:
        return None


class TaskReasoningAgentTools:
    def __init__(
        self,
        *,
        task: str,
        manifest: dict[str, object],
        dataset_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT,
        cache_root: str | Path = DEFAULT_SIMILARITY_CACHE_ROOT,
        tool_cache_root: str | Path = DEFAULT_AGENT_TOOL_CACHE_ROOT,
        enable_tool_cache: bool = True,
    ):
        self.task = str(task)
        self.manifest = manifest
        self.dataset_root = Path(dataset_root)
        self.cache_root = Path(cache_root)
        self.feature_set_name = str(manifest.get("feature_set_name", DEFAULT_AGENT_TOOL_FEATURE_SET_NAME))
        self.tool_cache_root = resolve_project_path(tool_cache_root)
        self.enable_tool_cache = bool(enable_tool_cache)

        bundle_paths = {
            str(name): resolve_project_path(path)
            for name, path in dict(manifest.get("bundle_paths", {})).items()
        }
        local_tool_manifest = dict(manifest.get("local_tool", {}))
        self.compare_mode = _normalize_compare_mode(local_tool_manifest.get("compare_mode", DEFAULT_COMPARE_MODE))
        self.global_bundle = (
            load_pickle(bundle_paths["global_bundle_path"])
            if "global_bundle_path" in bundle_paths
            else None
        )
        self.pos_bundle = (
            load_pickle(bundle_paths["pos_bundle_path"])
            if self.compare_mode == "pair_ebm" and "pos_bundle_path" in bundle_paths
            else None
        )
        self.neg_bundle = (
            load_pickle(bundle_paths["neg_bundle_path"])
            if self.compare_mode == "pair_ebm" and "neg_bundle_path" in bundle_paths
            else None
        )
        if self.compare_mode == "pair_ebm" and (self.pos_bundle is None or self.neg_bundle is None):
            raise FileNotFoundError("compare_mode='pair_ebm' requires both pos_model_bundle.pkl and neg_model_bundle.pkl")

        feature_config_paths = list(manifest.get("feature_config_paths") or DEFAULT_AGENT_TOOL_FEATURE_CONFIG_PATHS)
        if isinstance(self.global_bundle, dict) and self.global_bundle.get("feature_config_paths"):
            feature_config_paths = list(self.global_bundle["feature_config_paths"])
        self.feature_bundle = build_feature_source_bundle(feature_config_paths)
        self.feature_source = self.feature_bundle["feature_source"]
        self.retriever = CachedSimilarityRetriever(cache_root=self.cache_root, data_root=self.dataset_root)
        self.label_semantics = _resolve_label_semantics(self.task)
        manifest_label_semantics = manifest.get("label_semantics")
        if isinstance(manifest_label_semantics, dict):
            for label_key, label_payload in manifest_label_semantics.items():
                if isinstance(label_payload, dict):
                    self.label_semantics[int(label_key)] = dict(label_payload)

        if isinstance(self.global_bundle, dict):
            self.global_feature_columns = [str(column) for column in self.global_bundle["feature_columns"]]
        else:
            self.global_feature_columns = [
                str(column)
                for column in (
                    local_tool_manifest.get("raw_feature_names")
                    or manifest.get("global_tool", {}).get("dense_feature_names", [])
                    or local_tool_manifest.get("dense_feature_names", [])
                )
            ]
        self.global_feature_index = {
            feature_name: index for index, feature_name in enumerate(self.global_feature_columns)
        }
        self.global_feature_semantics = build_feature_semantics_map(self.global_feature_columns)

        if isinstance(self.pos_bundle, dict):
            self.local_raw_feature_columns = _resolve_raw_feature_columns(self.pos_bundle)
        else:
            self.local_raw_feature_columns = [
                str(column)
                for column in (
                    local_tool_manifest.get("raw_feature_names")
                    or local_tool_manifest.get("dense_feature_names", [])
                )
            ]
        self.local_feature_index = {
            feature_name: index for index, feature_name in enumerate(self.local_raw_feature_columns)
        }
        self.local_feature_semantics = build_feature_semantics_map(self.local_raw_feature_columns)

        self._smiles_index: dict[str, list[dict[str, object]]] | None = None
        self._train_raw_df = None
        self._train_raw_values = None
        self._train_index_by_smiles: dict[str, int] | None = None
        self._tool_payload_cache: dict[tuple[str, str, str], dict[str, object]] = {}
        self._compatible_tool_cache_path_cache: dict[tuple[str, str, str], Path | None] = {}
        self._resolved_smiles_cache: dict[str, str] = {}
        self._tool_cache_namespace = self._build_tool_cache_namespace()

    @classmethod
    def from_task(
        cls,
        *,
        task: str,
        feature_set_name: str = DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
        manifest_root: str | Path = DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
        dataset_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT,
        cache_root: str | Path = DEFAULT_SIMILARITY_CACHE_ROOT,
        tool_cache_root: str | Path = DEFAULT_AGENT_TOOL_CACHE_ROOT,
        enable_tool_cache: bool = True,
    ) -> "TaskReasoningAgentTools":
        manifest = load_task_tool_manifest(
            task=task,
            feature_set_name=feature_set_name,
            manifest_root=manifest_root,
        )
        return cls(
            task=task,
            manifest=manifest,
            dataset_root=dataset_root,
            cache_root=cache_root,
            tool_cache_root=tool_cache_root,
            enable_tool_cache=enable_tool_cache,
        )

    def _portable_cache_path(self, path_like: str | Path, resolved_path: Path) -> str:
        path = Path(path_like)
        if not path.is_absolute():
            return path.as_posix()
        project_root = PROJECT_ROOT.resolve()
        try:
            return path.relative_to(project_root).as_posix()
        except ValueError:
            pass
        try:
            return resolved_path.resolve().relative_to(project_root).as_posix()
        except ValueError:
            return str(resolved_path.resolve())

    def _cache_file_identity(self, path_like: str | Path) -> dict[str, object]:
        path = Path(path_like)
        resolved_path = path if path.is_absolute() else resolve_project_path(path)
        return {"path": self._portable_cache_path(path, resolved_path)}

    def _content_digest(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(TOOL_CACHE_CONTENT_DIGEST_CHUNK_BYTES)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest()

    def _cache_file_signature(self, path_like: str | Path) -> dict[str, object]:
        path = Path(path_like)
        resolved_path = path if path.is_absolute() else resolve_project_path(path)
        signature: dict[str, object] = {"path": self._portable_cache_path(path, resolved_path)}
        if resolved_path.exists():
            stat = resolved_path.stat()
            signature["size"] = int(stat.st_size)
            if stat.st_size <= TOOL_CACHE_CONTENT_DIGEST_MAX_BYTES:
                signature["sha256"] = self._content_digest(resolved_path)
            else:
                signature["sha256"] = None
                signature["sha256_skipped_reason"] = "file_exceeds_digest_size_limit"
                signature["sha256_size_limit_bytes"] = int(TOOL_CACHE_CONTENT_DIGEST_MAX_BYTES)
        else:
            signature["missing"] = True
        return signature

    def _similarity_cache_signatures(self) -> dict[str, dict[str, object]]:
        signatures: dict[str, dict[str, object]] = {}
        for family in ("Morgan_similarity", "Feature_Morgan_similarity"):
            for split in ("train", "valid", "test"):
                relative_key = f"{family}/{split}"
                path = self.cache_root / family / "by_task" / self.task / f"{split}_similarity.pkl"
                signatures[relative_key] = self._cache_file_signature(path)
        return signatures

    def _similarity_cache_identities(self) -> dict[str, dict[str, object]]:
        identities: dict[str, dict[str, object]] = {}
        for family in ("Morgan_similarity", "Feature_Morgan_similarity"):
            for split in ("train", "valid", "test"):
                relative_key = f"{family}/{split}"
                path = self.cache_root / family / "by_task" / self.task / f"{split}_similarity.pkl"
                identities[relative_key] = self._cache_file_identity(path)
        return identities

    def _portable_path_values(self, path_values: object) -> object:
        if isinstance(path_values, (str, Path)):
            path = Path(path_values)
            resolved_path = path if path.is_absolute() else resolve_project_path(path)
            return self._portable_cache_path(path, resolved_path)
        if isinstance(path_values, (list, tuple)):
            return [self._portable_path_values(path_value) for path_value in path_values]
        return _stable_json_value(path_values)

    def _bundle_metadata_signature(self, bundle_name: str) -> dict[str, object]:
        bundle_by_name = {
            "global_bundle_path": getattr(self, "global_bundle", None),
            "pos_bundle_path": getattr(self, "pos_bundle", None),
            "neg_bundle_path": getattr(self, "neg_bundle", None),
        }
        bundle = bundle_by_name.get(bundle_name)
        if not isinstance(bundle, dict):
            return {}

        common_keys = (
            "task",
            "model_type",
            "neighbor_label",
            "feature_set_name",
            "feature_config_paths",
            "feature_columns",
            "raw_feature_columns",
            "pair_columns",
            "ebm_params",
            "pair_params",
            "training_config",
            "metrics",
        )
        metadata: dict[str, object] = {}
        for key in common_keys:
            if key not in bundle:
                continue
            if key == "feature_config_paths":
                metadata[key] = self._portable_path_values(bundle[key])
            else:
                metadata[key] = _stable_json_value(bundle[key])
        return metadata

    def _build_tool_cache_namespace_payload(self) -> dict[str, object]:
        bundle_paths = dict(self.manifest.get("bundle_paths", {}))
        return {
            "schema_version": AGENT_TOOL_PAYLOAD_CACHE_SCHEMA_VERSION,
            "cache_signature_version": AGENT_TOOL_CACHE_SIGNATURE_VERSION,
            "task": self.task,
            "feature_set_name": self.feature_set_name,
            "manifest": {
                "schema_version": self.manifest.get("schema_version"),
                "feature_config_paths": self._portable_path_values(
                    self.manifest.get("feature_config_paths", DEFAULT_AGENT_TOOL_FEATURE_CONFIG_PATHS)
                ),
                "global_tool": self.manifest.get("global_tool"),
                "local_tool": self.manifest.get("local_tool"),
            },
            "bundle_files": {
                name: {
                    **self._cache_file_identity(path_like),
                    "metadata": self._bundle_metadata_signature(name),
                }
                for name, path_like in bundle_paths.items()
            },
            "similarity_cache_files": self._similarity_cache_identities(),
        }

    def _build_tool_cache_diagnostic_payload(self) -> dict[str, object]:
        bundle_paths = dict(self.manifest.get("bundle_paths", {}))
        return {
            "schema_version": AGENT_TOOL_PAYLOAD_CACHE_SCHEMA_VERSION,
            "cache_signature_version": AGENT_TOOL_CACHE_SIGNATURE_VERSION,
            "task": self.task,
            "feature_set_name": self.feature_set_name,
            "namespace_payload": self._build_tool_cache_namespace_payload(),
            "bundle_file_diagnostics": {
                name: self._cache_file_signature(path_like)
                for name, path_like in bundle_paths.items()
            },
            "similarity_cache_file_diagnostics": self._similarity_cache_signatures(),
        }

    def _build_tool_cache_namespace(self) -> str:
        signature_payload = self._build_tool_cache_namespace_payload()
        serialized = json.dumps(signature_payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha1(serialized.encode("utf-8")).hexdigest()[:16]

    def _tool_cache_namespace_dir(self) -> Path:
        return self.tool_cache_root / self.feature_set_name / self.task / self._tool_cache_namespace

    def _store_tool_cache_signature_manifest(self) -> None:
        if not self.enable_tool_cache:
            return
        namespace_dir = self._tool_cache_namespace_dir()
        signature_path = namespace_dir / "cache_signature.json"
        if signature_path.exists():
            return
        save_json(
            signature_path,
            {
                "cache_namespace": self._tool_cache_namespace,
                "signature": self._build_tool_cache_diagnostic_payload(),
            },
        )

    def _tool_cache_variant(self, *, tool_name: str, neighbors_per_label: object = None) -> str | None:
        if tool_name != "compare_similar_mols":
            return None
        return f"neighbors_per_label_{_normalize_neighbors_per_label(neighbors_per_label)}"

    def _tool_cache_path(
        self,
        *,
        tool_name: str,
        smiles: str,
        cache_variant: str | None = None,
    ) -> Path:
        smiles_digest = self._smiles_cache_digest(smiles)
        tool_dir = (
            self._tool_cache_namespace_dir()
            / tool_name
        )
        if cache_variant:
            tool_dir = tool_dir / cache_variant
        return tool_dir / f"{smiles_digest}.json"

    def _smiles_cache_digest(self, smiles: str) -> str:
        return hashlib.sha1(str(smiles).encode("utf-8")).hexdigest()

    def has_cached_tool_payload(
        self,
        *,
        tool_name: str,
        smiles: str,
        neighbors_per_label: object = None,
    ) -> bool:
        return (
            self._find_compatible_cached_tool_payload_path(
                tool_name=tool_name,
                smiles=smiles,
                neighbors_per_label=neighbors_per_label,
            )
            is not None
        )

    def _read_cached_tool_payload(
        self,
        cache_path: Path,
        *,
        tool_name: str,
        smiles: str,
        neighbors_per_label: object = None,
    ) -> dict[str, object] | None:
        try:
            cached_record = load_json(cache_path)
        except Exception:
            return None
        if str(cached_record.get("tool_name")) != tool_name:
            return None
        if str(cached_record.get("task")) != self.task:
            return None
        if str(cached_record.get("feature_set_name")) != self.feature_set_name:
            return None
        if str(cached_record.get("smiles")) != str(smiles):
            return None

        record_signature_version = cached_record.get("cache_signature_version")
        record_namespace = cached_record.get("cache_namespace")
        if record_signature_version == AGENT_TOOL_CACHE_SIGNATURE_VERSION:
            if str(record_namespace) != self._tool_cache_namespace:
                return None
        elif record_signature_version in LEGACY_COMPATIBLE_CACHE_SIGNATURE_VERSIONS:
            pass
        elif record_signature_version is not None:
            return None

        payload = cached_record.get("payload")
        if not isinstance(payload, dict):
            return None

        if tool_name == "compare_similar_mols":
            expected_neighbors_per_label = _normalize_neighbors_per_label(neighbors_per_label)
            cached_neighbors_per_label = payload.get("neighbors_per_label")
            if cached_neighbors_per_label is None:
                cache_parameters = cached_record.get("cache_parameters")
                if isinstance(cache_parameters, dict):
                    cached_neighbors_per_label = cache_parameters.get("neighbors_per_label")
            if cached_neighbors_per_label is None:
                if expected_neighbors_per_label != DEFAULT_NEIGHBORS_PER_LABEL:
                    return None
            else:
                try:
                    cached_neighbors_per_label = _normalize_neighbors_per_label(cached_neighbors_per_label)
                except ValueError:
                    return None
                if cached_neighbors_per_label != expected_neighbors_per_label:
                    return None
        return payload

    def _candidate_tool_cache_paths(
        self,
        *,
        tool_name: str,
        smiles: str,
        cache_variant: str | None,
    ) -> list[Path]:
        smiles_digest = self._smiles_cache_digest(smiles)
        task_cache_root = self.tool_cache_root / self.feature_set_name / self.task
        candidate_paths = sorted(task_cache_root.glob(f"*/{tool_name}/{smiles_digest}.json"))
        if cache_variant:
            candidate_paths.extend(sorted(task_cache_root.glob(f"*/{tool_name}/{cache_variant}/{smiles_digest}.json")))
        return candidate_paths

    def _find_compatible_cached_tool_payload_path(
        self,
        *,
        tool_name: str,
        smiles: str,
        neighbors_per_label: object = None,
    ) -> Path | None:
        cache_variant = self._tool_cache_variant(tool_name=tool_name, neighbors_per_label=neighbors_per_label)
        current_path = self._tool_cache_path(tool_name=tool_name, smiles=smiles, cache_variant=cache_variant)
        if current_path.exists() and self._read_cached_tool_payload(
            current_path,
            tool_name=tool_name,
            smiles=smiles,
            neighbors_per_label=neighbors_per_label,
        ):
            return current_path

        cache_key = (tool_name, str(smiles), str(cache_variant or ""))
        path_cache = getattr(self, "_compatible_tool_cache_path_cache", None)
        if path_cache is not None and cache_key in path_cache:
            return path_cache[cache_key]

        for candidate_path in self._candidate_tool_cache_paths(
            tool_name=tool_name,
            smiles=smiles,
            cache_variant=cache_variant,
        ):
            if candidate_path == current_path:
                continue
            if self._read_cached_tool_payload(
                candidate_path,
                tool_name=tool_name,
                smiles=smiles,
                neighbors_per_label=neighbors_per_label,
            ):
                if path_cache is not None:
                    path_cache[cache_key] = candidate_path
                return candidate_path

        if path_cache is not None:
            path_cache[cache_key] = None
        return None

    def _load_cached_tool_payload(
        self,
        *,
        tool_name: str,
        smiles: str,
        neighbors_per_label: object = None,
    ) -> dict[str, object] | None:
        cache_variant = self._tool_cache_variant(tool_name=tool_name, neighbors_per_label=neighbors_per_label)
        cache_key = (tool_name, str(smiles), str(cache_variant or ""))
        if cache_key in self._tool_payload_cache:
            return self._tool_payload_cache[cache_key]
        if not self.enable_tool_cache:
            return None

        cache_path = self._find_compatible_cached_tool_payload_path(
            tool_name=tool_name,
            smiles=smiles,
            neighbors_per_label=neighbors_per_label,
        )
        if cache_path is None:
            return None

        payload = self._read_cached_tool_payload(
            cache_path,
            tool_name=tool_name,
            smiles=smiles,
            neighbors_per_label=neighbors_per_label,
        )
        if payload is None:
            return None
        self._tool_payload_cache[cache_key] = payload
        return payload

    def _store_cached_tool_payload(
        self,
        *,
        tool_name: str,
        smiles: str,
        payload: dict[str, object],
        neighbors_per_label: object = None,
    ) -> dict[str, object]:
        cache_variant = self._tool_cache_variant(tool_name=tool_name, neighbors_per_label=neighbors_per_label)
        cache_key = (tool_name, str(smiles), str(cache_variant or ""))
        self._tool_payload_cache[cache_key] = payload
        if not self.enable_tool_cache:
            return payload

        cache_path = self._tool_cache_path(tool_name=tool_name, smiles=smiles, cache_variant=cache_variant)
        cache_parameters = {}
        if tool_name == "compare_similar_mols":
            cache_parameters["neighbors_per_label"] = _normalize_neighbors_per_label(neighbors_per_label)
        self._store_tool_cache_signature_manifest()
        save_json(
            cache_path,
            {
                "schema_version": AGENT_TOOL_PAYLOAD_CACHE_SCHEMA_VERSION,
                "cache_signature_version": AGENT_TOOL_CACHE_SIGNATURE_VERSION,
                "tool_name": tool_name,
                "task": self.task,
                "feature_set_name": self.feature_set_name,
                "cache_namespace": self._tool_cache_namespace,
                "cache_variant": cache_variant,
                "cache_parameters": cache_parameters,
                "smiles": str(smiles),
                "payload": payload,
            },
        )
        return payload

    def _get_smiles_index(self) -> dict[str, list[dict[str, object]]]:
        if self._smiles_index is None:
            index: dict[str, list[dict[str, object]]] = {}
            for split in ("train", "valid", "test"):
                task_split = load_tdc_split(self.task, split, data_root=self.dataset_root)
                for smiles, label, scaffold in zip(task_split.smiles, task_split.labels, task_split.scaffolds):
                    index.setdefault(str(smiles), []).append(
                        {
                            "split": split,
                            "label": int(label),
                            "scaffold": str(scaffold),
                        }
                    )
            self._smiles_index = index
        return self._smiles_index

    def _resolve_tool_smiles(self, smiles: str) -> str:
        smiles_text = str(smiles)
        if smiles_text in self._resolved_smiles_cache:
            return self._resolved_smiles_cache[smiles_text]

        index = self._get_smiles_index()
        if smiles_text in index:
            self._resolved_smiles_cache[smiles_text] = smiles_text
            return smiles_text

        canonical_smiles = _canonicalize_smiles_for_tool_lookup(smiles_text)
        if canonical_smiles and canonical_smiles in index:
            self._resolved_smiles_cache[smiles_text] = canonical_smiles
            return canonical_smiles

        self._resolved_smiles_cache[smiles_text] = smiles_text
        return smiles_text

    def _resolve_query_metadata(self, smiles: str) -> dict[str, object]:
        index = self._get_smiles_index()
        try:
            memberships = list(index[str(smiles)])
        except KeyError as exc:
            raise KeyError(
                f"SMILES {smiles!r} is not part of task {self.task!r}; compare_similar_mols requires a known task molecule."
            ) from exc

        split_priority = {"valid": 0, "test": 1, "train": 2}
        selected = sorted(
            memberships,
            key=lambda item: (split_priority.get(str(item["split"]), 99), str(item["split"])),
        )[0]
        return {
            **selected,
            "all_memberships": memberships,
        }

    def _get_train_feature_cache(self):
        if self._train_raw_df is None or self._train_raw_values is None or self._train_index_by_smiles is None:
            train_split = load_tdc_split(self.task, "train", data_root=self.dataset_root)
            self._train_raw_df = coerce_numeric_feature_frame(self.feature_source.load(train_split.smiles)).reset_index(drop=True)
            self._train_raw_values = self._train_raw_df.to_numpy(dtype=float)
            self._train_index_by_smiles = {smiles: index for index, smiles in enumerate(train_split.smiles)}
        return self._train_raw_df, self._train_raw_values, self._train_index_by_smiles

    def _present_functional_groups(self, raw_row) -> list[dict[str, object]]:
        present_groups: list[dict[str, object]] = []
        for feature_name in self.global_feature_columns:
            semantics = self.global_feature_semantics[feature_name]
            if not _is_functional_group_feature(semantics):
                continue
            raw_value = _safe_scalar(raw_row[feature_name])
            try:
                numeric_value = float(raw_value)
            except (TypeError, ValueError):
                continue
            if numeric_value == 0.0:
                continue
            present_groups.append(
                {
                    **semantics,
                    "feature_name": feature_name,
                    "feature_value": raw_value,
                    "feature_value_text": _infer_value_phrase(raw_value, semantics),
                }
            )
        present_groups.sort(key=lambda item: (str(item["display_name"]), str(item["feature_name"])))
        return present_groups

    def _functional_group_differences(self, *, query_raw_row, neighbor_raw_row) -> list[dict[str, object]]:
        differences: list[dict[str, object]] = []
        for feature_name in self.local_raw_feature_columns:
            semantics = self.local_feature_semantics[feature_name]
            if not _is_functional_group_feature(semantics):
                continue
            query_value = _safe_scalar(query_raw_row[feature_name])
            neighbor_value = _safe_scalar(neighbor_raw_row[feature_name])
            try:
                query_numeric = float(query_value)
                neighbor_numeric = float(neighbor_value)
            except (TypeError, ValueError):
                continue
            if abs(query_numeric - neighbor_numeric) < 1e-12:
                continue
            if query_numeric == 0.0 and neighbor_numeric == 0.0:
                continue
            differences.append(
                {
                    **semantics,
                    "feature_name": feature_name,
                    "query_value": query_value,
                    "query_value_text": _infer_value_phrase(query_value, semantics),
                    "neighbor_value": neighbor_value,
                    "neighbor_value_text": _infer_value_phrase(neighbor_value, semantics),
                    "delta_value": query_numeric - neighbor_numeric,
                }
            )
        differences.sort(key=lambda item: (str(item["display_name"]), str(item["feature_name"])))
        return differences

    def get_mol_properties_and_fg_payload(
        self,
        smiles: str,
        *,
        neighbors_per_label: object = None,
    ) -> dict[str, object]:
        if not isinstance(self.global_bundle, dict):
            raise RuntimeError(
                f"get_mol_properties_and_fg requires a global EBM bundle for task {self.task!r}; "
                "the current manifest only supports retrieval-based compare_similar_mols."
            )
        smiles = self._resolve_tool_smiles(smiles)
        cached_payload = self._load_cached_tool_payload(tool_name="get_mol_properties_and_fg", smiles=smiles)
        if cached_payload is not None:
            return cached_payload

        raw_feature_df = self.feature_source.load([smiles])
        aligned_df, transformed_df = transform_feature_frame(raw_feature_df, self.global_bundle["preprocessor"])
        x_matrix = transformed_df.to_numpy(dtype=float)

        model = self.global_bundle["model"]
        global_score = float(model.predict_proba(x_matrix)[0, 1])
        global_prediction = int(model.predict(x_matrix)[0])
        term_contributions = np.asarray(model.eval_terms(x_matrix), dtype=float)[0]
        rank_map = _sorted_rank_map(term_contributions)
        present_functional_groups = self._present_functional_groups(aligned_df.iloc[0])

        query_memberships = self._get_smiles_index().get(str(smiles), [])
        query_metadata = self._resolve_query_metadata(smiles) if query_memberships else {}
        dense_features: list[dict[str, object]] = []
        current_sample_top_features: list[str] = []
        top_ranked_indices = sorted(rank_map, key=lambda index: rank_map[index])[: int(self.manifest["global_tool"]["top_k_per_sample"])]
        current_sample_top_features = [
            self.global_feature_columns[index]
            for index in top_ranked_indices
            if not _is_functional_group_feature(self.global_feature_semantics[self.global_feature_columns[index]])
        ]

        for feature_name in self.manifest["global_tool"]["dense_feature_names"]:
            if feature_name not in self.global_feature_index:
                continue
            term_index = self.global_feature_index[feature_name]
            semantics = self.global_feature_semantics[feature_name]
            raw_value = _safe_scalar(aligned_df.iloc[0][feature_name])
            contribution = float(term_contributions[term_index])
            contribution_label = _label_payload(1 if contribution >= 0.0 else 0, self.label_semantics)
            dense_features.append(
                {
                    **semantics,
                    "feature_name": feature_name,
                    "feature_value": _sanitize_json_value(raw_value),
                    "feature_value_text": _infer_value_phrase(raw_value, semantics),
                    "model_input_value": float(transformed_df.iloc[0][feature_name]),
                    "contribution": contribution,
                    "contribution_abs": float(abs(contribution)),
                    "current_sample_contribution_rank": rank_map.get(term_index),
                    "supports_label": int(contribution_label["label"]),
                    "supports_option": str(contribution_label["option"]),
                    "supports_text": str(contribution_label["text"]),
                }
            )
            missing_reason = _missing_value_reason(raw_value, semantics)
            if missing_reason is not None:
                dense_features[-1]["feature_value_missing_reason"] = missing_reason

        payload = {
            "tool_name": "get_mol_properties_and_fg",
            "task": self.task,
            "smiles": str(smiles),
            "query_split": query_metadata.get("split"),
            "query_label": query_metadata.get("label"),
            "query_label_semantics": (
                _label_payload(int(query_metadata["label"]), self.label_semantics)
                if "label" in query_metadata
                else None
            ),
            "query_scaffold": query_metadata.get("scaffold"),
            "query_memberships": query_metadata.get("all_memberships", query_memberships),
            "global_prediction": global_prediction,
            "global_prediction_semantics": _label_payload(global_prediction, self.label_semantics),
            "global_score": global_score,
            "dense_feature_count": int(len(dense_features)),
            "dense_feature_names": list(self.manifest["global_tool"]["dense_feature_names"]),
            "current_sample_top_property_feature_names": current_sample_top_features,
            "present_functional_group_count": int(len(present_functional_groups)),
            "present_functional_groups": present_functional_groups,
            "features": dense_features,
        }
        return self._store_cached_tool_payload(
            tool_name="get_mol_properties_and_fg",
            smiles=smiles,
            payload=payload,
        )

    def get_mol_properties_and_fg(
        self,
        smiles: str,
        *,
        neighbors_per_label: object = None,
    ) -> str:
        return _render_global_payload_text(self.get_mol_properties_and_fg_payload(smiles))

    def _build_neighbor_feature_payloads(
        self,
        *,
        query_raw_row,
        neighbor_raw_row,
        term_contributions: np.ndarray,
        dense_feature_names: list[str],
        top_term_k: int,
    ) -> tuple[list[dict[str, object]], list[str]]:
        rank_map = _sorted_rank_map(term_contributions)
        top_pair_feature_names = [
            self.local_raw_feature_columns[index]
            for index in sorted(rank_map, key=lambda index: rank_map[index])[:top_term_k]
            if not _is_functional_group_feature(self.local_feature_semantics[self.local_raw_feature_columns[index]])
        ]
        feature_payloads: list[dict[str, object]] = []

        for feature_name in dense_feature_names:
            if feature_name not in self.local_feature_index:
                continue
            term_index = self.local_feature_index[feature_name]
            semantics = self.local_feature_semantics[feature_name]
            neighbor_value = _safe_scalar(neighbor_raw_row[feature_name])
            query_value = _safe_scalar(query_raw_row[feature_name])
            delta_value, delta_value_text, delta_missing_reason = _delta_value_payload(
                base_value=neighbor_value,
                query_value=query_value,
                semantics=semantics,
            )
            contribution = float(term_contributions[term_index])
            contribution_label = _label_payload(1 if contribution >= 0.0 else 0, self.label_semantics)
            pair_rank = rank_map.get(term_index)
            feature_payload = {
                **semantics,
                "feature_name": feature_name,
                "neighbor_value": _sanitize_json_value(neighbor_value),
                "neighbor_value_text": _infer_value_phrase(neighbor_value, semantics),
                "query_value": _sanitize_json_value(query_value),
                "query_value_text": _infer_value_phrase(query_value, semantics),
                "delta_value": delta_value,
                "delta_value_text": delta_value_text,
                "pair_contribution": contribution,
                "pair_contribution_abs": float(abs(contribution)),
                "pair_contribution_rank": pair_rank,
                "is_pair_top_term": bool(pair_rank is not None and pair_rank <= top_term_k),
                "supports_label": int(contribution_label["label"]),
                "supports_option": str(contribution_label["option"]),
                "supports_text": str(contribution_label["text"]),
            }
            neighbor_missing_reason = _missing_value_reason(neighbor_value, semantics)
            query_missing_reason = _missing_value_reason(query_value, semantics)
            if neighbor_missing_reason is not None:
                feature_payload["neighbor_value_missing_reason"] = neighbor_missing_reason
            if query_missing_reason is not None:
                feature_payload["query_value_missing_reason"] = query_missing_reason
            if delta_missing_reason is not None:
                feature_payload["delta_value_missing_reason"] = delta_missing_reason
            feature_payloads.append(feature_payload)
        return feature_payloads, top_pair_feature_names

    def _build_retrieval_neighbor_feature_payloads(
        self,
        *,
        query_raw_row,
        neighbor_raw_row,
        dense_feature_names: list[str],
    ) -> list[dict[str, object]]:
        feature_payloads: list[dict[str, object]] = []
        for feature_name in dense_feature_names:
            if feature_name not in self.local_feature_index:
                continue
            semantics = self.local_feature_semantics[feature_name]
            neighbor_value = _safe_scalar(neighbor_raw_row[feature_name])
            query_value = _safe_scalar(query_raw_row[feature_name])
            delta_value, delta_value_text, delta_missing_reason = _delta_value_payload(
                base_value=neighbor_value,
                query_value=query_value,
                semantics=semantics,
            )
            feature_payload = {
                **semantics,
                "feature_name": feature_name,
                "neighbor_value": _sanitize_json_value(neighbor_value),
                "neighbor_value_text": _infer_value_phrase(neighbor_value, semantics),
                "query_value": _sanitize_json_value(query_value),
                "query_value_text": _infer_value_phrase(query_value, semantics),
                "delta_value": delta_value,
                "delta_value_text": delta_value_text,
            }
            neighbor_missing_reason = _missing_value_reason(neighbor_value, semantics)
            query_missing_reason = _missing_value_reason(query_value, semantics)
            if neighbor_missing_reason is not None:
                feature_payload["neighbor_value_missing_reason"] = neighbor_missing_reason
            if query_missing_reason is not None:
                feature_payload["query_value_missing_reason"] = query_missing_reason
            if delta_missing_reason is not None:
                feature_payload["delta_value_missing_reason"] = delta_missing_reason
            feature_payloads.append(feature_payload)
        return feature_payloads

    def _build_neighbor_group_payload(
        self,
        *,
        query_smiles: str,
        query_split: str,
        query_scaffold: str,
        query_raw_row,
        query_raw_values: np.ndarray,
        desired_label: int,
        top_k_neighbors: int,
        model_bundle: dict[str, object],
    ) -> tuple[list[dict[str, object]], list[float], list[float]]:
        train_raw_df, train_raw_values, train_index_by_smiles = self._get_train_feature_cache()
        neighbors = self.retriever.get_neighbors(
            task=self.task,
            query_smiles=query_smiles,
            split=query_split,
            desired_label=desired_label,
            top_k=top_k_neighbors,
            exclude_same_scaffold=bool(self.manifest["local_tool"]["strict_cross_scaffold_pairs"]),
            query_scaffold=query_scaffold,
        )
        valid_neighbors = [neighbor for neighbor in neighbors if neighbor.smiles in train_index_by_smiles]
        if not valid_neighbors:
            return [], [], []

        neighbor_indices = np.asarray(
            [train_index_by_smiles[neighbor.smiles] for neighbor in valid_neighbors],
            dtype=int,
        )
        dense_feature_names = list(self.manifest["local_tool"]["dense_feature_names"])

        if self.compare_mode == "retrieval_only":
            neighbor_payloads: list[dict[str, object]] = []
            for row_index, neighbor in enumerate(valid_neighbors):
                neighbor_raw_row = train_raw_df.iloc[neighbor_indices[row_index]]
                neighbor_payloads.append(
                    {
                        "neighbor_smiles": neighbor.smiles,
                        "neighbor_label": int(neighbor.label),
                        "neighbor_label_semantics": _label_payload(int(neighbor.label), self.label_semantics),
                        "neighbor_similarity": float(neighbor.similarity),
                        "neighbor_scaffold": str(neighbor.scaffold),
                        "comparison_mode": "retrieval_only",
                        "functional_group_differences": self._functional_group_differences(
                            query_raw_row=query_raw_row,
                            neighbor_raw_row=neighbor_raw_row,
                        ),
                        "feature_comparisons": self._build_retrieval_neighbor_feature_payloads(
                            query_raw_row=query_raw_row,
                            neighbor_raw_row=neighbor_raw_row,
                            dense_feature_names=dense_feature_names,
                        ),
                    }
                )
            return (
                neighbor_payloads,
                [],
                [float(neighbor.similarity) for neighbor in valid_neighbors],
            )

        if not isinstance(model_bundle, dict):
            raise RuntimeError("pair_ebm compare mode requires a pair EBM model bundle")
        query_matrix = np.repeat(query_raw_values[np.newaxis, :], repeats=len(valid_neighbors), axis=0)
        pair_matrix = build_pair_matrix(
            query_values=query_matrix,
            neighbor_values=train_raw_values[neighbor_indices],
        )

        model = model_bundle["model"]
        pair_scores = model.predict_proba(pair_matrix)[:, 1]
        pair_predictions = model.predict(pair_matrix)
        pair_term_matrix = np.asarray(model.eval_terms(pair_matrix), dtype=float)
        top_term_k = int(self.manifest["local_tool"]["top_term_k_per_neighbor"])

        neighbor_payloads: list[dict[str, object]] = []
        for row_index, neighbor in enumerate(valid_neighbors):
            neighbor_raw_row = train_raw_df.iloc[neighbor_indices[row_index]]
            feature_payloads, top_pair_feature_names = self._build_neighbor_feature_payloads(
                query_raw_row=query_raw_row,
                neighbor_raw_row=neighbor_raw_row,
                term_contributions=pair_term_matrix[row_index],
                dense_feature_names=dense_feature_names,
                top_term_k=top_term_k,
            )
            pair_prediction = int(pair_predictions[row_index])
            neighbor_payloads.append(
                {
                    "neighbor_smiles": neighbor.smiles,
                    "neighbor_label": int(neighbor.label),
                    "neighbor_label_semantics": _label_payload(int(neighbor.label), self.label_semantics),
                    "neighbor_similarity": float(neighbor.similarity),
                    "neighbor_scaffold": str(neighbor.scaffold),
                    "pair_model_type": "positive_neighbor_model" if int(neighbor.label) == 1 else "negative_neighbor_model",
                    "pair_score": float(pair_scores[row_index]),
                    "pair_prediction": pair_prediction,
                    "pair_prediction_semantics": _label_payload(pair_prediction, self.label_semantics),
                    "top_pair_feature_names": top_pair_feature_names,
                    "functional_group_differences": self._functional_group_differences(
                        query_raw_row=query_raw_row,
                        neighbor_raw_row=neighbor_raw_row,
                    ),
                    "feature_comparisons": feature_payloads,
                }
            )

        return (
            neighbor_payloads,
            [float(score) for score in pair_scores.tolist()],
            [float(neighbor.similarity) for neighbor in valid_neighbors],
        )

    def compare_similar_mols_payload(
        self,
        smiles: str,
        *,
        neighbors_per_label: object = DEFAULT_NEIGHBORS_PER_LABEL,
    ) -> dict[str, object]:
        neighbors_per_label = _normalize_neighbors_per_label(neighbors_per_label)
        smiles = self._resolve_tool_smiles(smiles)
        cached_payload = self._load_cached_tool_payload(
            tool_name="compare_similar_mols",
            smiles=smiles,
            neighbors_per_label=neighbors_per_label,
        )
        if cached_payload is not None:
            return cached_payload

        query_metadata = self._resolve_query_metadata(smiles)
        query_split = str(query_metadata["split"])
        query_label = int(query_metadata["label"])
        query_scaffold = str(query_metadata["scaffold"])

        query_raw_df = coerce_numeric_feature_frame(self.feature_source.load([smiles])).reset_index(drop=True)
        query_raw_row = query_raw_df.iloc[0]
        query_raw_values = query_raw_df.to_numpy(dtype=float)[0]
        query_present_functional_groups = self._present_functional_groups(query_raw_row)

        positive_neighbors, pos_scores, pos_similarities = self._build_neighbor_group_payload(
            query_smiles=smiles,
            query_split=query_split,
            query_scaffold=query_scaffold,
            query_raw_row=query_raw_row,
            query_raw_values=query_raw_values,
            desired_label=1,
            top_k_neighbors=neighbors_per_label,
            model_bundle=self.pos_bundle,
        )
        negative_neighbors, neg_scores, neg_similarities = self._build_neighbor_group_payload(
            query_smiles=smiles,
            query_split=query_split,
            query_scaffold=query_scaffold,
            query_raw_row=query_raw_row,
            query_raw_values=query_raw_values,
            desired_label=0,
            top_k_neighbors=neighbors_per_label,
            model_bundle=self.neg_bundle,
        )

        if self.compare_mode == "pair_ebm":
            aggregated = aggregate_local_scores(
                pos_scores=pos_scores,
                pos_similarities=pos_similarities,
                neg_scores=neg_scores,
                neg_similarities=neg_similarities,
            )
            local_score = float(aggregated["s_local"])
            local_prediction = 1 if local_score >= 0.5 else 0
            s_pos = float(aggregated["s_pos"]) if not math.isnan(float(aggregated["s_pos"])) else None
            s_neg = float(aggregated["s_neg"]) if not math.isnan(float(aggregated["s_neg"])) else None
            local_prediction_semantics = _label_payload(local_prediction, self.label_semantics)
        else:
            local_score = None
            local_prediction = None
            s_pos = None
            s_neg = None
            local_prediction_semantics = None

        payload = {
            "tool_name": "compare_similar_mols",
            "task": self.task,
            "smiles": str(smiles),
            "comparison_mode": self.compare_mode,
            "query_split": query_split,
            "query_label": query_label,
            "query_label_semantics": _label_payload(query_label, self.label_semantics),
            "query_scaffold": query_scaffold,
            "query_memberships": query_metadata.get("all_memberships", []),
            "query_present_functional_group_count": int(len(query_present_functional_groups)),
            "query_present_functional_groups": query_present_functional_groups,
            "local_prediction": local_prediction,
            "local_prediction_semantics": local_prediction_semantics,
            "local_score": local_score,
            "s_pos": s_pos,
            "s_neg": s_neg,
            "neighbors_per_label": int(neighbors_per_label),
            "top_k_pos": int(neighbors_per_label),
            "top_k_neg": int(neighbors_per_label),
            "num_positive_neighbors": int(len(positive_neighbors)),
            "num_negative_neighbors": int(len(negative_neighbors)),
            "dense_feature_count": int(
                self.manifest["local_tool"].get(
                    "dense_feature_count",
                    len(self.manifest["local_tool"]["dense_feature_names"]),
                )
            ),
            "dense_feature_names": list(self.manifest["local_tool"]["dense_feature_names"]),
            "positive_neighbors": positive_neighbors,
            "negative_neighbors": negative_neighbors,
        }
        return self._store_cached_tool_payload(
            tool_name="compare_similar_mols",
            smiles=smiles,
            payload=payload,
            neighbors_per_label=neighbors_per_label,
        )

    def compare_similar_mols(
        self,
        smiles: str,
        *,
        neighbors_per_label: object = DEFAULT_NEIGHBORS_PER_LABEL,
    ) -> str:
        return _render_local_payload_text(
            self.compare_similar_mols_payload(smiles, neighbors_per_label=neighbors_per_label)
        )
