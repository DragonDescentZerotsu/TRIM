from __future__ import annotations

import math

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    f1_score,
    log_loss,
    roc_auc_score,
)


def safe_macro_f1(y_true, y_pred) -> float:
    if len(set(y_true)) <= 1:
        return 0.0
    return float(f1_score(y_true, y_pred, average="macro"))


def safe_roc_auc(y_true, y_score) -> float:
    if len(set(y_true)) <= 1:
        return math.nan
    return float(roc_auc_score(y_true, y_score))


def safe_balanced_accuracy(y_true, y_pred) -> float:
    if len(set(y_true)) <= 1:
        return math.nan
    return float(balanced_accuracy_score(y_true, y_pred))


def safe_brier_score(y_true, y_score) -> float:
    if len(set(y_true)) <= 1:
        return math.nan
    return float(brier_score_loss(y_true, y_score))


def safe_log_loss(y_true, y_score) -> float:
    clipped = np.clip(np.asarray(y_score, dtype=float), 1e-7, 1 - 1e-7)
    return float(log_loss(y_true, clipped, labels=[0, 1]))


def compute_binary_classification_metrics(y_true, y_pred, y_score) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": safe_macro_f1(y_true, y_pred),
        "roc_auc": safe_roc_auc(y_true, y_score),
        "balanced_accuracy": safe_balanced_accuracy(y_true, y_pred),
        "brier_score": safe_brier_score(y_true, y_score),
        "log_loss": safe_log_loss(y_true, y_score),
    }

