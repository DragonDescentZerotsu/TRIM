from __future__ import annotations

from interpret.glassbox import ExplainableBoostingClassifier


def build_ebm_params(
    *,
    interactions: int = 0,
    random_state: int = 42,
    n_jobs: int = 1,
) -> dict[str, object]:
    return {
        "interactions": interactions,
        "random_state": random_state,
        "n_jobs": n_jobs,
    }


def build_global_ebm(**ebm_params) -> ExplainableBoostingClassifier:
    return ExplainableBoostingClassifier(**ebm_params)
