from __future__ import annotations

import hashlib
import math
from pathlib import Path
import random

import numpy as np

from trim.data.datasets import load_tdc_split
from trim.features.pair_features import build_pair_matrix, coerce_numeric_feature_frame
from trim.features.table_loader import build_feature_source_bundle
from trim.models.aggregation import aggregate_local_scores
from trim.models.retrieval import CachedSimilarityRetriever, NeighborRecord
from trim.reasoning.evidence.global_evidence import (
    _build_ranked_evidence_detail_clause,
    _format_number,
    _infer_value_phrase,
    _label_payload,
    _missing_value_reason,
    _resolve_label_semantics,
    _sanitize_json_value,
)
from trim.reasoning.evidence.schemas import REASONING_SCHEMA_VERSION
from trim.reasoning.semantics import build_feature_semantics_map
from trim.utils.io import load_pickle, save_json
from trim.utils.paths import (
    DEFAULT_PROCESSED_DATA_ROOT,
    DEFAULT_SIMILARITY_CACHE_ROOT,
    OUTPUTS_ROOT,
    serialize_project_path,
)


LOCAL_EVIDENCE_STAGE = "local_evidence_only"
DEFAULT_TOP_TERM_K_PER_NEIGHBOR = 8
DEFAULT_RANDOM_TOP_TERM_MIN = 3
DEFAULT_RANDOM_TOP_TERM_MAX = 6
LOCAL_TERM_SELECTION_MODES = ("ranked_top_k", "random_k_ranked", "top_k_shuffled")


def _validate_term_selection_config(
    *,
    top_term_k: int,
    term_selection_mode: str,
    random_top_term_min: int,
    random_top_term_max: int,
) -> None:
    if term_selection_mode not in LOCAL_TERM_SELECTION_MODES:
        raise ValueError(
            f"Unsupported term_selection_mode={term_selection_mode!r}; "
            f"expected one of {LOCAL_TERM_SELECTION_MODES}"
        )
    if int(top_term_k) < 1:
        raise ValueError(f"top_term_k must be >= 1, got {top_term_k}")
    if int(random_top_term_min) < 1:
        raise ValueError(f"random_top_term_min must be >= 1, got {random_top_term_min}")
    if int(random_top_term_max) < int(random_top_term_min):
        raise ValueError(
            "random_top_term_max must be >= random_top_term_min, got "
            f"{random_top_term_max} < {random_top_term_min}"
        )


def _stable_rng(*, random_seed: int, parts: list[object]) -> random.Random:
    payload = "|".join([str(int(random_seed)), *(str(part) for part in parts)])
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    seed = int.from_bytes(digest[:8], byteorder="big", signed=False)
    return random.Random(seed)


def _select_pair_term_indices(
    *,
    ranked_indices: list[int],
    top_term_k: int,
    term_selection_mode: str,
    random_top_term_min: int,
    random_top_term_max: int,
    rng: random.Random | None,
) -> tuple[list[int], dict[str, object]]:
    if term_selection_mode == "ranked_top_k":
        return ranked_indices[: int(top_term_k)], {
            "mode": term_selection_mode,
            "requested_top_term_k": int(top_term_k),
            "selected_term_count": int(min(len(ranked_indices), int(top_term_k))),
        }

    if rng is None:
        raise ValueError(f"term_selection_mode={term_selection_mode!r} requires a deterministic RNG")

    if term_selection_mode == "random_k_ranked":
        requested_count = rng.randint(int(random_top_term_min), int(random_top_term_max))
        selected = ranked_indices[:requested_count]
        return selected, {
            "mode": term_selection_mode,
            "requested_min_terms": int(random_top_term_min),
            "requested_max_terms": int(random_top_term_max),
            "sampled_term_count": int(requested_count),
            "selected_term_count": int(len(selected)),
            "preserves_ranked_order": True,
        }

    if term_selection_mode == "top_k_shuffled":
        selected = list(ranked_indices[: int(top_term_k)])
        rng.shuffle(selected)
        return selected, {
            "mode": term_selection_mode,
            "requested_top_term_k": int(top_term_k),
            "selected_term_count": int(len(selected)),
            "preserves_ranked_order": False,
        }

    raise ValueError(f"Unsupported term_selection_mode={term_selection_mode!r}")


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def _delta_text(value: object) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(numeric):
        return "nan"
    return f"{numeric:+.4f}".rstrip("0").rstrip(".")


def _pair_model_type(neighbor_label: int) -> str:
    return "positive_neighbor_model" if int(neighbor_label) == 1 else "negative_neighbor_model"


def _neighbor_role(neighbor_label: int) -> str:
    return "positive_neighbor" if int(neighbor_label) == 1 else "negative_neighbor"


def _pair_prediction_probability(pair_score: float, pair_prediction: int) -> float:
    score = float(pair_score)
    if int(pair_prediction) == 1:
        return score
    return 1.0 - score


def _confidence_level(margin: float) -> str:
    margin = float(margin)
    if margin <= 0.1:
        return "low"
    if margin <= 0.3:
        return "medium"
    return "high"


def _strength_adverb(strength: str) -> str:
    if strength == "high":
        return "strongly"
    if strength == "medium":
        return "moderately"
    return "weakly"


def _semantic_label_reference(label: int, label_semantics: dict[int, dict[str, str]], *, plural: bool = False) -> str:
    label_payload = _label_payload(int(label), label_semantics)
    noun = "neighbors" if plural else "a neighbor"
    return f"{noun} labeled option ({label_payload['option']}): {label_payload['text']}"


def _term_sum_payload(term_contributions: np.ndarray, label_semantics: dict[int, dict[str, str]]) -> dict[str, object]:
    finite_terms = [float(value) for value in term_contributions if not math.isnan(float(value))]
    feature_logit = float(sum(finite_terms))
    feature_probability = _sigmoid(feature_logit)
    feature_prediction = 1 if feature_probability >= 0.5 else 0
    feature_margin = abs(feature_probability - 0.5)
    return {
        "feature_logit": feature_logit,
        "feature_probability": feature_probability,
        "feature_prediction": int(feature_prediction),
        "feature_prediction_semantics": _label_payload(feature_prediction, label_semantics),
        "feature_confidence_margin": float(feature_margin),
        "feature_evidence_strength": _confidence_level(feature_margin),
        "total_abs_feature_contribution": float(sum(abs(value) for value in finite_terms)),
    }


def _displayed_term_sum_payload(
    top_pair_terms: list[dict[str, object]],
    total_abs_feature_contribution: float,
    label_semantics: dict[int, dict[str, str]],
) -> dict[str, object]:
    displayed_terms = [float(term["contribution"]) for term in top_pair_terms]
    displayed_logit = float(sum(displayed_terms))
    displayed_probability = _sigmoid(displayed_logit)
    displayed_prediction = 1 if displayed_probability >= 0.5 else 0
    displayed_margin = abs(displayed_probability - 0.5)
    displayed_abs_contribution = float(sum(abs(value) for value in displayed_terms))
    if total_abs_feature_contribution > 0.0:
        displayed_coverage = displayed_abs_contribution / total_abs_feature_contribution
    else:
        displayed_coverage = 0.0
    return {
        "displayed_feature_logit": displayed_logit,
        "displayed_feature_probability": displayed_probability,
        "displayed_feature_prediction": int(displayed_prediction),
        "displayed_feature_prediction_semantics": _label_payload(displayed_prediction, label_semantics),
        "displayed_feature_confidence_margin": float(displayed_margin),
        "displayed_feature_evidence_strength": _confidence_level(displayed_margin),
        "displayed_abs_feature_contribution": displayed_abs_contribution,
        "displayed_abs_contribution_coverage": float(displayed_coverage),
    }


def _render_pair_observed_value(value_text: str) -> str:
    stripped = str(value_text).strip()
    if stripped.startswith(("value ", "count ", "present", "absent")):
        return stripped
    return f"value {stripped}"


def _pair_entity_value_clause(*, entity_name: str, feature_display_name: str, value_text: str) -> str:
    if value_text == "no acidic site":
        return f"the {entity_name} has no acidic site"
    if value_text == "no basic site":
        return f"the {entity_name} has no basic site"
    if value_text == "missing value":
        return f"{feature_display_name} is unavailable for the {entity_name}"
    return f"the {entity_name}'s {feature_display_name} is {_render_pair_observed_value(value_text)}"


def _delta_value_payload(
    *,
    base_value: object,
    query_value: object,
    semantics: dict[str, str],
) -> tuple[object, str, str | None]:
    base_reason = _missing_value_reason(base_value, semantics)
    query_reason = _missing_value_reason(query_value, semantics)
    if base_reason is None and query_reason is None:
        delta_value = float(query_value) - float(base_value)
        return delta_value, _delta_text(delta_value), None

    if base_reason == "no_acidic_site" and query_reason == "no_acidic_site":
        return None, "not defined because neither molecule has an acidic site", "no_acidic_site"
    if base_reason == "no_basic_site" and query_reason == "no_basic_site":
        return None, "not defined because neither molecule has a basic site", "no_basic_site"
    if base_reason == "no_acidic_site" or query_reason == "no_acidic_site":
        return None, "not defined because one molecule has no acidic site", "no_acidic_site"
    if base_reason == "no_basic_site" or query_reason == "no_basic_site":
        return None, "not defined because one molecule has no basic site", "no_basic_site"
    return None, "not defined because one side has no available value", "missing_value"


def _build_pair_term_text_hint(
    *,
    semantics: dict[str, str],
    feature_display_name: str,
    base_value_text: str,
    query_value_text: str,
    base_value: object,
    query_value: object,
    delta_value: object,
    contribution: float,
    contribution_label: dict[str, object],
) -> str:
    source_family = semantics.get("source_family", "")
    delta_value_export, delta_value_text, _ = _delta_value_payload(
        base_value=base_value,
        query_value=query_value,
        semantics=semantics,
    )
    if source_family == "fg_top_level":
        try:
            neighbor_count = int(round(float(base_value)))
            query_count = int(round(float(query_value)))
        except (TypeError, ValueError):
            neighbor_count = None
            query_count = None

        if neighbor_count is not None and query_count is not None:
            if neighbor_count == 0 and query_count == 0:
                comparison_text = f"Neither the neighbor nor the query has {feature_display_name}"
            elif neighbor_count == 0 and query_count == 1:
                comparison_text = f"The neighbor does not have {feature_display_name}, while the query has it once"
            elif neighbor_count == 1 and query_count == 0:
                comparison_text = f"The neighbor has {feature_display_name}, while the query does not"
            elif neighbor_count == 1 and query_count == 1:
                comparison_text = f"Both the neighbor and the query have {feature_display_name}"
            else:
                comparison_text = (
                    f"The neighbor has {neighbor_count} copies of {feature_display_name}, while the query has "
                    f"{query_count}"
                )
            return (
                f"{comparison_text} (query-minus-neighbor delta {delta_value_text}). "
                f"This pairwise contribution is {_format_number(contribution, decimals=4)}, which pushes toward "
                f"option ({contribution_label['option']}): {contribution_label['text']}."
            )

    neighbor_clause = _pair_entity_value_clause(
        entity_name="neighbor",
        feature_display_name=feature_display_name,
        value_text=base_value_text,
    )
    query_clause = _pair_entity_value_clause(
        entity_name="query",
        feature_display_name=feature_display_name,
        value_text=query_value_text,
    )
    if delta_value_export is None:
        delta_clause = f"The query-minus-neighbor delta is {delta_value_text}"
    else:
        delta_clause = f"The query-minus-neighbor delta is {delta_value_text}"
    return (
        f"For {feature_display_name}, {neighbor_clause}, while {query_clause}. {delta_clause}. "
        f"This pairwise contribution is "
        f"{_format_number(contribution, decimals=4)}, which pushes toward option ({contribution_label['option']}): "
        f"{contribution_label['text']}."
    )


def _extract_top_pair_terms(
    *,
    raw_feature_columns: list[str],
    feature_semantics_map: dict[str, dict[str, str]],
    query_raw_row,
    neighbor_raw_row,
    term_contributions: np.ndarray,
    label_semantics: dict[int, dict[str, str]],
    top_term_k: int,
    term_selection_mode: str,
    random_top_term_min: int,
    random_top_term_max: int,
    rng: random.Random | None,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    non_nan_indices = [index for index, value in enumerate(term_contributions) if not math.isnan(float(value))]
    ranked_indices = sorted(non_nan_indices, key=lambda index: abs(float(term_contributions[index])), reverse=True)
    rank_by_index = {term_index: rank for rank, term_index in enumerate(ranked_indices, start=1)}
    selected_indices, selection_payload = _select_pair_term_indices(
        ranked_indices=ranked_indices,
        top_term_k=top_term_k,
        term_selection_mode=term_selection_mode,
        random_top_term_min=random_top_term_min,
        random_top_term_max=random_top_term_max,
        rng=rng,
    )

    terms: list[dict[str, object]] = []
    for display_order, term_index in enumerate(selected_indices, start=1):
        raw_feature_name = raw_feature_columns[term_index]
        semantics = feature_semantics_map[raw_feature_name]
        base_value = neighbor_raw_row[raw_feature_name]
        query_value = query_raw_row[raw_feature_name]
        delta_value, delta_value_text, delta_missing_reason = _delta_value_payload(
            base_value=base_value,
            query_value=query_value,
            semantics=semantics,
        )
        contribution = float(term_contributions[term_index])
        contribution_label = _label_payload(1 if contribution >= 0.0 else 0, label_semantics)
        base_value_text = _infer_value_phrase(base_value, semantics)
        query_value_text = _infer_value_phrase(query_value, semantics)

        term_payload = {
            **semantics,
            "feature_name": raw_feature_name,
            "base_value": _sanitize_json_value(base_value),
            "query_value": _sanitize_json_value(query_value),
            "delta_value": delta_value,
            "base_value_text": base_value_text,
            "query_value_text": query_value_text,
            "delta_value_text": delta_value_text,
            "contribution": contribution,
            "contribution_abs": float(abs(contribution)),
            "contribution_rank": int(rank_by_index[term_index]),
            "display_order": int(display_order),
            "supports_label": int(contribution_label["label"]),
            "supports_option": str(contribution_label["option"]),
            "supports_text": str(contribution_label["text"]),
            "text_hint": _build_pair_term_text_hint(
                semantics=semantics,
                feature_display_name=semantics["display_name"],
                base_value_text=base_value_text,
                query_value_text=query_value_text,
                base_value=base_value,
                query_value=query_value,
                delta_value=delta_value,
                contribution=contribution,
                contribution_label=contribution_label,
            ),
        }
        base_missing_reason = _missing_value_reason(base_value, semantics)
        query_missing_reason = _missing_value_reason(query_value, semantics)
        if base_missing_reason is not None:
            term_payload["base_value_missing_reason"] = base_missing_reason
        if query_missing_reason is not None:
            term_payload["query_value_missing_reason"] = query_missing_reason
        if delta_missing_reason is not None:
            term_payload["delta_value_missing_reason"] = delta_missing_reason
        terms.append(term_payload)
    selection_payload["available_non_nan_term_count"] = int(len(ranked_indices))
    return terms, selection_payload


def _build_neighbor_evidence(
    *,
    query_smiles: str,
    query_label: int,
    neighbor: NeighborRecord,
    pair_score: float,
    query_raw_row,
    neighbor_raw_row,
    term_contributions: np.ndarray,
    raw_feature_columns: list[str],
    feature_semantics_map: dict[str, dict[str, str]],
    label_semantics: dict[int, dict[str, str]],
    top_term_k: int,
    term_selection_mode: str,
    random_top_term_min: int,
    random_top_term_max: int,
    term_selection_rng: random.Random | None,
) -> dict[str, object]:
    pair_model_type = _pair_model_type(neighbor.label)
    pair_prediction = 1 if pair_score >= 0.5 else 0
    pair_prediction_probability = _pair_prediction_probability(pair_score, pair_prediction)
    teacher_confidence_margin = abs(pair_prediction_probability - 0.5)
    term_payload = _term_sum_payload(term_contributions, label_semantics)
    top_pair_terms, term_selection_payload = _extract_top_pair_terms(
        raw_feature_columns=raw_feature_columns,
        feature_semantics_map=feature_semantics_map,
        query_raw_row=query_raw_row,
        neighbor_raw_row=neighbor_raw_row,
        term_contributions=term_contributions,
        label_semantics=label_semantics,
        top_term_k=top_term_k,
        term_selection_mode=term_selection_mode,
        random_top_term_min=random_top_term_min,
        random_top_term_max=random_top_term_max,
        rng=term_selection_rng,
    )
    displayed_payload = _displayed_term_sum_payload(
        top_pair_terms=top_pair_terms,
        total_abs_feature_contribution=float(term_payload["total_abs_feature_contribution"]),
        label_semantics=label_semantics,
    )
    teacher_feature_agreement = int(pair_prediction) == int(term_payload["feature_prediction"])
    displayed_teacher_agreement = int(pair_prediction) == int(displayed_payload["displayed_feature_prediction"])
    teacher_aligned_evidence_strength = (
        str(term_payload["feature_evidence_strength"])
        if teacher_feature_agreement and displayed_teacher_agreement
        else "low"
    )
    return {
        "neighbor_id": neighbor.smiles,
        "query_smiles": query_smiles,
        "query_label": int(query_label),
        "neighbor_smiles": neighbor.smiles,
        "neighbor_label": int(neighbor.label),
        "neighbor_similarity": float(neighbor.similarity),
        "neighbor_scaffold": str(neighbor.scaffold),
        "neighbor_role": _neighbor_role(neighbor.label),
        "pair_model_type": pair_model_type,
        "pair_score": float(pair_score),
        "pair_score_class1_probability": float(pair_score),
        "pair_prediction": int(pair_prediction),
        "pair_prediction_probability": pair_prediction_probability,
        "teacher_confidence_margin": float(teacher_confidence_margin),
        "teacher_confidence": _confidence_level(teacher_confidence_margin),
        "pair_prediction_semantics": _label_payload(pair_prediction, label_semantics),
        **term_payload,
        "teacher_feature_agreement": bool(teacher_feature_agreement),
        "teacher_aligned_evidence_strength": teacher_aligned_evidence_strength,
        **displayed_payload,
        "displayed_teacher_agreement": bool(displayed_teacher_agreement),
        "term_selection": term_selection_payload,
        "top_pair_terms": top_pair_terms,
    }


def _build_neighbor_middle_draft(
    *,
    neighbor_evidence: dict[str, object],
    label_semantics: dict[int, dict[str, str]],
) -> dict[str, object]:
    top_pair_terms = list(neighbor_evidence.get("top_pair_terms", []))
    pair_prediction = int(neighbor_evidence["pair_prediction"])
    pair_score = float(neighbor_evidence["pair_score"])
    pair_prediction_probability = _pair_prediction_probability(pair_score, pair_prediction)
    predicted_label_payload = _label_payload(pair_prediction, label_semantics)

    detail_clause = _build_ranked_evidence_detail_clause(
        evidence_items=top_pair_terms,
        no_evidence_text="No ranked pair-term evidence was available for this neighbor comparison.",
    )

    conclusion_clause = _build_neighbor_conclusion_clause(
        neighbor_evidence=neighbor_evidence,
        label_semantics=label_semantics,
    )

    return {
        "neighbor_id": neighbor_evidence["neighbor_id"],
        "neighbor_smiles": neighbor_evidence["neighbor_smiles"],
        "neighbor_role": neighbor_evidence["neighbor_role"],
        "pair_model_type": neighbor_evidence["pair_model_type"],
        "pair_score": pair_score,
        "pair_score_class1_probability": pair_score,
        "pair_prediction": pair_prediction,
        "pair_prediction_probability": pair_prediction_probability,
        "teacher_confidence_margin": float(neighbor_evidence["teacher_confidence_margin"]),
        "teacher_confidence": neighbor_evidence["teacher_confidence"],
        "pair_prediction_semantics": predicted_label_payload,
        "feature_logit": float(neighbor_evidence["feature_logit"]),
        "feature_probability": float(neighbor_evidence["feature_probability"]),
        "feature_prediction": int(neighbor_evidence["feature_prediction"]),
        "feature_prediction_semantics": dict(neighbor_evidence["feature_prediction_semantics"]),
        "feature_confidence_margin": float(neighbor_evidence["feature_confidence_margin"]),
        "feature_evidence_strength": neighbor_evidence["feature_evidence_strength"],
        "teacher_feature_agreement": bool(neighbor_evidence["teacher_feature_agreement"]),
        "teacher_aligned_evidence_strength": neighbor_evidence["teacher_aligned_evidence_strength"],
        "displayed_feature_logit": float(neighbor_evidence["displayed_feature_logit"]),
        "displayed_feature_probability": float(neighbor_evidence["displayed_feature_probability"]),
        "displayed_feature_prediction": int(neighbor_evidence["displayed_feature_prediction"]),
        "displayed_feature_prediction_semantics": dict(
            neighbor_evidence["displayed_feature_prediction_semantics"]
        ),
        "displayed_feature_confidence_margin": float(neighbor_evidence["displayed_feature_confidence_margin"]),
        "displayed_feature_evidence_strength": neighbor_evidence["displayed_feature_evidence_strength"],
        "displayed_abs_contribution_coverage": float(neighbor_evidence["displayed_abs_contribution_coverage"]),
        "displayed_teacher_agreement": bool(neighbor_evidence["displayed_teacher_agreement"]),
        "middle_draft": f"{detail_clause} {conclusion_clause}",
    }


def _resolve_raw_feature_columns(model_bundle: dict[str, object]) -> list[str]:
    pair_columns = [str(column) for column in model_bundle.get("pair_columns", [])]
    if pair_columns:
        base_columns = [column.removesuffix("__base") for column in pair_columns[0::2]]
        if all(base_columns):
            return base_columns
    return [str(column) for column in model_bundle["raw_feature_columns"]]


def _option_clause(label_payload: dict[str, object]) -> str:
    return f"option ({label_payload['option']}): {label_payload['text']}"


def _build_neighbor_conclusion_clause(
    *,
    neighbor_evidence: dict[str, object],
    label_semantics: dict[int, dict[str, str]],
) -> str:
    pair_prediction = int(neighbor_evidence["pair_prediction"])
    feature_prediction = int(neighbor_evidence["feature_prediction"])
    displayed_prediction = int(neighbor_evidence["displayed_feature_prediction"])

    pair_payload = _label_payload(pair_prediction, label_semantics)
    neighbor_label_reference = _semantic_label_reference(
        int(neighbor_evidence["neighbor_label"]),
        label_semantics,
    )

    feature_strength = str(neighbor_evidence["feature_evidence_strength"])
    teacher_aligned_strength = str(neighbor_evidence["teacher_aligned_evidence_strength"])
    feature_adverb = _strength_adverb(feature_strength)

    if feature_prediction != pair_prediction:
        return (
            f"Taken together, relative to {neighbor_label_reference}, these feature comparisons do not align cleanly "
            f"with {_option_clause(pair_payload)}. This neighbor should be treated only as "
            f"{teacher_aligned_strength}-strength evidence for {_option_clause(pair_payload)}."
        )

    if displayed_prediction != feature_prediction:
        return (
            f"Taken together, relative to {neighbor_label_reference}, these feature comparisons are mixed. "
            f"This neighbor should be treated as "
            f"{teacher_aligned_strength}-strength evidence for {_option_clause(pair_payload)}."
        )

    return (
        f"Taken together, relative to {neighbor_label_reference}, the pairwise feature evidence {feature_adverb} "
        f"supports {_option_clause(pair_payload)}. This neighbor provides {teacher_aligned_strength}-strength "
        f"evidence for {_option_clause(pair_payload)}."
    )


def _join_with_and(items: list[str]) -> str:
    filtered = [str(item).strip() for item in items if str(item).strip()]
    if not filtered:
        return ""
    if len(filtered) == 1:
        return filtered[0]
    if len(filtered) == 2:
        return f"{filtered[0]} and {filtered[1]}"
    return f"{', '.join(filtered[:-1])}, and {filtered[-1]}"


def _dominant_support_payload(
    support_weight_by_label: dict[int, float],
    label_semantics: dict[int, dict[str, str]],
) -> tuple[str, dict[str, object] | None]:
    nonzero_labels = [label for label, weight in support_weight_by_label.items() if weight > 0.0]
    if not nonzero_labels:
        return "none", None
    if len(nonzero_labels) == 1:
        label = nonzero_labels[0]
        return "single", _label_payload(label, label_semantics)

    label0_weight = float(support_weight_by_label.get(0, 0.0))
    label1_weight = float(support_weight_by_label.get(1, 0.0))
    total = label0_weight + label1_weight
    if total <= 0.0:
        return "none", None

    dominant_label = 1 if label1_weight >= label0_weight else 0
    dominant_ratio = max(label0_weight, label1_weight) / total
    if dominant_ratio < 0.65:
        return "mixed", None
    return "mostly", _label_payload(dominant_label, label_semantics)


def _aggregate_neighbor_group_terms(
    *,
    group_name: str,
    neighbor_evidence_list: list[dict[str, object]],
    label_semantics: dict[int, dict[str, str]],
) -> dict[str, object]:
    feature_buckets: dict[str, dict[str, object]] = {}

    for neighbor_rank, neighbor_evidence in enumerate(neighbor_evidence_list, start=1):
        neighbor_similarity = float(neighbor_evidence["neighbor_similarity"])
        for term in neighbor_evidence.get("top_pair_terms", []):
            feature_name = str(term["feature_name"])
            bucket = feature_buckets.setdefault(
                feature_name,
                {
                    "feature_name": feature_name,
                    "display_name": str(term["display_name"]),
                    "description": str(term.get("description", "")),
                    "source_family": str(term.get("source_family", "")),
                    "raw_name": str(term.get("raw_name", "")),
                    "occurrence_count": 0,
                    "neighbor_ranks": [],
                    "neighbor_ids": [],
                    "neighbor_similarities": [],
                    "support_weight_by_label": {0: 0.0, 1: 0.0},
                    "total_abs_contribution": 0.0,
                    "total_weighted_evidence": 0.0,
                    "term_instances": [],
                },
            )
            evidence_weight = float(term["contribution_abs"]) * max(neighbor_similarity, 0.0)
            support_label = int(term["supports_label"])
            bucket["occurrence_count"] += 1
            bucket["neighbor_ranks"].append(int(neighbor_rank))
            bucket["neighbor_ids"].append(str(neighbor_evidence["neighbor_id"]))
            bucket["neighbor_similarities"].append(neighbor_similarity)
            bucket["support_weight_by_label"][support_label] += evidence_weight
            bucket["total_abs_contribution"] += float(term["contribution_abs"])
            bucket["total_weighted_evidence"] += evidence_weight
            bucket["term_instances"].append(
                {
                    "neighbor_rank": int(neighbor_rank),
                    "neighbor_id": str(neighbor_evidence["neighbor_id"]),
                    "neighbor_similarity": neighbor_similarity,
                    "pair_score": float(neighbor_evidence["pair_score"]),
                    "pair_prediction": int(neighbor_evidence["pair_prediction"]),
                    "pair_prediction_semantics": dict(neighbor_evidence["pair_prediction_semantics"]),
                    "contribution": float(term["contribution"]),
                    "contribution_abs": float(term["contribution_abs"]),
                    "contribution_rank": int(term["contribution_rank"]),
                    "supports_label": support_label,
                    "supports_option": str(term["supports_option"]),
                    "supports_text": str(term["supports_text"]),
                    "text_hint": str(term["text_hint"]),
                }
            )

    shared_evidence: list[dict[str, object]] = []
    single_neighbor_evidence: list[dict[str, object]] = []
    for bucket in feature_buckets.values():
        support_mode, dominant_payload = _dominant_support_payload(
            bucket["support_weight_by_label"],
            label_semantics,
        )
        normalized_bucket = {
            "feature_name": bucket["feature_name"],
            "display_name": bucket["display_name"],
            "description": bucket["description"],
            "source_family": bucket["source_family"],
            "raw_name": bucket["raw_name"],
            "occurrence_count": int(bucket["occurrence_count"]),
            "neighbor_ranks": [int(rank) for rank in bucket["neighbor_ranks"]],
            "neighbor_ids": list(bucket["neighbor_ids"]),
            "neighbor_similarities": [float(value) for value in bucket["neighbor_similarities"]],
            "support_weight_by_label": {
                "0": float(bucket["support_weight_by_label"][0]),
                "1": float(bucket["support_weight_by_label"][1]),
            },
            "support_mode": support_mode,
            "dominant_support": dominant_payload,
            "total_abs_contribution": float(bucket["total_abs_contribution"]),
            "total_weighted_evidence": float(bucket["total_weighted_evidence"]),
            "term_instances": list(bucket["term_instances"]),
        }
        if int(bucket["occurrence_count"]) >= 2:
            shared_evidence.append(normalized_bucket)
        else:
            single_instance = dict(bucket["term_instances"][0])
            single_neighbor_evidence.append(
                {
                    **normalized_bucket,
                    "neighbor_rank": int(single_instance["neighbor_rank"]),
                    "neighbor_id": str(single_instance["neighbor_id"]),
                    "neighbor_similarity": float(single_instance["neighbor_similarity"]),
                    "pair_score": float(single_instance["pair_score"]),
                    "pair_prediction": int(single_instance["pair_prediction"]),
                    "pair_prediction_semantics": dict(single_instance["pair_prediction_semantics"]),
                    "contribution": float(single_instance["contribution"]),
                    "contribution_abs": float(single_instance["contribution_abs"]),
                    "contribution_rank": int(single_instance["contribution_rank"]),
                    "supports_label": int(single_instance["supports_label"]),
                    "supports_option": str(single_instance["supports_option"]),
                    "supports_text": str(single_instance["supports_text"]),
                    "text_hint": str(single_instance["text_hint"]),
                }
            )

    shared_evidence.sort(
        key=lambda item: (
            -int(item["occurrence_count"]),
            -float(item["total_weighted_evidence"]),
            str(item["display_name"]),
        )
    )
    single_neighbor_evidence.sort(
        key=lambda item: (
            -float(item["neighbor_similarity"]),
            -float(item["contribution_abs"]),
            int(item["neighbor_rank"]),
            str(item["display_name"]),
        )
    )

    return {
        "group_name": group_name,
        "num_neighbors": int(len(neighbor_evidence_list)),
        "num_shared_features": int(len(shared_evidence)),
        "num_single_neighbor_features": int(len(single_neighbor_evidence)),
        "shared_evidence": shared_evidence,
        "single_neighbor_evidence": single_neighbor_evidence,
    }


def _shared_evidence_clause(
    *,
    shared_payload: dict[str, object],
    num_neighbors: int,
) -> str:
    display_name = str(shared_payload["display_name"])
    occurrence_count = int(shared_payload["occurrence_count"])
    support_mode = str(shared_payload["support_mode"])
    dominant_support = shared_payload.get("dominant_support")

    if support_mode == "mixed" or dominant_support is None:
        return (
            f"{display_name}, which recurs in {occurrence_count} of {num_neighbors} neighbor comparisons, "
            f"but with mixed direction"
        )

    return (
        f"{display_name}, which recurs in {occurrence_count} of {num_neighbors} neighbor comparisons and "
        f"{'consistently' if support_mode == 'single' else 'mostly'} pushes toward option "
        f"({dominant_support['option']}): {dominant_support['text']}"
    )


def _single_neighbor_clause(single_payload: dict[str, object]) -> str:
    text_hint = str(single_payload["text_hint"]).rstrip()
    if text_hint.endswith("."):
        text_hint = text_hint[:-1]
    if text_hint:
        text_hint = text_hint[0].lower() + text_hint[1:]
    return (
        f"With neighbor {int(single_payload['neighbor_rank'])} "
        f"(similarity {_format_number(float(single_payload['neighbor_similarity']))}), the comparison shows that "
        f"{text_hint}."
    )


def _build_group_summary_middle_draft(
    *,
    group_summary: dict[str, object],
    group_label: str,
) -> str:
    num_neighbors = int(group_summary["num_neighbors"])
    shared_evidence = list(group_summary.get("shared_evidence", []))
    single_neighbor_evidence = list(group_summary.get("single_neighbor_evidence", []))

    if num_neighbors == 0:
        return f"No {group_label} were available for this sample."

    sentences: list[str] = []
    if shared_evidence:
        shared_clauses = [
            _shared_evidence_clause(shared_payload=payload, num_neighbors=num_neighbors)
            for payload in shared_evidence
        ]
        sentences.append(
            f"Across the {group_label}, shared local signals include {_join_with_and(shared_clauses)}."
        )
    else:
        sentences.append(f"Across the {group_label}, no feature repeated across multiple neighbor comparisons.")

    if single_neighbor_evidence:
        sentences.append(
            f"The remaining one-off signals from the {group_label} are all kept explicitly for downstream rewriting."
        )
        sentences.extend(_single_neighbor_clause(payload) for payload in single_neighbor_evidence)

    return " ".join(sentences)


def _build_local_summary_middle_draft(
    *,
    pos_evidence: list[dict[str, object]],
    neg_evidence: list[dict[str, object]],
    local_score: float,
    s_pos: float | None,
    s_neg: float | None,
    local_prediction: int,
    label_semantics: dict[int, dict[str, str]],
) -> dict[str, object]:
    pos_group_summary = _aggregate_neighbor_group_terms(
        group_name="positive_neighbors",
        neighbor_evidence_list=pos_evidence,
        label_semantics=label_semantics,
    )
    neg_group_summary = _aggregate_neighbor_group_terms(
        group_name="negative_neighbors",
        neighbor_evidence_list=neg_evidence,
        label_semantics=label_semantics,
    )

    pos_draft = _build_group_summary_middle_draft(
        group_summary=pos_group_summary,
        group_label=_semantic_label_reference(1, label_semantics, plural=True),
    )
    neg_draft = _build_group_summary_middle_draft(
        group_summary=neg_group_summary,
        group_label=_semantic_label_reference(0, label_semantics, plural=True),
    )

    predicted_payload = _label_payload(local_prediction, label_semantics)
    local_prediction_probability = _pair_prediction_probability(local_score, local_prediction)
    score_clauses = [f"local prediction probability {_format_number(local_prediction_probability)}"]
    if s_pos is not None:
        score_clauses.append(
            f"aggregate over {_semantic_label_reference(1, label_semantics, plural=True)} {_format_number(s_pos)}"
        )
    if s_neg is not None:
        score_clauses.append(
            f"aggregate over {_semantic_label_reference(0, label_semantics, plural=True)} {_format_number(s_neg)}"
        )

    conclusion_clause = (
        f"Taken together, these local analog comparisons support option ({predicted_payload['option']}): "
        f"{predicted_payload['text']} with {_join_with_and(score_clauses)}."
    )

    return {
        "positive_neighbors": pos_group_summary,
        "negative_neighbors": neg_group_summary,
        "middle_draft": f"{pos_draft} {neg_draft} {conclusion_clause}",
    }


def _extract_neighbor_group(
    *,
    model_bundle: dict[str, object],
    split: str,
    sample_index: int,
    query_smiles: str,
    query_label: int,
    query_raw_row,
    query_raw_values: np.ndarray,
    train_raw_df,
    train_raw_values: np.ndarray,
    train_index_by_smiles: dict[str, int],
    neighbors: list[NeighborRecord],
    feature_semantics_map: dict[str, dict[str, str]],
    label_semantics: dict[int, dict[str, str]],
    top_term_k: int,
    term_selection_mode: str,
    random_top_term_min: int,
    random_top_term_max: int,
    random_seed: int,
) -> tuple[list[dict[str, object]], list[float], list[float]]:
    if not neighbors:
        return [], [], []

    valid_neighbors = [neighbor for neighbor in neighbors if neighbor.smiles in train_index_by_smiles]
    if not valid_neighbors:
        return [], [], []

    neighbor_indices = np.asarray([train_index_by_smiles[neighbor.smiles] for neighbor in valid_neighbors], dtype=int)
    query_matrix = np.repeat(query_raw_values[np.newaxis, :], repeats=len(valid_neighbors), axis=0)
    neighbor_matrix = train_raw_values[neighbor_indices]
    pair_matrix = build_pair_matrix(query_values=query_matrix, neighbor_values=neighbor_matrix)

    model = model_bundle["model"]
    pair_scores = model.predict_proba(pair_matrix)[:, 1]
    pair_term_matrix = np.asarray(model.eval_terms(pair_matrix), dtype=float)
    raw_feature_columns = _resolve_raw_feature_columns(model_bundle)

    evidence_rows: list[dict[str, object]] = []
    for row_index, neighbor in enumerate(valid_neighbors):
        neighbor_raw_row = train_raw_df.iloc[neighbor_indices[row_index]]
        term_selection_rng = None
        if term_selection_mode != "ranked_top_k":
            term_selection_rng = _stable_rng(
                random_seed=random_seed,
                parts=[
                    model_bundle.get("task", ""),
                    split,
                    sample_index,
                    query_smiles,
                    neighbor.smiles,
                    neighbor.label,
                    row_index,
                    model_bundle.get("model_type", ""),
                ],
            )
        evidence_rows.append(
            _build_neighbor_evidence(
                query_smiles=query_smiles,
                query_label=query_label,
                neighbor=neighbor,
                pair_score=float(pair_scores[row_index]),
                query_raw_row=query_raw_row,
                neighbor_raw_row=neighbor_raw_row,
                term_contributions=pair_term_matrix[row_index],
                raw_feature_columns=raw_feature_columns,
                feature_semantics_map=feature_semantics_map,
                label_semantics=label_semantics,
                top_term_k=top_term_k,
                term_selection_mode=term_selection_mode,
                random_top_term_min=random_top_term_min,
                random_top_term_max=random_top_term_max,
                term_selection_rng=term_selection_rng,
            )
        )

    return (
        evidence_rows,
        [float(score) for score in pair_scores.tolist()],
        [float(neighbor.similarity) for neighbor in valid_neighbors],
    )


def build_default_local_evidence_output_dir(
    *,
    pos_bundle_path: str | Path,
    split: str,
    output_root: str | Path = OUTPUTS_ROOT / "reasoning_evidence" / "local",
) -> Path:
    pos_bundle_path = Path(pos_bundle_path)
    feature_set_name = pos_bundle_path.parent.name
    task = pos_bundle_path.parent.parent.name
    experiment_name = pos_bundle_path.parent.parent.parent.name
    return Path(output_root) / experiment_name / task / feature_set_name / split


def extract_local_evidence_for_split(
    *,
    pos_bundle_path: str | Path,
    neg_bundle_path: str | Path,
    split: str,
    dataset_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT,
    cache_root: str | Path = DEFAULT_SIMILARITY_CACHE_ROOT,
    top_k_pos: int = 3,
    top_k_neg: int = 3,
    top_term_k: int = DEFAULT_TOP_TERM_K_PER_NEIGHBOR,
    term_selection_mode: str = "ranked_top_k",
    random_top_term_min: int = DEFAULT_RANDOM_TOP_TERM_MIN,
    random_top_term_max: int = DEFAULT_RANDOM_TOP_TERM_MAX,
    random_seed: int = 0,
    strict_cross_scaffold_pairs: bool = True,
    sample_indices: list[int] | None = None,
    max_samples: int | None = None,
    prompt_root: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, object]:
    _validate_term_selection_config(
        top_term_k=top_term_k,
        term_selection_mode=term_selection_mode,
        random_top_term_min=random_top_term_min,
        random_top_term_max=random_top_term_max,
    )
    pos_bundle_path = Path(pos_bundle_path)
    neg_bundle_path = Path(neg_bundle_path)
    pos_bundle = load_pickle(pos_bundle_path)
    neg_bundle = load_pickle(neg_bundle_path)

    task = str(pos_bundle["task"])
    if str(neg_bundle["task"]) != task:
        raise ValueError("Positive and negative pair bundles must belong to the same task")

    feature_bundle = build_feature_source_bundle(pos_bundle["feature_config_paths"])
    retriever = CachedSimilarityRetriever(cache_root=cache_root, data_root=dataset_root)
    label_semantics = _resolve_label_semantics(task, prompt_root=prompt_root)

    task_split = load_tdc_split(task, split, data_root=dataset_root)
    train_split = load_tdc_split(task, "train", data_root=dataset_root)
    query_raw_df = coerce_numeric_feature_frame(feature_bundle["feature_source"].load(task_split.smiles)).reset_index(drop=True)
    train_raw_df = coerce_numeric_feature_frame(feature_bundle["feature_source"].load(train_split.smiles)).reset_index(drop=True)
    query_raw_values = query_raw_df.to_numpy(dtype=float)
    train_raw_values = train_raw_df.to_numpy(dtype=float)
    train_index_by_smiles = {smiles: index for index, smiles in enumerate(train_split.smiles)}
    feature_semantics_map = build_feature_semantics_map(_resolve_raw_feature_columns(pos_bundle))

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

    records: list[dict[str, object]] = []
    for sample_index in target_indices:
        query_smiles = task_split.smiles[sample_index]
        query_label = int(task_split.labels[sample_index])
        query_scaffold = task_split.scaffolds[sample_index]
        query_raw_row = query_raw_df.iloc[sample_index]

        pos_neighbors = retriever.get_neighbors(
            task=task,
            query_smiles=query_smiles,
            split=split,
            desired_label=1,
            top_k=top_k_pos,
            exclude_same_scaffold=strict_cross_scaffold_pairs,
            query_scaffold=query_scaffold,
        )
        neg_neighbors = retriever.get_neighbors(
            task=task,
            query_smiles=query_smiles,
            split=split,
            desired_label=0,
            top_k=top_k_neg,
            exclude_same_scaffold=strict_cross_scaffold_pairs,
            query_scaffold=query_scaffold,
        )

        pos_evidence, pos_scores, pos_similarities = _extract_neighbor_group(
            model_bundle=pos_bundle,
            split=split,
            sample_index=sample_index,
            query_smiles=query_smiles,
            query_label=query_label,
            query_raw_row=query_raw_row,
            query_raw_values=query_raw_values[sample_index],
            train_raw_df=train_raw_df,
            train_raw_values=train_raw_values,
            train_index_by_smiles=train_index_by_smiles,
            neighbors=pos_neighbors,
            feature_semantics_map=feature_semantics_map,
            label_semantics=label_semantics,
            top_term_k=top_term_k,
            term_selection_mode=term_selection_mode,
            random_top_term_min=random_top_term_min,
            random_top_term_max=random_top_term_max,
            random_seed=random_seed,
        )
        neg_evidence, neg_scores, neg_similarities = _extract_neighbor_group(
            model_bundle=neg_bundle,
            split=split,
            sample_index=sample_index,
            query_smiles=query_smiles,
            query_label=query_label,
            query_raw_row=query_raw_row,
            query_raw_values=query_raw_values[sample_index],
            train_raw_df=train_raw_df,
            train_raw_values=train_raw_values,
            train_index_by_smiles=train_index_by_smiles,
            neighbors=neg_neighbors,
            feature_semantics_map=feature_semantics_map,
            label_semantics=label_semantics,
            top_term_k=top_term_k,
            term_selection_mode=term_selection_mode,
            random_top_term_min=random_top_term_min,
            random_top_term_max=random_top_term_max,
            random_seed=random_seed,
        )
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
        local_summary_middle_draft = _build_local_summary_middle_draft(
            pos_evidence=pos_evidence,
            neg_evidence=neg_evidence,
            local_score=local_score,
            s_pos=s_pos,
            s_neg=s_neg,
            local_prediction=local_prediction,
            label_semantics=label_semantics,
        )

        records.append(
            {
                "schema_version": REASONING_SCHEMA_VERSION,
                "evidence_stage": LOCAL_EVIDENCE_STAGE,
                "sample_id": f"{split}_sample_{sample_index}",
                "sample_index": int(sample_index),
                "task": task,
                "split": split,
                "smiles": query_smiles,
                "gt_label": query_label,
                "gt_label_semantics": _label_payload(query_label, label_semantics),
                "local_prediction": int(local_prediction),
                "local_prediction_semantics": _label_payload(local_prediction, label_semantics),
                "local_prediction_correct": int(local_prediction) == query_label,
                "local_score": local_score,
                "s_pos": s_pos,
                "s_neg": s_neg,
                "local_term_selection": {
                    "mode": str(term_selection_mode),
                    "top_term_k": int(top_term_k),
                    "random_top_term_min": int(random_top_term_min),
                    "random_top_term_max": int(random_top_term_max),
                    "random_seed": int(random_seed),
                },
                "keep_for_reasoning": True,
                "drop_reason": None,
                "local_per_neighbor_decision_evidence": {
                    "positive_neighbors": pos_evidence,
                    "negative_neighbors": neg_evidence,
                    "num_positive_neighbors": len(pos_evidence),
                    "num_negative_neighbors": len(neg_evidence),
                },
                "local_per_neighbor_middle_draft": {
                    "positive_neighbors": [
                        _build_neighbor_middle_draft(
                            neighbor_evidence=neighbor_payload,
                            label_semantics=label_semantics,
                        )
                        for neighbor_payload in pos_evidence
                    ],
                    "negative_neighbors": [
                        _build_neighbor_middle_draft(
                            neighbor_evidence=neighbor_payload,
                            label_semantics=label_semantics,
                        )
                        for neighbor_payload in neg_evidence
                    ],
                },
                "local_summary_middle_draft": local_summary_middle_draft,
            }
        )

    artifact_paths: dict[str, object] = {}
    if output_dir is not None:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        for record in records:
            sample_path = output_path / f"sample_{int(record['sample_index']):05d}.json"
            save_json(sample_path, record)
        artifact_paths["output_dir"] = serialize_project_path(output_path)

    return {
        "schema_version": REASONING_SCHEMA_VERSION,
        "evidence_stage": LOCAL_EVIDENCE_STAGE,
        "task": task,
        "split": split,
        "pos_bundle_path": serialize_project_path(pos_bundle_path),
        "neg_bundle_path": serialize_project_path(neg_bundle_path),
        "dataset_root": serialize_project_path(Path(dataset_root)),
        "cache_root": serialize_project_path(Path(cache_root)),
        "feature_set_name": str(pos_bundle["feature_set_name"]),
        "local_term_selection": {
            "mode": str(term_selection_mode),
            "top_term_k": int(top_term_k),
            "random_top_term_min": int(random_top_term_min),
            "random_top_term_max": int(random_top_term_max),
            "random_seed": int(random_seed),
        },
        "num_records": int(len(records)),
        "sample_indices": [int(record["sample_index"]) for record in records],
        "records": records,
        "artifacts": artifact_paths,
    }
