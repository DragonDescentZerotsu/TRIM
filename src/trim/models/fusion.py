from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from trim.evaluation.metrics import compute_binary_classification_metrics


def fuse_scores(global_score: float, local_score: float, lambda_value: float) -> float:
    return float((lambda_value * global_score) + ((1.0 - lambda_value) * local_score))


def select_best_lambda(
    *,
    y_true: list[int],
    global_scores: list[float],
    local_scores: list[float],
    lambda_grid: Iterable[float] | None = None,
) -> dict[str, object]:
    if lambda_grid is None:
        lambda_grid = np.linspace(0.0, 1.0, num=21)

    best_payload: dict[str, object] | None = None
    for lambda_value in lambda_grid:
        fused_scores = [fuse_scores(g, l, float(lambda_value)) for g, l in zip(global_scores, local_scores)]
        predictions = [1 if score >= 0.5 else 0 for score in fused_scores]
        metrics = compute_binary_classification_metrics(y_true, predictions, fused_scores)
        payload = {
            "lambda": float(lambda_value),
            "metrics": metrics,
            "scores": fused_scores,
        }
        if best_payload is None:
            best_payload = payload
            continue
        if metrics["macro_f1"] > best_payload["metrics"]["macro_f1"]:
            best_payload = payload
        elif (
            metrics["macro_f1"] == best_payload["metrics"]["macro_f1"]
            and metrics["roc_auc"] > best_payload["metrics"]["roc_auc"]
        ):
            best_payload = payload
    assert best_payload is not None
    return best_payload

