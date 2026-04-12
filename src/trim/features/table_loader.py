from __future__ import annotations

from pathlib import Path

from trim.data.datasets import (
    DEFAULT_LABEL_FIELD,
    DEFAULT_SMILES_FIELD,
    BinaryTaskSplit,
    load_tdc_split,
)
import trim.features.csv_smiles_lookup  # noqa: F401
import trim.features.fg_top_level_csv  # noqa: F401
from trim.features.preprocessing import fit_feature_preprocessor, transform_feature_frame
from trim.features.registry import build_composite_feature_source, load_feature_specs_from_paths


def infer_feature_set_name(loaded_configs: list[dict[str, object]], feature_source_name: str) -> str:
    configured_names = [
        str(config["feature_set_name"]) for config in loaded_configs if config.get("feature_set_name")
    ]
    if configured_names:
        return "+".join(configured_names)
    return feature_source_name.replace("/", "_")


def build_feature_source_bundle(config_paths: list[str | Path]) -> dict[str, object]:
    feature_specs, loaded_configs = load_feature_specs_from_paths(list(config_paths))
    feature_source = build_composite_feature_source(feature_specs)
    feature_set_name = infer_feature_set_name(loaded_configs, feature_source.name)
    return {
        "feature_source": feature_source,
        "feature_set_name": feature_set_name,
        "loaded_configs": loaded_configs,
        "config_paths": [str(Path(path)) for path in config_paths],
    }


def load_smiles_feature_frame(
    *,
    smiles_list: list[str],
    feature_source,
):
    return feature_source.load(smiles_list)


def load_task_feature_matrices(
    *,
    task: str,
    feature_source,
    dataset_root,
    train_split_name: str = "train",
    valid_split_name: str = "valid",
    smiles_key: str = DEFAULT_SMILES_FIELD,
    label_key: str = DEFAULT_LABEL_FIELD,
    scale_features: bool = False,
) -> dict[str, object]:
    train_split: BinaryTaskSplit = load_tdc_split(
        task,
        train_split_name,
        data_root=dataset_root,
        smiles_field=smiles_key,
        label_field=label_key,
    )
    valid_split: BinaryTaskSplit = load_tdc_split(
        task,
        valid_split_name,
        data_root=dataset_root,
        smiles_field=smiles_key,
        label_field=label_key,
    )

    raw_train_df = feature_source.load(train_split.smiles)
    raw_valid_df = feature_source.load(valid_split.smiles)
    preprocessor = fit_feature_preprocessor(raw_train_df, scale_features=scale_features)
    _, x_train_df = transform_feature_frame(raw_train_df, preprocessor)
    _, x_valid_df = transform_feature_frame(raw_valid_df, preprocessor)

    return {
        "x_train": x_train_df.to_numpy(),
        "y_train": train_split.labels,
        "x_valid": x_valid_df.to_numpy(),
        "y_valid": valid_split.labels,
        "train_split": train_split,
        "valid_split": valid_split,
        "surviving_columns": list(preprocessor["surviving_columns"]),
        "preprocessor": preprocessor,
        "raw_train_df": raw_train_df,
        "raw_valid_df": raw_valid_df,
        "transformed_train_df": x_train_df,
        "transformed_valid_df": x_valid_df,
    }
