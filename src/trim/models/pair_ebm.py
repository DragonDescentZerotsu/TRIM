from __future__ import annotations

from interpret.glassbox import ExplainableBoostingClassifier

from trim.features.pair_features import build_pair_interaction_pairs


def build_pair_ebm_params(
    *,
    pair_columns: list[str],
    random_state: int = 42,
    n_jobs: int = 1,
    max_bins: int = 256,
) -> dict[str, object]:
    if len(pair_columns) % 2 != 0:
        raise ValueError("Pair columns must contain base/delta pairs")
    raw_feature_count = len(pair_columns) // 2
    pair_interactions = build_pair_interaction_pairs([str(index) for index in range(raw_feature_count)])
    return {
        "interactions": pair_interactions,
        "exclude": list(range(len(pair_columns))),
        "random_state": random_state,
        "n_jobs": n_jobs,
        "max_bins": max_bins,
    }


def build_pair_ebm(**params) -> ExplainableBoostingClassifier:
    return ExplainableBoostingClassifier(**params)
