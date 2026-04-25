from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

from trim.data.datasets import load_tdc_split
from trim.evaluation.metrics import compute_binary_classification_metrics
from trim.features.pair_features import (
    build_pair_column_names,
    build_pair_matrix,
    coerce_numeric_feature_frame,
)
from trim.models.pair_ebm import build_pair_ebm, build_pair_ebm_params
from trim.models.retrieval import CachedSimilarityRetriever
from trim.utils.io import save_json, save_pickle
from trim.utils.paths import serialize_project_path

try:
    from tqdm.auto import tqdm
except ImportError:
    def tqdm(iterable=None, **kwargs):
        return iterable


@dataclass(frozen=True)
class PairTrainingConfig:
    neighbor_label: int
    top_k: int = 3
    strict_cross_scaffold_pairs: bool = True
    random_state: int = 42
    n_jobs: int = 1
    max_bins: int = 256


def build_pair_training_frame(
    *,
    task: str,
    feature_source,
    retriever: CachedSimilarityRetriever,
    split: str,
    neighbor_label: int,
    top_k: int,
    strict_cross_scaffold_pairs: bool,
) -> tuple[pd.DataFrame, list[int], pd.DataFrame]:
    task_split = load_tdc_split(task, split, data_root=retriever.data_root)
    train_split = task_split if split == "train" else load_tdc_split(task, "train", data_root=retriever.data_root)

    query_feature_df = coerce_numeric_feature_frame(feature_source.load(task_split.smiles)).reset_index(drop=True)
    if split == "train":
        train_feature_df = query_feature_df
    else:
        train_feature_df = coerce_numeric_feature_frame(feature_source.load(train_split.smiles)).reset_index(drop=True)

    train_index_by_smiles = {smiles: index for index, smiles in enumerate(train_split.smiles)}
    feature_columns = query_feature_df.columns.tolist()

    query_row_indices: list[int] = []
    neighbor_row_indices: list[int] = []
    pair_labels: list[int] = []
    metadata_rows: list[dict[str, object]] = []

    iterator = zip(task_split.smiles, task_split.labels, task_split.scaffolds)
    for query_index, (query_smiles, query_label, query_scaffold) in enumerate(
        tqdm(
            iterator,
            total=len(task_split.smiles),
            desc=f"Build {task} {split} neighbor_label={neighbor_label}",
        )
    ):
        neighbors = retriever.get_neighbors(
            task=task,
            query_smiles=query_smiles,
            split=split,
            desired_label=neighbor_label,
            top_k=top_k,
            exclude_same_scaffold=strict_cross_scaffold_pairs,
            query_scaffold=query_scaffold,
        )
        if not neighbors:
            continue

        for neighbor in neighbors:
            neighbor_index = train_index_by_smiles.get(neighbor.smiles)
            if neighbor_index is None:
                continue
            query_row_indices.append(query_index)
            neighbor_row_indices.append(neighbor_index)
            pair_labels.append(int(query_label))
            metadata_rows.append(
                {
                    "query_smiles": query_smiles,
                    "query_label": int(query_label),
                    "query_scaffold": query_scaffold,
                    "neighbor_smiles": neighbor.smiles,
                    "neighbor_label": neighbor.label,
                    "neighbor_scaffold": neighbor.scaffold,
                    "similarity": neighbor.similarity,
                }
            )

    if not query_row_indices:
        raise ValueError(f"No pairwise training rows were constructed for task={task} split={split}")

    pair_matrix = build_pair_matrix(
        query_values=query_feature_df.to_numpy(dtype=float)[np.asarray(query_row_indices, dtype=int)],
        neighbor_values=train_feature_df.to_numpy(dtype=float)[np.asarray(neighbor_row_indices, dtype=int)],
    )
    pair_df = pd.DataFrame(pair_matrix, columns=build_pair_column_names(feature_columns))
    return pair_df, pair_labels, pd.DataFrame(metadata_rows)


def train_pair_task(
    *,
    task: str,
    feature_bundle: dict[str, object],
    retriever: CachedSimilarityRetriever,
    config: PairTrainingConfig,
    output_dir: str | Path,
) -> dict[str, object]:
    train_build_start = perf_counter()
    train_df, train_labels, train_meta = build_pair_training_frame(
        task=task,
        feature_source=feature_bundle["feature_source"],
        retriever=retriever,
        split="train",
        neighbor_label=config.neighbor_label,
        top_k=config.top_k,
        strict_cross_scaffold_pairs=config.strict_cross_scaffold_pairs,
    )
    train_build_seconds = perf_counter() - train_build_start

    valid_build_start = perf_counter()
    valid_df, valid_labels, valid_meta = build_pair_training_frame(
        task=task,
        feature_source=feature_bundle["feature_source"],
        retriever=retriever,
        split="valid",
        neighbor_label=config.neighbor_label,
        top_k=config.top_k,
        strict_cross_scaffold_pairs=config.strict_cross_scaffold_pairs,
    )
    valid_build_seconds = perf_counter() - valid_build_start

    raw_feature_columns = [column[:-7] for column in train_df.columns if column.endswith("__base")]
    pair_params = build_pair_ebm_params(
        pair_columns=train_df.columns.tolist(),
        random_state=config.random_state,
        n_jobs=config.n_jobs,
        max_bins=config.max_bins,
    )
    pair_name = "pos" if config.neighbor_label == 1 else "neg"
    print(
        f"[pair-train] task={task} model={pair_name} "
        f"rows(train={len(train_df)}, valid={len(valid_df)}) "
        f"raw_features={len(raw_feature_columns)} pair_columns={len(train_df.columns)} "
        f"build_seconds(train={train_build_seconds:.2f}, valid={valid_build_seconds:.2f}) "
        f"n_jobs={config.n_jobs}"
    )

    fit_start = perf_counter()
    model = build_pair_ebm(**pair_params)
    model.fit(train_df.to_numpy(), train_labels)
    fit_seconds = perf_counter() - fit_start
    print(f"[pair-train] task={task} model={pair_name} fit_seconds={fit_seconds:.2f}")

    train_scores = model.predict_proba(train_df.to_numpy())[:, 1]
    valid_scores = model.predict_proba(valid_df.to_numpy())[:, 1]
    train_predictions = model.predict(train_df.to_numpy())
    valid_predictions = model.predict(valid_df.to_numpy())

    train_metrics = compute_binary_classification_metrics(train_labels, train_predictions, train_scores)
    valid_metrics = compute_binary_classification_metrics(valid_labels, valid_predictions, valid_scores)

    output_dir = Path(output_dir) / task / str(feature_bundle["feature_set_name"])
    output_dir.mkdir(parents=True, exist_ok=True)

    train_pred_df = train_meta.copy()
    train_pred_df["prediction"] = train_predictions
    train_pred_df["score"] = train_scores
    valid_pred_df = valid_meta.copy()
    valid_pred_df["prediction"] = valid_predictions
    valid_pred_df["score"] = valid_scores

    train_pred_path = output_dir / f"{pair_name}_train_pair_predictions.csv"
    valid_pred_path = output_dir / f"{pair_name}_valid_pair_predictions.csv"
    train_pred_df.to_csv(train_pred_path, index=False)
    valid_pred_df.to_csv(valid_pred_path, index=False)

    bundle = {
        "task": task,
        "model_type": f"pair_ebm_{pair_name}",
        "neighbor_label": config.neighbor_label,
        "feature_set_name": feature_bundle["feature_set_name"],
        "feature_config_paths": feature_bundle["config_paths"],
        "pair_columns": train_df.columns.tolist(),
        "raw_feature_columns": raw_feature_columns,
        "pair_params": pair_params,
        "model": model,
        "metrics": {"train": train_metrics, "valid": valid_metrics},
        "training_config": {
            "top_k": config.top_k,
            "strict_cross_scaffold_pairs": config.strict_cross_scaffold_pairs,
            "n_jobs": config.n_jobs,
        },
    }
    bundle_path = output_dir / f"{pair_name}_model_bundle.pkl"
    save_pickle(bundle_path, bundle)

    summary = {
        "task": task,
        "model_type": f"pair_ebm_{pair_name}",
        "neighbor_label": config.neighbor_label,
        "feature_set_name": feature_bundle["feature_set_name"],
        "feature_config_paths": feature_bundle["config_paths"],
        "metrics": {"train": train_metrics, "valid": valid_metrics},
        "pair_rows": {"train": len(train_df), "valid": len(valid_df)},
        "timing_seconds": {
            "build_train": round(train_build_seconds, 4),
            "build_valid": round(valid_build_seconds, 4),
            "fit": round(fit_seconds, 4),
        },
        "artifacts": {
            "bundle_pkl": serialize_project_path(bundle_path),
            "train_pair_predictions_csv": serialize_project_path(train_pred_path),
            "valid_pair_predictions_csv": serialize_project_path(valid_pred_path),
        },
    }
    save_json(output_dir / f"{pair_name}_train_summary.json", summary)
    return summary
