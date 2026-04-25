from __future__ import annotations

from pathlib import Path
from typing import Any

from trim.reasoning.semantics.task_semantics import load_task_label_semantics
from trim.reasoning.rewrite.playbooks import load_task_playbook
from trim.reasoning.rewrite.playbooks import resolve_playbook_root
from trim.utils.io import ensure_directory, load_json, save_json
from trim.utils.paths import OUTPUTS_ROOT, resolve_project_path, serialize_project_path


REWRITE_CANDIDATE_SCHEMA_VERSION = "trim_reasoning_rewrite_v1"
DEFAULT_REWRITE_CANDIDATE_OUTPUT_ROOT = OUTPUTS_ROOT / "reasoning_rewrite_candidates"
TEACHER_FILTER_MODES = ("any_correct", "local_correct", "global_correct", "none")


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


def _validate_teacher_filter(teacher_filter: str) -> str:
    value = str(teacher_filter)
    if value not in TEACHER_FILTER_MODES:
        raise ValueError(f"Unsupported teacher_filter={value!r}; expected one of {TEACHER_FILTER_MODES}")
    return value


def _keep_for_teacher_filter(*, global_correct: bool, local_correct: bool, teacher_filter: str) -> bool:
    teacher_filter = _validate_teacher_filter(teacher_filter)
    if teacher_filter == "any_correct":
        return bool(global_correct or local_correct)
    if teacher_filter == "local_correct":
        return bool(local_correct)
    if teacher_filter == "global_correct":
        return bool(global_correct)
    if teacher_filter == "none":
        return True
    raise AssertionError(f"Unhandled teacher_filter={teacher_filter!r}")


def _drop_reason_for_filter(
    *,
    teacher_case: str,
    global_correct: bool,
    local_correct: bool,
    teacher_filter: str,
) -> str | None:
    if _keep_for_teacher_filter(
        global_correct=global_correct,
        local_correct=local_correct,
        teacher_filter=teacher_filter,
    ):
        return None
    if teacher_filter == "any_correct":
        return _drop_reason(teacher_case)
    if teacher_filter == "local_correct":
        return "local_prediction_wrong"
    if teacher_filter == "global_correct":
        return "global_prediction_wrong"
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


def _label_semantics_text(label: int, label_semantics: dict[int, dict[str, str]]) -> str:
    payload = label_semantics[int(label)]
    return f"option ({payload['option']}): {payload['text']}"


def _term_observation_text(term: dict[str, Any]) -> str:
    display_name = str(term["display_name"])
    base_value_text = str(term.get("base_value_text", term.get("base_value", "")))
    query_value_text = str(term.get("query_value_text", term.get("query_value", "")))
    delta_value_text = str(term.get("delta_value_text", term.get("delta_value", "")))
    return (
        f"For {display_name}, the neighbor value is {base_value_text}, the query value is "
        f"{query_value_text}, and the query-minus-neighbor delta is {delta_value_text}."
    )


def _build_observation_payload(term: dict[str, Any]) -> dict[str, Any]:
    return {
        "feature_name": str(term["feature_name"]),
        "display_name": str(term["display_name"]),
        "description": str(term.get("description", "")),
        "source_family": str(term.get("source_family", "")),
        "raw_name": str(term.get("raw_name", "")),
        "neighbor_value": term.get("base_value"),
        "query_value": term.get("query_value"),
        "delta_value": term.get("delta_value"),
        "neighbor_value_text": str(term.get("base_value_text", "")),
        "query_value_text": str(term.get("query_value_text", "")),
        "delta_value_text": str(term.get("delta_value_text", "")),
        "observation_text": _term_observation_text(term),
    }


def _build_hidden_signal_payload(
    term: dict[str, Any],
    *,
    label_semantics: dict[int, dict[str, str]],
) -> dict[str, Any]:
    supports_label = int(term["supports_label"])
    return {
        "feature_name": str(term["feature_name"]),
        "contribution": float(term["contribution"]),
        "contribution_abs": float(term["contribution_abs"]),
        "contribution_rank": int(term["contribution_rank"]),
        "supports_label": supports_label,
        "supports_semantics": _label_semantics_text(supports_label, label_semantics),
    }


def _build_neighbor_rewrite_row(
    *,
    neighbor_index: int,
    neighbor_evidence: dict[str, Any],
    neighbor_middle_draft: dict[str, Any],
    label_semantics: dict[int, dict[str, str]],
) -> dict[str, Any]:
    for field_name in ("neighbor_id", "neighbor_smiles", "neighbor_role"):
        if neighbor_evidence.get(field_name) != neighbor_middle_draft.get(field_name):
            raise ValueError(
                f"Neighbor evidence/middle-draft mismatch for {field_name}: "
                f"{neighbor_evidence.get(field_name)!r} != {neighbor_middle_draft.get(field_name)!r}"
            )

    pair_prediction = int(neighbor_evidence["pair_prediction"])
    neighbor_label = int(neighbor_evidence["neighbor_label"])
    top_pair_terms = list(neighbor_evidence.get("top_pair_terms", []))
    middle_draft_text = str(neighbor_middle_draft["middle_draft"])
    return {
        "neighbor_index": int(neighbor_index),
        "neighbor_id": str(neighbor_evidence["neighbor_id"]),
        "neighbor_smiles": str(neighbor_evidence["neighbor_smiles"]),
        "neighbor_role": str(neighbor_evidence["neighbor_role"]),
        "neighbor_label": neighbor_label,
        "neighbor_label_semantics": _label_semantics_text(neighbor_label, label_semantics),
        "neighbor_similarity": float(neighbor_evidence["neighbor_similarity"]),
        "pair_teacher": {
            "pair_model_type": str(neighbor_evidence["pair_model_type"]),
            "pair_score": float(neighbor_evidence["pair_score"]),
            "pair_score_class1_probability": float(neighbor_evidence["pair_score_class1_probability"]),
            "pair_prediction": pair_prediction,
            "pair_prediction_probability": float(neighbor_evidence["pair_prediction_probability"]),
            "pair_prediction_semantics": _label_semantics_text(pair_prediction, label_semantics),
            "teacher_confidence": str(neighbor_evidence["teacher_confidence"]),
            "teacher_confidence_margin": float(neighbor_evidence["teacher_confidence_margin"]),
        },
        "evidence_strength": {
            "feature_probability": float(neighbor_evidence["feature_probability"]),
            "feature_prediction": int(neighbor_evidence["feature_prediction"]),
            "feature_prediction_semantics": _label_semantics_text(
                int(neighbor_evidence["feature_prediction"]),
                label_semantics,
            ),
            "feature_evidence_strength": str(neighbor_evidence["feature_evidence_strength"]),
            "feature_confidence_margin": float(neighbor_evidence["feature_confidence_margin"]),
            "teacher_feature_agreement": bool(neighbor_evidence["teacher_feature_agreement"]),
            "teacher_aligned_evidence_strength": str(neighbor_evidence["teacher_aligned_evidence_strength"]),
            "displayed_feature_prediction": int(neighbor_evidence["displayed_feature_prediction"]),
            "displayed_teacher_agreement": bool(neighbor_evidence["displayed_teacher_agreement"]),
            "displayed_abs_contribution_coverage": float(neighbor_evidence["displayed_abs_contribution_coverage"]),
        },
        "middle_draft": middle_draft_text,
        "tool_visible_observations": [_build_observation_payload(term) for term in top_pair_terms],
        "hidden_teacher_signals": [
            _build_hidden_signal_payload(term, label_semantics=label_semantics) for term in top_pair_terms
        ],
        "middle_draft_reference": {
            "purpose": "legacy_alias_for_middle_draft",
            "text": middle_draft_text,
        },
    }


def _build_per_neighbor_rewrite_input(
    *,
    local_payload: dict[str, Any],
    playbook_text: str,
    label_semantics: dict[int, dict[str, str]],
    task_description: str,
    expected_neighbor_count: int,
) -> dict[str, Any]:
    evidence = dict(local_payload["local_per_neighbor_decision_evidence"])
    middle_drafts = dict(local_payload["local_per_neighbor_middle_draft"])

    rows: list[dict[str, Any]] = []
    neighbor_index = 1
    for group_name in ("positive_neighbors", "negative_neighbors"):
        evidence_rows = list(evidence.get(group_name, []))
        draft_rows = list(middle_drafts.get(group_name, []))
        if len(evidence_rows) != len(draft_rows):
            raise ValueError(
                f"Mismatch for {group_name}: evidence has {len(evidence_rows)} rows, "
                f"middle draft has {len(draft_rows)} rows"
            )
        for neighbor_evidence, neighbor_middle_draft in zip(evidence_rows, draft_rows, strict=True):
            rows.append(
                _build_neighbor_rewrite_row(
                    neighbor_index=neighbor_index,
                    neighbor_evidence=dict(neighbor_evidence),
                    neighbor_middle_draft=dict(neighbor_middle_draft),
                    label_semantics=label_semantics,
                )
            )
            neighbor_index += 1

    if len(rows) != expected_neighbor_count:
        raise ValueError(f"Expected {expected_neighbor_count} per-neighbor rewrite inputs, found {len(rows)}")

    return {
        "task_playbook": playbook_text,
        "task_description": task_description,
        "positive_label_semantics": str(label_semantics[1]["text"]),
        "negative_label_semantics": str(label_semantics[0]["text"]),
        "num_neighbors": int(len(rows)),
        "neighbors": rows,
    }


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
    per_neighbor_rewrite_input = _build_per_neighbor_rewrite_input(
        local_payload=local_payload,
        playbook_text=playbook_text,
        label_semantics=label_semantics,
        task_description=task_description,
        expected_neighbor_count=expected_neighbor_count,
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
        "playbook_path": serialize_project_path(playbook_path),
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
        "local_per_neighbor_rewrite_input": per_neighbor_rewrite_input,
        "hybrid_rewrite_input": {
            "gt_label": int(global_payload["gt_label"]),
            "gt_label_semantics": gt_label_semantics,
        },
        "source_artifacts": {
            "global_evidence_path": serialize_project_path(global_payload["_source_path"]),
            "local_evidence_path": serialize_project_path(local_payload["_source_path"]),
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
    teacher_filter: str = "any_correct",
) -> dict[str, Any]:
    teacher_filter = _validate_teacher_filter(teacher_filter)
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
        keep_for_rewrite = _keep_for_teacher_filter(
            global_correct=global_correct,
            local_correct=local_correct,
            teacher_filter=teacher_filter,
        )
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
            "teacher_filter": teacher_filter,
            "keep_for_rewrite": keep_for_rewrite,
            "drop_reason": _drop_reason_for_filter(
                teacher_case=teacher_case,
                global_correct=global_correct,
                local_correct=local_correct,
                teacher_filter=teacher_filter,
            ),
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
            "output_dir": serialize_project_path(resolved_output_dir),
            "kept_records_path": serialize_project_path(kept_path),
            "dropped_records_path": serialize_project_path(dropped_path),
        }

    manifest = {
        "schema_version": REWRITE_CANDIDATE_SCHEMA_VERSION,
        "candidate_stage": "pre_rewrite_filter_only",
        "task": task_name,
        "split": split_name,
        "global_dir": serialize_project_path(resolve_project_path(global_dir)),
        "local_dir": serialize_project_path(resolve_project_path(local_dir)),
        "teacher_filter": teacher_filter,
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
    allow_missing_playbook: bool = False,
    sample_indices: list[int] | None = None,
    max_samples: int | None = None,
    expected_neighbor_count: int = 6,
    teacher_filter: str = "any_correct",
) -> dict[str, Any]:
    teacher_filter = _validate_teacher_filter(teacher_filter)
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
        global_payload["_source_path"] = serialize_project_path(global_paths[sample_index])
        local_payload["_source_path"] = serialize_project_path(local_paths[sample_index])
        _validate_alignment(global_payload, local_payload)

        task = str(global_payload["task"])
        split = str(global_payload["split"])
        task_name = task if task_name is None else task_name
        split_name = split if split_name is None else split_name
        try:
            playbook_text, playbook_path = load_task_playbook(task, playbook_root=playbook_root)
        except FileNotFoundError:
            if not allow_missing_playbook:
                raise
            playbook_path = (resolve_playbook_root(playbook_root) / f"{task}.md").resolve()
            playbook_text = ""

        global_correct = bool(global_payload["global_prediction_correct"])
        local_correct = bool(local_payload["local_prediction_correct"])
        teacher_case = _teacher_case(global_correct=global_correct, local_correct=local_correct)
        if not _keep_for_teacher_filter(
            global_correct=global_correct,
            local_correct=local_correct,
            teacher_filter=teacher_filter,
        ):
            dropped_records.append(
                {
                    "sample_id": str(global_payload["sample_id"]),
                    "sample_index": int(sample_index),
                    "smiles": str(global_payload["smiles"]),
                    "global_prediction_correct": global_correct,
                    "local_prediction_correct": local_correct,
                    "teacher_case": teacher_case,
                    "teacher_filter": teacher_filter,
                    "drop_reason": _drop_reason_for_filter(
                        teacher_case=teacher_case,
                        global_correct=global_correct,
                        local_correct=local_correct,
                        teacher_filter=teacher_filter,
                    ),
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
        expected_sample_names = {
            f"sample_{int(record['sample_index']):05d}.json" for record in kept_records
        }
        for stale_path in resolved_output_dir.glob("sample_*.json"):
            if stale_path.name not in expected_sample_names:
                stale_path.unlink()
        written_files = []
        for record in kept_records:
            sample_path = resolved_output_dir / f"sample_{int(record['sample_index']):05d}.json"
            save_json(sample_path, record)
            written_files.append(serialize_project_path(sample_path))
        artifact_paths = {
            "output_dir": serialize_project_path(resolved_output_dir),
            "sample_files": written_files,
        }

    manifest = {
        "schema_version": REWRITE_CANDIDATE_SCHEMA_VERSION,
        "candidate_stage": "pre_rewrite_filtered_inputs",
        "task": task_name,
        "split": split_name,
        "global_dir": serialize_project_path(resolve_project_path(global_dir)),
        "local_dir": serialize_project_path(resolve_project_path(local_dir)),
        "allow_missing_playbook": bool(allow_missing_playbook),
        "teacher_filter": teacher_filter,
        "kept_record_count": int(len(kept_records)),
        "dropped_record_count": int(len(dropped_records)),
        "kept_sample_indices": [int(record["sample_index"]) for record in kept_records],
        "dropped_records": dropped_records,
        "artifacts": artifact_paths,
    }
    if resolved_output_dir is not None:
        save_json(resolved_output_dir / "manifest.json", manifest)
    return manifest
