from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from trim.data.datasets import load_tdc_split
from trim.evaluation.metrics import compute_binary_classification_metrics
from trim.features.pair_features import build_pair_matrix, coerce_numeric_feature_frame
from trim.models.aggregation import aggregate_local_scores
from trim.models.fusion import fuse_scores, select_best_lambda
from trim.models.retrieval import CachedSimilarityRetriever
from trim.utils.io import load_pickle, save_json

try:
    from tqdm.auto import tqdm
except ImportError:
    def tqdm(iterable=None, **kwargs):
        return iterable


def evaluate_local_system(
    *,
    task: str,
    split: str,
    feature_source,
    retriever: CachedSimilarityRetriever,
    pos_bundle_path: str | Path,
    neg_bundle_path: str | Path,
    global_bundle_path: str | Path | None = None,
    top_k_pos: int = 3,
    top_k_neg: int = 3,
    strict_cross_scaffold_pairs: bool = True,
    lambda_value: float | None = None,
) -> tuple[pd.DataFrame, dict[str, object]]:
    pos_bundle = load_pickle(pos_bundle_path)
    neg_bundle = load_pickle(neg_bundle_path)
    global_bundle = load_pickle(global_bundle_path) if global_bundle_path is not None else None

    task_split = load_tdc_split(task, split, data_root=retriever.data_root)
    train_split = load_tdc_split(task, "train", data_root=retriever.data_root)
    query_feature_df = coerce_numeric_feature_frame(feature_source.load(task_split.smiles)).reset_index(drop=True)
    train_feature_df = coerce_numeric_feature_frame(feature_source.load(train_split.smiles)).reset_index(drop=True)
    train_index_by_smiles = {smiles: index for index, smiles in enumerate(train_split.smiles)}
    rows: list[dict[str, object]] = []
    pos_query_indices: list[int] = []
    pos_neighbor_indices: list[int] = []
    pos_owner_indices: list[int] = []
    pos_similarities_by_query: list[list[float]] = [[] for _ in task_split.smiles]
    neg_query_indices: list[int] = []
    neg_neighbor_indices: list[int] = []
    neg_owner_indices: list[int] = []
    neg_similarities_by_query: list[list[float]] = [[] for _ in task_split.smiles]

    if global_bundle is not None:
        from trim.features.table_loader import build_feature_source_bundle
        from trim.features.preprocessing import transform_feature_frame

        global_feature_bundle = build_feature_source_bundle(global_bundle["feature_config_paths"])
        global_raw_df = global_feature_bundle["feature_source"].load(task_split.smiles)
        _, global_transformed = transform_feature_frame(global_raw_df, global_bundle["preprocessor"])
        global_scores = global_bundle["model"].predict_proba(global_transformed.to_numpy())[:, 1].tolist()
    else:
        global_scores = [float("nan")] * len(task_split.smiles)

    iterator = zip(task_split.smiles, task_split.labels, task_split.scaffolds)
    for idx, (query_smiles, label, scaffold) in enumerate(
        tqdm(iterator, total=len(task_split.smiles), desc=f"Eval {task} {split}")
    ):
        pos_neighbors = retriever.get_neighbors(
            task=task,
            query_smiles=query_smiles,
            split=split,
            desired_label=1,
            top_k=top_k_pos,
            exclude_same_scaffold=strict_cross_scaffold_pairs,
            query_scaffold=scaffold,
        )
        neg_neighbors = retriever.get_neighbors(
            task=task,
            query_smiles=query_smiles,
            split=split,
            desired_label=0,
            top_k=top_k_neg,
            exclude_same_scaffold=strict_cross_scaffold_pairs,
            query_scaffold=scaffold,
        )

        for neighbor in pos_neighbors:
            neighbor_index = train_index_by_smiles.get(neighbor.smiles)
            if neighbor_index is None:
                continue
            pos_query_indices.append(idx)
            pos_neighbor_indices.append(neighbor_index)
            pos_owner_indices.append(idx)
            pos_similarities_by_query[idx].append(neighbor.similarity)

        for neighbor in neg_neighbors:
            neighbor_index = train_index_by_smiles.get(neighbor.smiles)
            if neighbor_index is None:
                continue
            neg_query_indices.append(idx)
            neg_neighbor_indices.append(neighbor_index)
            neg_owner_indices.append(idx)
            neg_similarities_by_query[idx].append(neighbor.similarity)

    query_values = query_feature_df.to_numpy(dtype=float)
    train_values = train_feature_df.to_numpy(dtype=float)

    pos_scores_by_query: list[list[float]] = [[] for _ in task_split.smiles]
    if pos_query_indices:
        pos_pair_matrix = build_pair_matrix(
            query_values=query_values[np.asarray(pos_query_indices, dtype=int)],
            neighbor_values=train_values[np.asarray(pos_neighbor_indices, dtype=int)],
        )
        pos_scores = pos_bundle["model"].predict_proba(pos_pair_matrix)[:, 1].tolist()
        for owner_index, score in zip(pos_owner_indices, pos_scores):
            pos_scores_by_query[owner_index].append(float(score))

    neg_scores_by_query: list[list[float]] = [[] for _ in task_split.smiles]
    if neg_query_indices:
        neg_pair_matrix = build_pair_matrix(
            query_values=query_values[np.asarray(neg_query_indices, dtype=int)],
            neighbor_values=train_values[np.asarray(neg_neighbor_indices, dtype=int)],
        )
        neg_scores = neg_bundle["model"].predict_proba(neg_pair_matrix)[:, 1].tolist()
        for owner_index, score in zip(neg_owner_indices, neg_scores):
            neg_scores_by_query[owner_index].append(float(score))

    for idx, (query_smiles, label, scaffold) in enumerate(
        zip(task_split.smiles, task_split.labels, task_split.scaffolds)
    ):
        aggregated = aggregate_local_scores(
            pos_scores=pos_scores_by_query[idx],
            pos_similarities=pos_similarities_by_query[idx],
            neg_scores=neg_scores_by_query[idx],
            neg_similarities=neg_similarities_by_query[idx],
        )
        local_score = aggregated["s_local"]
        global_score = global_scores[idx]

        row = {
            "smiles": query_smiles,
            "label": int(label),
            "scaffold": scaffold,
            "global_score": global_score,
            "s_pos": aggregated["s_pos"],
            "s_neg": aggregated["s_neg"],
            "local_score": local_score,
            "max_pos_similarity": max(pos_similarities_by_query[idx], default=float("nan")),
            "max_neg_similarity": max(neg_similarities_by_query[idx], default=float("nan")),
            "num_pos_neighbors": len(pos_similarities_by_query[idx]),
            "num_neg_neighbors": len(neg_similarities_by_query[idx]),
        }
        if global_bundle is not None and lambda_value is not None:
            row["final_score"] = fuse_scores(global_score, local_score, lambda_value)
        rows.append(row)

    predictions_df = pd.DataFrame(rows)

    local_predictions = [1 if score >= 0.5 else 0 for score in predictions_df["local_score"].tolist()]
    payload: dict[str, object] = {
        "local_only": compute_binary_classification_metrics(
            predictions_df["label"].tolist(),
            local_predictions,
            predictions_df["local_score"].tolist(),
        )
    }
    if global_bundle is not None:
        global_predictions = [1 if score >= 0.5 else 0 for score in predictions_df["global_score"].tolist()]
        payload["global_only"] = compute_binary_classification_metrics(
            predictions_df["label"].tolist(),
            global_predictions,
            predictions_df["global_score"].tolist(),
        )
        if lambda_value is None and split == "valid":
            lambda_payload = select_best_lambda(
                y_true=predictions_df["label"].tolist(),
                global_scores=predictions_df["global_score"].tolist(),
                local_scores=predictions_df["local_score"].tolist(),
            )
            lambda_value = float(lambda_payload["lambda"])
        if lambda_value is not None:
            predictions_df["final_score"] = [
                fuse_scores(g, l, lambda_value)
                for g, l in zip(predictions_df["global_score"].tolist(), predictions_df["local_score"].tolist())
            ]
            final_predictions = [1 if score >= 0.5 else 0 for score in predictions_df["final_score"].tolist()]
            payload["hybrid"] = compute_binary_classification_metrics(
                predictions_df["label"].tolist(),
                final_predictions,
                predictions_df["final_score"].tolist(),
            )
            payload["lambda"] = lambda_value

    return predictions_df, payload


def save_local_evaluation(
    *,
    predictions_df: pd.DataFrame,
    metrics_payload: dict[str, object],
    output_dir: str | Path,
    task: str,
    split: str,
) -> dict[str, object]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    predictions_path = output_dir / f"{task}__{split}_molecule_level_predictions.csv"
    metrics_path = output_dir / f"{task}__{split}_molecule_level_metrics.json"
    predictions_df.to_csv(predictions_path, index=False)
    payload = {
        "task": task,
        "split": split,
        "metrics": metrics_payload,
        "artifacts": {
            "predictions_csv": str(predictions_path.resolve()),
            "metrics_json": str(metrics_path.resolve()),
        },
    }
    save_json(metrics_path, payload)
    return payload
