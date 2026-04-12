from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


def build_pair_interaction_pairs(feature_columns: list[str]) -> list[tuple[int, int]]:
    return [(2 * index, 2 * index + 1) for index in range(len(feature_columns))]


def coerce_numeric_feature_frame(frame: pd.DataFrame) -> pd.DataFrame:
    numeric_frame = frame.copy()
    for column in numeric_frame.columns:
        numeric_frame[column] = pd.to_numeric(numeric_frame[column], errors="coerce")
    return numeric_frame


def build_pair_column_names(feature_columns: list[str]) -> list[str]:
    pair_columns: list[str] = []
    for column in feature_columns:
        pair_columns.append(f"{column}__base")
        pair_columns.append(f"{column}__delta")
    return pair_columns


def build_pair_matrix(
    *,
    query_values: np.ndarray,
    neighbor_values: np.ndarray,
) -> np.ndarray:
    if query_values.shape != neighbor_values.shape:
        raise ValueError(
            f"query_values shape {query_values.shape} must match neighbor_values shape {neighbor_values.shape}"
        )
    if query_values.ndim != 2:
        raise ValueError(f"Expected 2D arrays, got ndim={query_values.ndim}")

    pair_matrix = np.empty((query_values.shape[0], query_values.shape[1] * 2), dtype=float)
    pair_matrix[:, 0::2] = neighbor_values
    pair_matrix[:, 1::2] = query_values - neighbor_values
    return pair_matrix


@dataclass
class PairFeatureBuilder:
    feature_source: object

    def build_from_smiles(self, query_smiles: list[str], neighbor_smiles: list[str]) -> pd.DataFrame:
        if len(query_smiles) != len(neighbor_smiles):
            raise ValueError("query_smiles and neighbor_smiles must have the same length")
        query_df = coerce_numeric_feature_frame(self.feature_source.load(query_smiles)).reset_index(drop=True)
        neighbor_df = coerce_numeric_feature_frame(self.feature_source.load(neighbor_smiles)).reset_index(drop=True)
        return self.build_from_frames(query_df=query_df, neighbor_df=neighbor_df)

    def build_from_frames(self, *, query_df: pd.DataFrame, neighbor_df: pd.DataFrame) -> pd.DataFrame:
        if list(query_df.columns) != list(neighbor_df.columns):
            raise ValueError("Query and neighbor feature frames must have identical columns")
        query_df = coerce_numeric_feature_frame(query_df)
        neighbor_df = coerce_numeric_feature_frame(neighbor_df)
        pair_matrix = build_pair_matrix(
            query_values=query_df.to_numpy(dtype=float),
            neighbor_values=neighbor_df.to_numpy(dtype=float),
        )
        return pd.DataFrame(pair_matrix, columns=build_pair_column_names(query_df.columns.tolist()))
