from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np


def similarity_weighted_average(scores: Sequence[float], similarities: Sequence[float]) -> float:
    if not scores:
        return math.nan
    weights = np.asarray(similarities, dtype=float)
    values = np.asarray(scores, dtype=float)
    if np.allclose(weights.sum(), 0.0):
        return float(values.mean())
    return float(np.average(values, weights=weights))


def aggregate_local_scores(
    *,
    pos_scores: Sequence[float],
    pos_similarities: Sequence[float],
    neg_scores: Sequence[float],
    neg_similarities: Sequence[float],
) -> dict[str, float]:
    s_pos = similarity_weighted_average(pos_scores, pos_similarities)
    s_neg = similarity_weighted_average(neg_scores, neg_similarities)
    pooled_scores = list(pos_scores) + list(neg_scores)
    pooled_sims = list(pos_similarities) + list(neg_similarities)
    if pooled_scores:
        s_local = similarity_weighted_average(pooled_scores, pooled_sims)
    else:
        s_local = 0.5
    return {"s_pos": s_pos, "s_neg": s_neg, "s_local": s_local}
