from __future__ import annotations

import math

import pandas as pd

from trim.features.pair_features import PairFeatureBuilder
from trim.models.aggregation import aggregate_local_scores
from trim.models.fusion import fuse_scores, select_best_lambda


class DummyFeatureSource:
    def load(self, smiles_list):
        return pd.DataFrame(
            {
                "a": [float(index + 1) for index, _ in enumerate(smiles_list)],
                "b": [float((index + 1) * 10) for index, _ in enumerate(smiles_list)],
            }
        )


def test_pair_feature_builder_shapes_base_and_delta():
    builder = PairFeatureBuilder(feature_source=DummyFeatureSource())
    frame = builder.build_from_smiles(["q1", "q2"], ["n1", "n2"])
    assert frame.columns.tolist() == ["a__base", "a__delta", "b__base", "b__delta"]
    assert len(frame) == 2


def test_aggregate_local_scores_returns_expected_keys():
    payload = aggregate_local_scores(
        pos_scores=[0.8, 0.6],
        pos_similarities=[0.9, 0.1],
        neg_scores=[0.4],
        neg_similarities=[0.5],
    )
    assert set(payload) == {"s_pos", "s_neg", "s_local"}
    assert not math.isnan(payload["s_local"])


def test_select_best_lambda_runs():
    payload = select_best_lambda(
        y_true=[0, 1, 1, 0],
        global_scores=[0.2, 0.7, 0.8, 0.4],
        local_scores=[0.3, 0.6, 0.9, 0.2],
        lambda_grid=[0.0, 0.5, 1.0],
    )
    assert payload["lambda"] in {0.0, 0.5, 1.0}
    assert "metrics" in payload
    assert 0.0 <= fuse_scores(0.8, 0.4, 0.25) <= 1.0
