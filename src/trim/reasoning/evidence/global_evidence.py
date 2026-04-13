from __future__ import annotations

import math
from pathlib import Path
import numpy as np
import pandas as pd

from trim.data.datasets import load_tdc_split
from trim.features.preprocessing import transform_feature_frame
from trim.features.table_loader import build_feature_source_bundle
from trim.reasoning.evidence.schemas import GLOBAL_EVIDENCE_STAGE, REASONING_SCHEMA_VERSION
from trim.reasoning.semantics import build_feature_semantics_map, load_task_label_semantics
from trim.utils.io import load_pickle, save_json
from trim.utils.paths import DEFAULT_PROCESSED_DATA_ROOT, OUTPUTS_ROOT


def _format_number(value: object, *, decimals: int = 4) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)

    if math.isnan(numeric):
        return "nan"
    if math.isinf(numeric):
        return "inf" if numeric > 0 else "-inf"
    formatted = f"{numeric:.{decimals}f}".rstrip("0").rstrip(".")
    return "0" if formatted == "-0" else formatted


def _safe_float(value: object) -> float | None:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(numeric) or math.isinf(numeric):
        return None
    return numeric


def _default_label_semantics() -> dict[int, dict[str, str]]:
    return {
        0: {"option": "A", "text": "label 0"},
        1: {"option": "B", "text": "label 1"},
    }


def _resolve_label_semantics(task: str, prompt_root: str | Path | None = None) -> dict[int, dict[str, str]]:
    loaded = load_task_label_semantics(task, prompt_root=prompt_root)
    if loaded is None:
        return _default_label_semantics()
    payload = _default_label_semantics()
    payload.update(loaded)
    return payload


def _label_payload(label: int, label_semantics: dict[int, dict[str, str]]) -> dict[str, object]:
    resolved = dict(label_semantics.get(int(label), {}))
    resolved.setdefault("option", "B" if int(label) == 1 else "A")
    resolved.setdefault("text", f"label {int(label)}")
    resolved["label"] = int(label)
    return resolved


def _supports_prediction(contribution: float, predicted_label: int) -> bool:
    if predicted_label == 1:
        return contribution >= 0.0
    return contribution <= 0.0


def _infer_value_phrase(raw_value: object, semantics: dict[str, str]) -> str:
    numeric = _safe_float(raw_value)
    if numeric is None:
        return f"value {raw_value}"

    raw_name = semantics.get("raw_name", "")
    source_family = semantics.get("source_family", "")
    integer_like = abs(numeric - round(numeric)) < 1e-9
    bool_like = integer_like and round(numeric) in {0, 1}

    if raw_name.startswith(("has_", "is_", "warning_")) or (bool_like and source_family in {"fg_top_level", "pka"}):
        return "present (1)" if round(numeric) == 1 else "absent (0)"

    if source_family == "fg_top_level" or raw_name.startswith("fr_"):
        if integer_like:
            count = int(round(numeric))
            if count == 0:
                return "absent (0)"
            if count == 1:
                return "present once (1)"
            return f"count {count}"

    if integer_like and abs(numeric) <= 20:
        return f"value {int(round(numeric))}"
    return f"value {_format_number(numeric)}"


def _to_numeric_array(values: list[object] | np.ndarray) -> np.ndarray | None:
    try:
        return np.asarray(values, dtype=float)
    except (TypeError, ValueError):
        return None


def _build_bin_context(detail: dict[str, object], model_input_value: object) -> dict[str, object]:
    numeric_value = _safe_float(model_input_value)
    scores = _to_numeric_array(detail.get("scores", []))
    names = _to_numeric_array(detail.get("names", []))

    if numeric_value is None or scores is None or scores.size == 0 or names is None or names.size == 0:
        return {
            "current_bin_index": None,
            "bin_left": None,
            "bin_right": None,
        }

    if names.size == scores.size + 1:
        current_bin_index = int(np.searchsorted(names, numeric_value, side="right") - 1)
        current_bin_index = max(0, min(current_bin_index, scores.size - 1))
        bin_left = float(names[current_bin_index])
        bin_right = float(names[current_bin_index + 1])
        return {
            "current_bin_index": current_bin_index,
            "bin_left": bin_left,
            "bin_right": bin_right,
        }

    current_bin_index = int(np.argmin(np.abs(names - numeric_value)))
    current_bin_index = max(0, min(current_bin_index, scores.size - 1))
    bin_value = float(names[current_bin_index])
    return {
        "current_bin_index": current_bin_index,
        "bin_left": bin_value,
        "bin_right": bin_value,
    }


def _build_local_trend(
    *,
    detail: dict[str, object],
    model_input_value: object,
    label_semantics: dict[int, dict[str, str]],
) -> dict[str, object]:
    scores = _to_numeric_array(detail.get("scores", []))
    if scores is None or scores.size == 0:
        return {
            "trend_label": "unknown",
            "forward_delta": None,
            "backward_delta": None,
            "text": "Local trend could not be estimated from the EBM term curve.",
        }

    bin_context = _build_bin_context(detail, model_input_value)
    current_bin_index = bin_context["current_bin_index"]
    if current_bin_index is None:
        return {
            "trend_label": "unknown",
            "forward_delta": None,
            "backward_delta": None,
            "text": "Local trend could not be estimated from the EBM term curve.",
        }

    left_index = current_bin_index - 1 if current_bin_index > 0 else None
    right_index = current_bin_index + 1 if current_bin_index < scores.size - 1 else None

    backward_delta = None if left_index is None else float(scores[current_bin_index] - scores[left_index])
    forward_delta = None if right_index is None else float(scores[right_index] - scores[current_bin_index])

    epsilon = 1e-6
    if forward_delta is None and backward_delta is None:
        trend_label = "single_bin"
        text = "This feature only has one learned contribution region in the current model."
    elif forward_delta is None:
        if abs(backward_delta or 0.0) <= epsilon:
            trend_label = "flat_right_boundary"
            text = "Near the upper boundary, the learned contribution is essentially flat."
        elif backward_delta > 0:
            trend_label = "upward_right_boundary"
            text = "Near the upper boundary, larger values have been associated with a more positive contribution."
        else:
            trend_label = "downward_right_boundary"
            text = "Near the upper boundary, larger values have been associated with a more negative contribution."
    elif backward_delta is None:
        if abs(forward_delta) <= epsilon:
            trend_label = "flat_left_boundary"
            text = "Near the lower boundary, the learned contribution is essentially flat."
        elif forward_delta > 0:
            trend_label = "upward_left_boundary"
            text = "Near the lower boundary, increasing this feature makes the contribution more positive."
        else:
            trend_label = "downward_left_boundary"
            text = "Near the lower boundary, increasing this feature makes the contribution more negative."
    else:
        if abs(forward_delta) <= epsilon and abs(backward_delta) <= epsilon:
            trend_label = "flat"
            text = "Near the current value, the learned contribution is nearly flat."
        elif forward_delta > epsilon and backward_delta > -epsilon:
            trend_label = "upward"
            text = "Near the current value, increasing this feature makes the contribution more positive."
        elif forward_delta < -epsilon and backward_delta < epsilon:
            trend_label = "downward"
            text = "Near the current value, increasing this feature makes the contribution more negative."
        else:
            trend_label = "mixed"
            text = "Near the current value, the learned contribution is locally mixed rather than monotonic."

    label_if_up = _label_payload(1, label_semantics)
    label_if_down = _label_payload(0, label_semantics)
    if trend_label.startswith("upward"):
        text = f"{text} That nearby direction favors option ({label_if_up['option']}): {label_if_up['text']}."
    elif trend_label.startswith("downward"):
        text = f"{text} That nearby direction favors option ({label_if_down['option']}): {label_if_down['text']}."

    return {
        "trend_label": trend_label,
        "forward_delta": forward_delta,
        "backward_delta": backward_delta,
        "text": text,
    }


def _build_text_hint(
    *,
    display_name: str,
    value_phrase: str,
    contribution: float,
    contribution_label: dict[str, object],
    trend_text: str | None = None,
) -> str:
    contribution_text = _format_number(contribution, decimals=4)
    hint = (
        f"{display_name} is {value_phrase}. "
        f"At this value the global EBM contribution is {contribution_text}, "
        f"which pushes toward option ({contribution_label['option']}): {contribution_label['text']}."
    )
    if trend_text:
        hint = f"{hint} {trend_text}"
    return hint


def _build_global_middle_draft(
    *,
    top_features: list[dict[str, object]],
    predicted_label: int,
    predicted_score: float,
    label_semantics: dict[int, dict[str, str]],
    include_intro: bool,
) -> str:
    transition_words = ["First", "Next", "Then", "After that", "Finally"]
    predicted_label_payload = _label_payload(predicted_label, label_semantics)

    if include_intro and top_features:
        top_feature_text = ", ".join(
            str(feature["display_name"])
            for feature in top_features[:3]
        )
        intro_clause = (
            f"This global reasoning repeatedly relies on important features such as {top_feature_text}."
        )
    elif include_intro:
        intro_clause = "This global reasoning is driven by the ranked feature evidence below."
    else:
        intro_clause = ""

    if top_features:
        step_clauses = []
        for step_index, feature in enumerate(top_features):
            transition = (
                transition_words[step_index]
                if step_index < len(transition_words)
                else f"Step {step_index + 1}"
            )
            step_statement = str(feature["text_hint"]).rstrip()
            if step_statement.endswith("."):
                step_statement = step_statement[:-1]
            step_clauses.append(f"{transition}, {step_statement}.")
        detail_clause = " ".join(step_clauses)
    else:
        detail_clause = "No ranked global feature evidence was available for this sample."

    conclusion_clause = (
        f"Taken together, these global descriptor-level signals make the model predict option "
        f"({predicted_label_payload['option']}): {predicted_label_payload['text']} with score "
        f"{_format_number(predicted_score)}."
    )
    clauses = [clause for clause in [intro_clause, detail_clause, conclusion_clause] if clause]
    return " ".join(clauses)


def _build_feature_evidence(
    *,
    feature_name: str,
    semantics: dict[str, str],
    raw_value: object,
    model_input_value: object,
    contribution: float,
    contribution_rank: int,
    predicted_label: int,
    label_semantics: dict[int, dict[str, str]],
    global_explanation,
    term_index: int,
    include_local_trend: bool,
) -> dict[str, object]:
    contribution_label = _label_payload(1 if contribution >= 0.0 else 0, label_semantics)
    detail = global_explanation.data(term_index)
    trend = None
    if include_local_trend:
        trend = _build_local_trend(
            detail=detail,
            model_input_value=model_input_value,
            label_semantics=label_semantics,
        )
    bin_context = _build_bin_context(detail, model_input_value)
    value_phrase = _infer_value_phrase(raw_value, semantics)

    payload = {
        **semantics,
        "feature_value": raw_value,
        "feature_value_text": value_phrase,
        "model_input_value": model_input_value,
        "contribution": float(contribution),
        "contribution_abs": float(abs(contribution)),
        "contribution_rank": int(contribution_rank),
        "supports_prediction": _supports_prediction(contribution, predicted_label),
        "supports_label": int(contribution_label["label"]),
        "supports_option": str(contribution_label["option"]),
        "supports_text": str(contribution_label["text"]),
        "current_bin_index": bin_context["current_bin_index"],
        "bin_left": bin_context["bin_left"],
        "bin_right": bin_context["bin_right"],
        "text_hint": _build_text_hint(
            display_name=semantics["display_name"],
            value_phrase=value_phrase,
            contribution=contribution,
            contribution_label=contribution_label,
        ),
    }
    if trend is not None:
        payload["local_trend"] = trend
    return payload


def _extract_base_contribution(model) -> float | None:
    intercept = getattr(model, "intercept_", None)
    if intercept is None:
        return None
    try:
        intercept_array = np.asarray(intercept, dtype=float).reshape(-1)
    except (TypeError, ValueError):
        return None
    if intercept_array.size == 0:
        return None
    return float(intercept_array[0])


def _build_sample_payload(
    *,
    bundle: dict[str, object],
    sample_index: int,
    split: str,
    smiles: str,
    gt_label: int,
    predicted_label: int,
    global_score: float,
    raw_row: pd.Series,
    transformed_row: pd.Series,
    term_contributions: np.ndarray,
    global_explanation,
    label_semantics: dict[int, dict[str, str]],
    feature_semantics_map: dict[str, dict[str, str]],
    top_k: int,
    include_local_trend: bool,
    include_intro: bool,
) -> dict[str, object]:
    feature_columns = list(bundle["feature_columns"])
    non_nan_indices = [index for index, value in enumerate(term_contributions) if not math.isnan(float(value))]
    ranked_indices = sorted(non_nan_indices, key=lambda index: abs(float(term_contributions[index])), reverse=True)
    selected_indices = ranked_indices[:top_k]

    top_features = []
    for rank, term_index in enumerate(selected_indices, start=1):
        feature_name = feature_columns[term_index]
        top_features.append(
            _build_feature_evidence(
                feature_name=feature_name,
                semantics=feature_semantics_map[feature_name],
                raw_value=raw_row[feature_name],
                model_input_value=transformed_row[feature_name],
                contribution=float(term_contributions[term_index]),
                contribution_rank=rank,
                predicted_label=predicted_label,
                label_semantics=label_semantics,
                global_explanation=global_explanation,
                term_index=term_index,
                include_local_trend=include_local_trend,
            )
        )

    predicted_semantics = _label_payload(predicted_label, label_semantics)
    gt_semantics = _label_payload(gt_label, label_semantics)
    score_for_prediction = global_score if predicted_label == 1 else 1.0 - global_score

    supporting_features = [feature for feature in top_features if feature["supports_prediction"]]
    caution_features = [feature for feature in top_features if not feature["supports_prediction"]]
    supporting_feature_names = [str(feature["display_name"]) for feature in supporting_features]
    caution_feature_names = [str(feature["display_name"]) for feature in caution_features]

    return {
        "schema_version": REASONING_SCHEMA_VERSION,
        "evidence_stage": GLOBAL_EVIDENCE_STAGE,
        "sample_id": f"{split}_sample_{sample_index}",
        "sample_index": int(sample_index),
        "task": str(bundle["task"]),
        "split": split,
        "smiles": smiles,
        "gt_label": int(gt_label),
        "gt_label_semantics": gt_semantics,
        "global_prediction": int(predicted_label),
        "global_prediction_semantics": predicted_semantics,
        "global_prediction_correct": int(predicted_label) == int(gt_label),
        "global_score": float(global_score),
        "global_score_for_prediction": float(score_for_prediction),
        "keep_for_reasoning": True,
        "drop_reason": None,
        "global_decision_evidence": {
            "model_type": str(bundle["model_type"]),
            "feature_set_name": str(bundle["feature_set_name"]),
            "num_total_terms": int(len(feature_columns)),
            "num_nonzero_terms": int(sum(abs(float(value)) > 0.0 for value in term_contributions)),
            "base_contribution": _extract_base_contribution(bundle["model"]),
            "top_k": int(top_k),
            "supporting_feature_count": int(len(supporting_features)),
            "caution_feature_count": int(len(caution_features)),
            "supporting_feature_names": supporting_feature_names,
            "caution_feature_names": caution_feature_names,
            "top_features": top_features,
        },
        "global_middle_draft": _build_global_middle_draft(
            top_features=top_features,
            predicted_label=predicted_label,
            predicted_score=score_for_prediction,
            label_semantics=label_semantics,
            include_intro=include_intro,
        ),
    }


def build_default_global_evidence_output_dir(
    *,
    bundle_path: str | Path,
    split: str,
    output_root: str | Path = OUTPUTS_ROOT / "reasoning_evidence" / "global",
) -> Path:
    bundle_path = Path(bundle_path)
    feature_set_name = bundle_path.parent.name
    task = bundle_path.parent.parent.name
    experiment_name = bundle_path.parent.parent.parent.name
    return Path(output_root) / experiment_name / task / feature_set_name / split


def extract_global_evidence_for_split(
    *,
    bundle_path: str | Path,
    split: str,
    dataset_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT,
    top_k: int = 10,
    sample_indices: list[int] | None = None,
    max_samples: int | None = None,
    prompt_root: str | Path | None = None,
    output_dir: str | Path | None = None,
    include_local_trend: bool = False,
    include_intro: bool = False,
) -> dict[str, object]:
    bundle_path = Path(bundle_path)
    bundle = load_pickle(bundle_path)
    feature_bundle = build_feature_source_bundle(bundle["feature_config_paths"])
    task = str(bundle["task"])
    label_semantics = _resolve_label_semantics(task, prompt_root=prompt_root)

    task_split = load_tdc_split(task, split, data_root=dataset_root)
    raw_feature_df = feature_bundle["feature_source"].load(task_split.smiles)
    aligned_df, transformed_df = transform_feature_frame(raw_feature_df, bundle["preprocessor"])

    model = bundle["model"]
    x_matrix = transformed_df.to_numpy()
    global_scores = model.predict_proba(x_matrix)[:, 1]
    global_predictions = model.predict(x_matrix)
    term_contribution_matrix = np.asarray(model.eval_terms(x_matrix), dtype=float)
    global_explanation = model.explain_global()
    feature_semantics_map = build_feature_semantics_map(list(bundle["feature_columns"]))

    available_indices = list(range(len(task_split.smiles)))
    if sample_indices is not None:
        requested = [int(index) for index in sample_indices]
        available_set = set(available_indices)
        missing = [index for index in requested if index not in available_set]
        if missing:
            raise IndexError(f"Sample indices out of range for split {split}: {missing}")
        target_indices = requested
    else:
        target_indices = available_indices

    if max_samples is not None:
        target_indices = target_indices[: int(max_samples)]

    records = []
    for sample_index in target_indices:
        record = _build_sample_payload(
            bundle=bundle,
            sample_index=sample_index,
            split=split,
            smiles=task_split.smiles[sample_index],
            gt_label=int(task_split.labels[sample_index]),
            predicted_label=int(global_predictions[sample_index]),
            global_score=float(global_scores[sample_index]),
            raw_row=aligned_df.iloc[sample_index],
            transformed_row=transformed_df.iloc[sample_index],
            term_contributions=term_contribution_matrix[sample_index],
            global_explanation=global_explanation,
            label_semantics=label_semantics,
            feature_semantics_map=feature_semantics_map,
            top_k=top_k,
            include_local_trend=include_local_trend,
            include_intro=include_intro,
        )
        records.append(record)

    artifact_paths: dict[str, object] = {}
    if output_dir is not None:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        for record in records:
            sample_path = output_path / f"sample_{int(record['sample_index']):05d}.json"
            save_json(sample_path, record)
        artifact_paths["output_dir"] = str(output_path.resolve())

    return {
        "schema_version": REASONING_SCHEMA_VERSION,
        "evidence_stage": GLOBAL_EVIDENCE_STAGE,
        "task": task,
        "split": split,
        "bundle_path": str(bundle_path.resolve()),
        "dataset_root": str(Path(dataset_root).resolve()),
        "feature_set_name": str(bundle["feature_set_name"]),
        "num_records": int(len(records)),
        "sample_indices": [int(record["sample_index"]) for record in records],
        "records": records,
        "artifacts": artifact_paths,
    }
