from __future__ import annotations

import pandas as pd

from trim.evaluation.metrics import compute_binary_classification_metrics


def bucket_neighbor_support(
    frame: pd.DataFrame,
    *,
    similarity_column: str = "max_pos_similarity",
) -> pd.DataFrame:
    bucketed = frame.copy()
    bucketed["support_bucket"] = pd.cut(
        bucketed[similarity_column],
        bins=[-float("inf"), 0.2, 0.4, float("inf")],
        labels=["low", "medium", "high"],
    )
    return bucketed


def summarize_bucket_metrics(
    frame: pd.DataFrame,
    *,
    score_column: str,
    label_column: str = "label",
    bucket_column: str = "support_bucket",
) -> dict[str, dict[str, float]]:
    payload: dict[str, dict[str, float]] = {}
    for bucket, bucket_frame in frame.groupby(bucket_column, dropna=False):
        if len(bucket_frame) == 0:
            continue
        predictions = [1 if score >= 0.5 else 0 for score in bucket_frame[score_column].tolist()]
        payload[str(bucket)] = compute_binary_classification_metrics(
            bucket_frame[label_column].tolist(),
            predictions,
            bucket_frame[score_column].tolist(),
        )
    return payload

