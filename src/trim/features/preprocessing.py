from __future__ import annotations

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


def _coerce_numeric_frame(frame: pd.DataFrame) -> pd.DataFrame:
    numeric_frame = frame.copy()
    for column in numeric_frame.columns:
        numeric_frame[column] = pd.to_numeric(numeric_frame[column], errors="coerce")
    return numeric_frame


def fit_feature_preprocessor(
    train_df: pd.DataFrame,
    *,
    scale_features: bool = False,
    drop_any_nan_columns: bool = False,
) -> dict[str, object]:
    train_df = _coerce_numeric_frame(train_df)
    input_columns = train_df.columns.tolist()
    if drop_any_nan_columns:
        surviving_columns = train_df.columns[~train_df.isna().any(axis=0)].tolist()
    else:
        surviving_columns = train_df.columns[~train_df.isna().all(axis=0)].tolist()
    if not surviving_columns:
        raise ValueError("No usable feature columns remain after dropping NaN columns from training data.")

    train_df = train_df[surviving_columns]
    imputer = SimpleImputer(strategy="median")
    imputer.fit(train_df)

    scaler = None
    if scale_features:
        scaler = StandardScaler()
        scaler.fit(imputer.transform(train_df))

    return {
        "input_columns": input_columns,
        "surviving_columns": surviving_columns,
        "imputer": imputer,
        "scaler": scaler,
        "scale_features": scale_features,
        "drop_any_nan_columns": drop_any_nan_columns,
    }


def transform_feature_frame(
    frame: pd.DataFrame,
    preprocessor: dict[str, object],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    numeric_frame = _coerce_numeric_frame(frame)
    surviving_columns = list(preprocessor["surviving_columns"])
    aligned_frame = numeric_frame.reindex(columns=surviving_columns)
    transformed = preprocessor["imputer"].transform(aligned_frame)

    scaler = preprocessor.get("scaler")
    if scaler is not None:
        transformed = scaler.transform(transformed)

    transformed_df = pd.DataFrame(transformed, columns=surviving_columns, index=frame.index)
    return aligned_frame, transformed_df
