from __future__ import annotations

from pathlib import Path
from typing import Any

from trim.reasoning.semantics.task_semantics import load_task_label_semantics
from trim.reasoning.rewrite.playbooks import load_task_playbook
from trim.utils.io import ensure_directory, load_json, save_json
from trim.utils.paths import OUTPUTS_ROOT, resolve_project_path


REWRITE_CANDIDATE_SCHEMA_VERSION = "trim_reasoning_rewrite_v1"
DEFAULT_REWRITE_CANDIDATE_OUTPUT_ROOT = OUTPUTS_ROOT / "reasoning_rewrite_candidates"


def _sample_paths_by_index(directory: str | Path) -> dict[int, Path]:
    root = resolve_project_path(directory)
    sample_paths: dict[int, Path] = {}
    for path in sorted(root.glob("sample_*.json")):
        stem = path.stem
        try:
            sample_index = int(stem.split("_")[-1])
        except ValueError as exc:
            raise ValueError(f"Could not parse sample index from {path}") from exc
        sample_paths[sample_index] = path.resolve()
    if not sample_paths:
        raise FileNotFoundError(f"No sample_*.json files found in {root}")
    return sample_paths


def _teacher_case(*, global_correct: bool, local_correct: bool) -> str:
    if global_correct and local_correct:
        return "both_correct"
    if global_correct:
        return "global_only_correct"
    if local_correct:
        return "local_only_correct"
    return "both_wrong"


def _drop_reason(teacher_case: str) -> str | None:
    if teacher_case == "both_wrong":
        return "both_global_and_local_wrong"
    return None


def _default_label_semantics() -> dict[int, dict[str, str]]:
    return {
        0: {"option": "A", "text": "label 0"},
        1: {"option": "B", "text": "label 1"},
    }


def _resolve_label_semantics(task: str) -> dict[int, dict[str, str]]:
    loaded = load_task_label_semantics(task)
    if loaded is None:
        return _default_label_semantics()
    payload = _default_label_semantics()
    payload.update(loaded)
    return payload


def _validate_alignment(global_payload: dict[str, Any], local_payload: dict[str, Any]) -> None:
    fields = ("sample_id", "task", "split", "sample_index", "smiles", "gt_label")
    for field_name in fields:
        if global_payload.get(field_name) != local_payload.get(field_name):
            raise ValueError(
                f"Global/local mismatch for field {field_name}: "
                f"{global_payload.get(field_name)!r} != {local_payload.get(field_name)!r}"
            )


def _extract_neighbor_similarities(local_payload: dict[str, Any], *, expected_neighbor_count: int) -> list[dict[str, Any]]:
    evidence = dict(local_payload["local_per_neighbor_decision_evidence"])
    rows: list[dict[str, Any]] = []
    for group_name in ("positive_neighbors", "negative_neighbors"):
        for rank, neighbor in enumerate(evidence[group_name], start=1):
            rows.append(
                {
                    "neighbor_role": str(neighbor["neighbor_role"]),
                    "neighbor_rank": int(rank),
                    "neighbor_id": str(neighbor["neighbor_id"]),
                    "neighbor_smiles": str(neighbor["neighbor_smiles"]),
                    "similarity": float(neighbor["neighbor_similarity"]),
                }
            )
    if len(rows) != expected_neighbor_count:
        raise ValueError(
            f"Expected {expected_neighbor_count} neighbors for local rewrite input, found {len(rows)}"
        )
    return rows


def _build_candidate_record(
    *,
    global_payload: dict[str, Any],
    local_payload: dict[str, Any],
    playbook_text: str,
    playbook_path: Path,
    expected_neighbor_count: int,
) -> dict[str, Any]:
    _validate_alignment(global_payload, local_payload)

    global_correct = bool(global_payload["global_prediction_correct"])
    local_correct = bool(local_payload["local_prediction_correct"])
    teacher_case = _teacher_case(global_correct=global_correct, local_correct=local_correct)
    keep_for_rewrite = teacher_case != "both_wrong"
    gt_label_semantics = dict(global_payload["gt_label_semantics"])
    label_semantics = _resolve_label_semantics(str(global_payload["task"]))
    task_description = (
        f"molecule local analog-comparison task {global_payload['task']} "
        f"where option (A) means {label_semantics[0]['text']} and option (B) means {label_semantics[1]['text']}"
    )

    candidate = {
        "schema_version": REWRITE_CANDIDATE_SCHEMA_VERSION,
        "candidate_stage": "pre_rewrite_filtered_inputs",
        "sample_id": str(global_payload["sample_id"]),
        "sample_index": int(global_payload["sample_index"]),
        "task": str(global_payload["task"]),
        "split": str(global_payload["split"]),
        "smiles": str(global_payload["smiles"]),
        "gt_label": int(global_payload["gt_label"]),
        "gt_label_semantics": gt_label_semantics,
        "global_prediction_correct": global_correct,
        "local_prediction_correct": local_correct,
        "keep_for_rewrite": keep_for_rewrite,
        "drop_reason": _drop_reason(teacher_case),
        "teacher_case": teacher_case,
        "playbook_path": str(playbook_path),
        "global_rewrite_input": {
            "task_playbook": playbook_text,
            "task_description": (
                f"task {global_payload['task']} where option (A) means {label_semantics[0]['text']} "
                f"and option (B) means {label_semantics[1]['text']}"
            ),
            "global_middle_draft": str(global_payload["global_middle_draft"]),
        },
        "local_rewrite_input": {
            "task_playbook": playbook_text,
            "task_description": task_description,
            "positive_label_semantics": str(label_semantics[1]["text"]),
            "negative_label_semantics": str(label_semantics[0]["text"]),
            "neighbor_similarities": _extract_neighbor_similarities(
                local_payload,
                expected_neighbor_count=expected_neighbor_count,
            ),
            "local_per_neighbor_middle_draft": dict(local_payload["local_per_neighbor_middle_draft"]),
            "local_prediction": int(local_payload["local_prediction"]),
            "local_prediction_semantics": (
                f"option ({label_semantics[int(local_payload['local_prediction'])]['option']}): "
                f"{label_semantics[int(local_payload['local_prediction'])]['text']}"
            ),
        },
        "hybrid_rewrite_input": {
            "gt_label": int(global_payload["gt_label"]),
            "gt_label_semantics": gt_label_semantics,
        },
        "source_artifacts": {
            "global_evidence_path": str(global_payload["_source_path"]),
            "local_evidence_path": str(local_payload["_source_path"]),
        },
    }
    return candidate


def filter_rewrite_samples(
    *,
    global_dir: str | Path,
    local_dir: str | Path,
    output_dir: str | Path | None = None,
    sample_indices: list[int] | None = None,
    max_samples: int | None = None,
) -> dict[str, Any]:
    global_paths = _sample_paths_by_index(global_dir)
    local_paths = _sample_paths_by_index(local_dir)

    shared_indices = sorted(set(global_paths).intersection(local_paths))
    if not shared_indices:
        raise ValueError("No overlapping sample indices found between global and local evidence directories")

    if sample_indices is not None:
        target_indices = [int(index) for index in sample_indices]
        missing = [index for index in target_indices if index not in shared_indices]
        if missing:
            raise IndexError(f"Requested sample indices missing from shared evidence set: {missing}")
    else:
        target_indices = shared_indices

    if max_samples is not None:
        target_indices = target_indices[: int(max_samples)]

    task_name: str | None = None
    split_name: str | None = None
    kept_records: list[dict[str, Any]] = []
    dropped_records: list[dict[str, Any]] = []

    for sample_index in target_indices:
        global_payload = load_json(global_paths[sample_index])
        local_payload = load_json(local_paths[sample_index])
        _validate_alignment(global_payload, local_payload)

        global_correct = bool(global_payload["global_prediction_correct"])
        local_correct = bool(local_payload["local_prediction_correct"])
        teacher_case = _teacher_case(global_correct=global_correct, local_correct=local_correct)
        record = {
            "sample_id": str(global_payload["sample_id"]),
            "sample_index": int(sample_index),
            "task": str(global_payload["task"]),
            "split": str(global_payload["split"]),
            "smiles": str(global_payload["smiles"]),
            "gt_label": int(global_payload["gt_label"]),
            "global_prediction_correct": global_correct,
            "local_prediction_correct": local_correct,
            "teacher_case": teacher_case,
            "keep_for_rewrite": teacher_case != "both_wrong",
            "drop_reason": _drop_reason(teacher_case),
        }
        task_name = record["task"] if task_name is None else task_name
        split_name = record["split"] if split_name is None else split_name
        if record["keep_for_rewrite"]:
            kept_records.append(record)
        else:
            dropped_records.append(record)

    artifact_paths: dict[str, Any] = {}
    resolved_output_dir: Path | None = None
    if output_dir is not None:
        resolved_output_dir = ensure_directory(resolve_project_path(output_dir))
        kept_path = resolved_output_dir / "kept_records.json"
        dropped_path = resolved_output_dir / "dropped_records.json"
        save_json(kept_path, kept_records)
        save_json(dropped_path, dropped_records)
        artifact_paths = {
            "output_dir": str(resolved_output_dir.resolve()),
            "kept_records_path": str(kept_path.resolve()),
            "dropped_records_path": str(dropped_path.resolve()),
        }

    manifest = {
        "schema_version": REWRITE_CANDIDATE_SCHEMA_VERSION,
        "candidate_stage": "pre_rewrite_filter_only",
        "task": task_name,
        "split": split_name,
        "global_dir": str(resolve_project_path(global_dir)),
        "local_dir": str(resolve_project_path(local_dir)),
        "total_record_count": int(len(target_indices)),
        "kept_record_count": int(len(kept_records)),
        "dropped_record_count": int(len(dropped_records)),
        "kept_sample_indices": [int(record["sample_index"]) for record in kept_records],
        "dropped_sample_indices": [int(record["sample_index"]) for record in dropped_records],
        "teacher_case_counts": {
            "both_correct": int(sum(record["teacher_case"] == "both_correct" for record in kept_records)),
            "global_only_correct": int(sum(record["teacher_case"] == "global_only_correct" for record in kept_records)),
            "local_only_correct": int(sum(record["teacher_case"] == "local_only_correct" for record in kept_records)),
            "both_wrong": int(len(dropped_records)),
        },
        "artifacts": artifact_paths,
    }
    if resolved_output_dir is not None:
        save_json(resolved_output_dir / "manifest.json", manifest)
    return manifest


def build_rewrite_candidates(
    *,
    global_dir: str | Path,
    local_dir: str | Path,
    output_dir: str | Path | None = None,
    playbook_root: str | Path | None = None,
    sample_indices: list[int] | None = None,
    max_samples: int | None = None,
    expected_neighbor_count: int = 6,
) -> dict[str, Any]:
    global_paths = _sample_paths_by_index(global_dir)
    local_paths = _sample_paths_by_index(local_dir)

    shared_indices = sorted(set(global_paths).intersection(local_paths))
    if not shared_indices:
        raise ValueError("No overlapping sample indices found between global and local evidence directories")

    if sample_indices is not None:
        target_indices = [int(index) for index in sample_indices]
        missing = [index for index in target_indices if index not in shared_indices]
        if missing:
            raise IndexError(f"Requested sample indices missing from shared evidence set: {missing}")
    else:
        target_indices = shared_indices

    if max_samples is not None:
        target_indices = target_indices[: int(max_samples)]

    kept_records: list[dict[str, Any]] = []
    dropped_records: list[dict[str, Any]] = []
    task_name: str | None = None
    split_name: str | None = None

    for sample_index in target_indices:
        global_payload = load_json(global_paths[sample_index])
        local_payload = load_json(local_paths[sample_index])
        global_payload["_source_path"] = str(global_paths[sample_index])
        local_payload["_source_path"] = str(local_paths[sample_index])
        _validate_alignment(global_payload, local_payload)

        task = str(global_payload["task"])
        split = str(global_payload["split"])
        task_name = task if task_name is None else task_name
        split_name = split if split_name is None else split_name
        playbook_text, playbook_path = load_task_playbook(task, playbook_root=playbook_root)

        global_correct = bool(global_payload["global_prediction_correct"])
        local_correct = bool(local_payload["local_prediction_correct"])
        teacher_case = _teacher_case(global_correct=global_correct, local_correct=local_correct)
        if teacher_case == "both_wrong":
            dropped_records.append(
                {
                    "sample_id": str(global_payload["sample_id"]),
                    "sample_index": int(sample_index),
                    "smiles": str(global_payload["smiles"]),
                    "teacher_case": teacher_case,
                    "drop_reason": _drop_reason(teacher_case),
                }
            )
            continue

        kept_records.append(
            _build_candidate_record(
                global_payload=global_payload,
                local_payload=local_payload,
                playbook_text=playbook_text,
                playbook_path=playbook_path,
                expected_neighbor_count=expected_neighbor_count,
            )
        )

    artifact_paths: dict[str, Any] = {}
    resolved_output_dir: Path | None = None
    if output_dir is not None:
        resolved_output_dir = ensure_directory(resolve_project_path(output_dir))
        written_files = []
        for record in kept_records:
            sample_path = resolved_output_dir / f"sample_{int(record['sample_index']):05d}.json"
            save_json(sample_path, record)
            written_files.append(str(sample_path.resolve()))
        artifact_paths = {
            "output_dir": str(resolved_output_dir.resolve()),
            "sample_files": written_files,
        }

    manifest = {
        "schema_version": REWRITE_CANDIDATE_SCHEMA_VERSION,
        "candidate_stage": "pre_rewrite_filtered_inputs",
        "task": task_name,
        "split": split_name,
        "global_dir": str(resolve_project_path(global_dir)),
        "local_dir": str(resolve_project_path(local_dir)),
        "kept_record_count": int(len(kept_records)),
        "dropped_record_count": int(len(dropped_records)),
        "kept_sample_indices": [int(record["sample_index"]) for record in kept_records],
        "dropped_records": dropped_records,
        "artifacts": artifact_paths,
    }
    if resolved_output_dir is not None:
        save_json(resolved_output_dir / "manifest.json", manifest)
    return manifest
