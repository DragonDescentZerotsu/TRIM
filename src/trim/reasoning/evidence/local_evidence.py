from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from trim.data.datasets import load_tdc_split
from trim.features.pair_features import build_pair_matrix, coerce_numeric_feature_frame
from trim.features.table_loader import build_feature_source_bundle
from trim.models.aggregation import aggregate_local_scores
from trim.models.retrieval import CachedSimilarityRetriever, NeighborRecord
from trim.reasoning.evidence.global_evidence import (
    _format_number,
    _infer_value_phrase,
    _label_payload,
    _resolve_label_semantics,
)
from trim.reasoning.evidence.schemas import REASONING_SCHEMA_VERSION
from trim.reasoning.semantics import build_feature_semantics_map
from trim.utils.io import load_pickle, save_json
from trim.utils.paths import (
    DEFAULT_PROCESSED_DATA_ROOT,
    DEFAULT_SIMILARITY_CACHE_ROOT,
    OUTPUTS_ROOT,
)


LOCAL_EVIDENCE_STAGE = "local_evidence_only"


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


def _render_pair_observed_value(value_text: str) -> str:
    stripped = str(value_text).strip()
    if stripped.startswith(("value ", "count ", "present", "absent")):
        return stripped
    return f"value {stripped}"


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
                f"{comparison_text} (query-minus-neighbor delta {_delta_text(delta_value)}). "
                f"This pairwise contribution is {_format_number(contribution, decimals=4)}, which pushes toward "
                f"option ({contribution_label['option']}): {contribution_label['text']}."
            )

    rendered_base_value = _render_pair_observed_value(base_value_text)
    rendered_query_value = _render_pair_observed_value(query_value_text)
    return (
        f"{feature_display_name} has neighbor {rendered_base_value}, query {rendered_query_value}, and "
        f"query-minus-neighbor delta {_delta_text(delta_value)}. This pairwise contribution is "
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
) -> list[dict[str, object]]:
    non_nan_indices = [index for index, value in enumerate(term_contributions) if not math.isnan(float(value))]
    ranked_indices = sorted(non_nan_indices, key=lambda index: abs(float(term_contributions[index])), reverse=True)
    selected_indices = ranked_indices[:top_term_k]

    terms: list[dict[str, object]] = []
    for rank, term_index in enumerate(selected_indices, start=1):
        raw_feature_name = raw_feature_columns[term_index]
        semantics = feature_semantics_map[raw_feature_name]
        base_value = neighbor_raw_row[raw_feature_name]
        query_value = query_raw_row[raw_feature_name]
        delta_value = float(query_value) - float(base_value)
        contribution = float(term_contributions[term_index])
        contribution_label = _label_payload(1 if contribution >= 0.0 else 0, label_semantics)
        base_value_text = _infer_value_phrase(base_value, semantics)
        query_value_text = _infer_value_phrase(query_value, semantics)

        terms.append(
            {
                **semantics,
                "feature_name": raw_feature_name,
                "base_value": base_value,
                "query_value": query_value,
                "delta_value": delta_value,
                "base_value_text": base_value_text,
                "query_value_text": query_value_text,
                "contribution": contribution,
                "contribution_abs": float(abs(contribution)),
                "contribution_rank": rank,
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
        )
    return terms


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
) -> dict[str, object]:
    pair_model_type = _pair_model_type(neighbor.label)
    pair_prediction = 1 if pair_score >= 0.5 else 0
    top_pair_terms = _extract_top_pair_terms(
        raw_feature_columns=raw_feature_columns,
        feature_semantics_map=feature_semantics_map,
        query_raw_row=query_raw_row,
        neighbor_raw_row=neighbor_raw_row,
        term_contributions=term_contributions,
        label_semantics=label_semantics,
        top_term_k=top_term_k,
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
        "pair_prediction": int(pair_prediction),
        "pair_prediction_semantics": _label_payload(pair_prediction, label_semantics),
        "top_pair_terms": top_pair_terms,
    }


def _build_neighbor_middle_draft(
    *,
    neighbor_evidence: dict[str, object],
    label_semantics: dict[int, dict[str, str]],
) -> dict[str, object]:
    transition_words = ["First", "Next", "Then", "After that", "Finally"]
    top_pair_terms = list(neighbor_evidence.get("top_pair_terms", []))
    pair_prediction = int(neighbor_evidence["pair_prediction"])
    pair_score = float(neighbor_evidence["pair_score"])
    predicted_label_payload = _label_payload(pair_prediction, label_semantics)

    if top_pair_terms:
        step_clauses = []
        for step_index, term in enumerate(top_pair_terms):
            transition = (
                transition_words[step_index]
                if step_index < len(transition_words)
                else f"Step {step_index + 1}"
            )
            step_statement = str(term["text_hint"]).rstrip()
            if step_statement.endswith("."):
                step_statement = step_statement[:-1]
            step_clauses.append(f"{transition}, {step_statement}.")
        detail_clause = " ".join(step_clauses)
    else:
        detail_clause = "No ranked pair-term evidence was available for this neighbor comparison."

    conclusion_clause = (
        f"Taken together, this {_neighbor_role(int(neighbor_evidence['neighbor_label'])).replace('_', '-')} comparison "
        f"pushes toward option ({predicted_label_payload['option']}): {predicted_label_payload['text']} with pair score "
        f"{_format_number(pair_score)}."
    )

    return {
        "neighbor_id": neighbor_evidence["neighbor_id"],
        "neighbor_smiles": neighbor_evidence["neighbor_smiles"],
        "neighbor_role": neighbor_evidence["neighbor_role"],
        "pair_model_type": neighbor_evidence["pair_model_type"],
        "pair_score": pair_score,
        "pair_prediction": pair_prediction,
        "pair_prediction_semantics": predicted_label_payload,
        "middle_draft": f"{detail_clause} {conclusion_clause}",
    }


def _resolve_raw_feature_columns(model_bundle: dict[str, object]) -> list[str]:
    pair_columns = [str(column) for column in model_bundle.get("pair_columns", [])]
    if pair_columns:
        base_columns = [column.removesuffix("__base") for column in pair_columns[0::2]]
        if all(base_columns):
            return base_columns
    return [str(column) for column in model_bundle["raw_feature_columns"]]


def _extract_neighbor_group(
    *,
    model_bundle: dict[str, object],
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
    top_term_k: int = 6,
    strict_cross_scaffold_pairs: bool = True,
    sample_indices: list[int] | None = None,
    max_samples: int | None = None,
    prompt_root: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, object]:
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
        )
        neg_evidence, neg_scores, neg_similarities = _extract_neighbor_group(
            model_bundle=neg_bundle,
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
        )
        aggregated = aggregate_local_scores(
            pos_scores=pos_scores,
            pos_similarities=pos_similarities,
            neg_scores=neg_scores,
            neg_similarities=neg_similarities,
        )
        local_score = float(aggregated["s_local"])
        local_prediction = 1 if local_score >= 0.5 else 0

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
                "s_pos": float(aggregated["s_pos"]) if not math.isnan(float(aggregated["s_pos"])) else None,
                "s_neg": float(aggregated["s_neg"]) if not math.isnan(float(aggregated["s_neg"])) else None,
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
            }
        )

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
        "evidence_stage": LOCAL_EVIDENCE_STAGE,
        "task": task,
        "split": split,
        "pos_bundle_path": str(pos_bundle_path.resolve()),
        "neg_bundle_path": str(neg_bundle_path.resolve()),
        "dataset_root": str(Path(dataset_root).resolve()),
        "cache_root": str(Path(cache_root).resolve()),
        "feature_set_name": str(pos_bundle["feature_set_name"]),
        "num_records": int(len(records)),
        "sample_indices": [int(record["sample_index"]) for record in records],
        "records": records,
        "artifacts": artifact_paths,
    }
